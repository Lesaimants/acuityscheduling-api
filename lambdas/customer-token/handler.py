import logging
import os
import sys
import traceback
from http import HTTPStatus

import requests
from requests import HTTPError
from requests.exceptions import Timeout, ConnectionError as ReqConnectionError, RequestException

from http_utils import make_response, internal_server_error
from validation import validation
from validation_model import RequestBody

logger = logging.getLogger()

DEFAULT_TIMEOUT = 8
DEFAULT_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2024-07")
shop_domain = os.getenv("SHOPIFY_STORE_DOMAIN")
storefront_token = os.getenv("SHOPIFY_STOREFRONT_ACCESS_TOKEN")
HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Storefront-Access-Token": storefront_token,
}

MUTATION = (
    "mutation customerAccessTokenCreate($input: CustomerAccessTokenCreateInput!) { "
    "customerAccessTokenCreate(input: $input) { "
    "customerAccessToken { accessToken expiresAt } "
    "userErrors { message } "
    "} "
    "}"
)


@validation
def function_handler(event, __, request_body: RequestBody):
    try:
        # Build endpoint and payload
        endpoint = f"https://{shop_domain}/api/{DEFAULT_API_VERSION}/graphql.json"
        payload = {
            "query": MUTATION,
            "variables": {
                "input": {
                    "email": request_body.email,
                    "password": request_body.password,
                }
            },
        }

        try:
            resp = requests.post(endpoint, json=payload, headers=HEADERS, timeout=DEFAULT_TIMEOUT)
            # We treat non-2xx as upstream errors
            resp.raise_for_status()
            data = resp.json() or {}
            create = ((data.get("data") or {}).get("customerAccessTokenCreate") or {})
            user_errors = create.get("userErrors") or []
            if isinstance(user_errors, list) and len(user_errors) > 0:
                return make_response(HTTPStatus.UNAUTHORIZED, {
                    "success": False,
                    "error": "Credenciales inválidas",
                    "details": [e.get("message") for e in user_errors if isinstance(e, dict) and e.get("message")],
                })
            token_obj = create.get("customerAccessToken") or {}
            access_token = token_obj.get("accessToken")
            expires_at = token_obj.get("expiresAt")
            if access_token and expires_at:
                return make_response(HTTPStatus.OK, {
                    "accessToken": access_token,
                    "expiresAt": expires_at,
                })
            # No token and no explicit userErrors: treat as invalid credentials
            return make_response(HTTPStatus.UNAUTHORIZED, {
                "success": False,
                "error": "Credenciales inválidas",
            })
        except HTTPError as http_err:
            status = http_err.response.status_code if http_err.response is not None else 502
            content = _safe_content(http_err)
            return make_response(HTTPStatus.BAD_GATEWAY, {
                "success": False,
                "error": "Error al consultar Shopify Storefront",
                "upstream": {"status": status, "body": content},
            })
        except (Timeout, ReqConnectionError):
            return make_response(HTTPStatus.BAD_GATEWAY, {
                "success": False,
                "error": "Error de comunicación con Shopify Storefront",
            })
        except RequestException:
            return make_response(HTTPStatus.BAD_GATEWAY, {
                "success": False,
                "error": "Error al consultar Shopify Storefront",
            })

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error("*** xml tb_lineno: {}".format(exc_traceback.tb_lineno))
        logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
        return internal_server_error("Ocurrió un error inesperado. Contacte a soporte")


def _safe_content(http_err: HTTPError):
    try:
        if http_err.response is not None:
            return http_err.response.json()
        return None
    except Exception:
        return http_err.response.text if http_err.response is not None else None
