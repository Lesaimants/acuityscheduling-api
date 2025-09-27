import logging
import os
import sys
import traceback
from http import HTTPStatus

import requests
from requests import HTTPError
from requests.exceptions import Timeout, ConnectionError as ReqConnectionError, RequestException

from http_utils import make_response, internal_server_error, bad_request
from validation import validation
from validation_model import RequestBody

logger = logging.getLogger()

BASE_URL = "https://acuityscheduling.com/api/v1"
DEFAULT_TIMEOUT = 10
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "get-appointments-lambda/1.0",
}


@validation
def function_handler(_, __, request_body: RequestBody):
    try:
        user_id = os.environ.get("ACUITY_USER_ID")
        api_key = os.environ.get("ACUITY_API_KEY")
        resource = request_body.resource
        params = {}
        url = BASE_URL

        if resource == "appointments":
            # validate required
            missing = []
            if not request_body.start_date:
                missing.append("start_date")
            if not request_body.end_date:
                missing.append("end_date")
            if missing:
                return bad_request(f"Parámetros faltantes: {', '.join(missing)}")
            if not _is_valid_date(request_body.start_date) or not _is_valid_date(request_body.end_date):
                return bad_request("Formato de fecha inválido. Use YYYY-MM-DD en start_date y end_date")

            url += "/appointments"
            params = {
                "minDate": request_body.start_date,
                "maxDate": request_body.end_date,
            }
            if request_body.calendarId is not None:
                params["calendarID"] = request_body.calendarId
            if request_body.appointmentTypeId is not None:
                params["appointmentTypeID"] = request_body.appointmentTypeId
            if request_body.limit is not None:
                params["limit"] = request_body.limit
            if request_body.page is not None:
                params["page"] = request_body.page

        elif resource == "availability":
            if not request_body.date:
                return bad_request("Parámetro faltante: date")
            if not _is_valid_date(request_body.date):
                return bad_request("Formato de fecha inválido. Use YYYY-MM-DD en date")

            url += "/availability/times"
            params = {
                "date": request_body.date,
            }
            if request_body.calendarId is not None:
                params["calendarID"] = request_body.calendarId
            if request_body.appointmentTypeId is not None:
                params["appointmentTypeID"] = request_body.appointmentTypeId
            if request_body.timezone is not None:
                params["timezone"] = request_body.timezone
        else:
            return bad_request("Valor de 'resource' inválido. Use 'appointments' o 'availability'")

        try:
            response = requests.get(url, params=params, auth=(user_id, api_key), headers=HEADERS, timeout=DEFAULT_TIMEOUT)
            # raise for status to catch as HTTPError
            response.raise_for_status()
            data = response.json()
            return make_response(HTTPStatus.OK, {"data": data, "meta": {"resource": resource}})
        except HTTPError as http_err:
            status = http_err.response.status_code if http_err.response is not None else 502
            content = None
            try:
                if http_err.response is not None:
                    content = http_err.response.json()
                else:
                    content = None
            except Exception:
                content = http_err.response.text if http_err.response is not None else None
            # Return as upstream error
            return make_response(HTTPStatus.BAD_GATEWAY, {
                "success": False,
                "error": "Error al consultar el API de Acuity",
                "upstream": {"status": status, "body": content},
            })
        except (Timeout, ReqConnectionError) as net_err:
            logger.error(f"Error de red/timeout consultando Acuity: {net_err}")
            return make_response(HTTPStatus.BAD_GATEWAY, {
                "success": False,
                "error": "Error de comunicación con el API de Acuity",
            })
        except RequestException as req_err:
            logger.error(f"Error de solicitud Acuity: {req_err}")
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
        # simple validation to avoid extra deps
        parts = yyyy_mm_dd.split("-")
        if len(parts) != 3:
            return False
        y, m, d = [int(p) for p in parts]
        return 1 <= m <= 12 and 1 <= d <= 31 and len(parts[0]) == 4
    except Exception:
        return False
