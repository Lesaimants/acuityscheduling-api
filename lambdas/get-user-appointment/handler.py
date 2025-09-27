import logging
import os
import sys
import traceback
from http import HTTPStatus

import requests
from requests import HTTPError
from requests.exceptions import Timeout, ConnectionError as ReqConnectionError, RequestException

from http_utils import make_response, internal_server_error, bad_request, not_found
from validation import validation
from validation_model import RequestBody
from db_user_links import DBUserLinks

logger = logging.getLogger()

BASE_URL = "https://acuityscheduling.com/api/v1"
DEFAULT_TIMEOUT = 10
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "get-user-appointments-lambda/1.0",
}


user_id = os.environ.get("ACUITY_USER_ID")
api_key = os.environ.get("ACUITY_API_KEY")
db_links = DBUserLinks()


@validation
def function_handler(event, __, request_body: RequestBody):
    try:
        # 1) Extract authorizer context
        auth_ctx = ((event or {}).get("requestContext") or {}).get("authorizer") or {}
        shopify_customer_id = str(auth_ctx.get("shopifyCustomerId")) if auth_ctx.get("shopifyCustomerId") is not None else None
        email = str(auth_ctx.get("email")) if auth_ctx.get("email") is not None else None
        first_name = str(auth_ctx.get("firstName")) if auth_ctx.get("firstName") is not None else ""
        last_name = str(auth_ctx.get("lastName")) if auth_ctx.get("lastName") is not None else ""
        phone = str(auth_ctx.get("phone")) if auth_ctx.get("phone") is not None else ""
        shop_domain = str(auth_ctx.get("shopDomain")) if auth_ctx.get("shopDomain") is not None else ""

        # Requiere al menos teléfono o email para identificar al usuario
        if (not phone or phone.strip() == "") and (not email or str(email).strip() == ""):
            return make_response(HTTPStatus.UNAUTHORIZED, {
                "success": False,
                "error": "No autorizado: faltan datos del usuario (teléfono o email)",
            })

        # 2) Consultar citas por usuario (teléfono prioritario, si no email)
        if phone and phone.strip() != "":
            params = {
                "phone": phone,
                "showall": True,
                "canceled": True
            }
        else:
            params = {
                "email": email,
                "showall": True,
                "canceled": True
            }
        if request_body.calendarId is not None:
            params["calendarID"] = request_body.calendarId
        if request_body.appointmentTypeId is not None:
            params["appointmentTypeID"] = request_body.appointmentTypeId

        try:
            a_resp = requests.get(
                f"{BASE_URL}/appointments",
                params=params,
                auth=(user_id, api_key),
                headers=HEADERS,
                timeout=DEFAULT_TIMEOUT,
            )
            a_resp.raise_for_status()
            data = a_resp.json() or []
            if isinstance(data, list) and len(data) == 0:
                return not_found("No se encontraron citas para el usuario")
            return make_response(HTTPStatus.OK, {"data": data, "meta": {"resource": "user-appointments"}})
        except HTTPError as http_err:
            status = http_err.response.status_code if http_err.response is not None else 502
            content = _safe_content(http_err)
            return make_response(HTTPStatus.BAD_GATEWAY, {
                "success": False,
                "error": "Error al consultar el API de Acuity",
                "upstream": {"status": status, "body": content},
            })
        except (Timeout, ReqConnectionError):
            return make_response(HTTPStatus.BAD_GATEWAY, {
                "success": False,
                "error": "Error de comunicación con el API de Acuity",
            })
        except RequestException:
            return make_response(HTTPStatus.BAD_GATEWAY, {
                "success": False,
                "error": "Error al consultar el API de Acuity",
            })

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error("*** xml tb_lineno: {}".format(exc_traceback.tb_lineno))
        logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
        return internal_server_error("Ocurrió un error inesperado. Contacte a soporte")


def _is_valid_date(yyyy_mm_dd: str) -> bool:
    try:
        parts = yyyy_mm_dd.split("-")
        if len(parts) != 3:
            return False
        y, m, d = [int(p) for p in parts]
        return 1 <= m <= 12 and 1 <= d <= 31 and len(parts[0]) == 4
    except Exception:
        return False


def _safe_content(http_err: HTTPError):
    try:
        if http_err.response is not None:
            return http_err.response.json()
        return None
    except Exception:
        return http_err.response.text if http_err.response is not None else None
