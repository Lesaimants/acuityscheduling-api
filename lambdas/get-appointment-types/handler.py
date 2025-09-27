import logging
import os
import sys
import traceback
from http import HTTPStatus

import requests
from requests import HTTPError
from requests.exceptions import Timeout, ConnectionError as ReqConnectionError, RequestException

from http_utils import make_response, internal_server_error

logger = logging.getLogger()

# Constants per spec
BASE_URL = "https://acuityscheduling.com/api/v1"
DEFAULT_TIMEOUT = 10
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "get-appointment-types-lambda/1.0",
}

def function_handler(_, __):
    try:
        # Credentials are assumed to be present in env variables
        user_id = os.environ["ACUITY_USER_ID"]
        api_key = os.environ["ACUITY_API_KEY"]

        url = f"{BASE_URL}/appointment-types"

        try:
            response = requests.get(
                url,
                auth=(user_id, api_key),
                headers=HEADERS,
                timeout=DEFAULT_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            return make_response(
                HTTPStatus.OK,
                {"data": data, "meta": {"resource": "appointment-types"}},
            )
        except HTTPError as http_err:
            status = http_err.response.status_code if http_err.response is not None else 502
            content = None
            try:
                if http_err.response is not None:
                    content = http_err.response.json()
            except Exception:
                try:
                    content = http_err.response.text if http_err.response is not None else None
                except Exception:
                    content = None
            return make_response(
                HTTPStatus.BAD_GATEWAY,
                {
                    "success": False,
                    "error": "Error al consultar el API de Acuity",
                    "upstream": {"status": status, "body": content},
                },
            )
        except (Timeout, ReqConnectionError) as net_err:
            logger.error(f"Error de comunicación (timeout/conexión) con Acuity: {net_err}")
            return make_response(
                HTTPStatus.BAD_GATEWAY,
                {"success": False, "error": "Error de comunicación con el API de Acuity"},
            )
        except RequestException as req_err:
            logger.error(f"Error en la solicitud a Acuity: {req_err}")
            return make_response(
                HTTPStatus.BAD_GATEWAY, {"success": False, "error": "Error al consultar el API de Acuity"}
            )

    except Exception:
        # Generic unexpected error handling with internal logging only
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error("*** xml tb_lineno: {}".format(exc_traceback.tb_lineno))
        logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
        return internal_server_error("Ocurrió un error inesperado. Contacte a soporte")
