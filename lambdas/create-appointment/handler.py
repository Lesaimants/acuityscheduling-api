import logging
import os
import sys
import traceback
from http import HTTPStatus
from typing import Any, Dict

import requests
from requests import HTTPError
from requests.exceptions import Timeout, ConnectionError as ReqConnectionError, RequestException

from http_utils import make_response, internal_server_error, bad_request
from validation import validation
from validation_model import RequestBody
from db_user_links import DBUserLinks

logger = logging.getLogger()

BASE_URL = "https://acuityscheduling.com/api/v1"
DEFAULT_TIMEOUT = 10
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "create-appointment-lambda/1.0",
}

user_id = os.environ.get("ACUITY_USER_ID")
api_key = os.environ.get("ACUITY_API_KEY")
db_links = DBUserLinks()


@validation
def function_handler(event, __, request_body: RequestBody):
    try:
        # Authorizer context extraction
        auth_ctx = ((event or {}).get("requestContext") or {}).get("authorizer") or {}
        shopify_customer_id = str(auth_ctx.get("shopifyCustomerId")) if auth_ctx.get("shopifyCustomerId") is not None else None
        email = str(auth_ctx.get("email")) if auth_ctx.get("email") is not None else None
        first_name = str(auth_ctx.get("firstName")) if auth_ctx.get("firstName") is not None else ""
        last_name = str(auth_ctx.get("lastName")) if auth_ctx.get("lastName") is not None else ""
        phone = str(auth_ctx.get("phone")) if auth_ctx.get("phone") is not None else ""
        shop_domain = str(auth_ctx.get("shopDomain")) if auth_ctx.get("shopDomain") is not None else ""

        # Validar identidad mínima: requiere al menos teléfono o email
        if (not phone or phone.strip() == "") and (not email or str(email).strip() == ""):
            return bad_request("Debe proporcionar al menos un identificador del usuario (teléfono o email)")

        # Guardar/actualizar perfil del usuario en Dynamo sin acuityClientId
        if shopify_customer_id:
            existing = db_links.get({"customerId": str(shopify_customer_id), "profile": "les-aimants"})
            if not existing:
                db_links.upsert_profile(shopify_customer_id, {
                    "email": email,
                    "shopDomain": shop_domain or "",
                    "firstName": first_name or "",
                    "lastName": last_name or "",
                    "phone": phone or "",
                })

        # Crear cita. Incluir datos del cliente si están disponibles
        appointment_payload: Dict[str, Any] = {
            "datetime": request_body.datetime,
            "calendarID": request_body.calendarID,
            "appointmentTypeID": request_body.appointmentTypeID,
        }
        if request_body.timezone:
            appointment_payload["timezone"] = request_body.timezone
        if request_body.notes:
            appointment_payload["notes"] = request_body.notes
        # Datos de cliente desde authorizer
        if first_name:
            appointment_payload["firstName"] = first_name
        if last_name:
            appointment_payload["lastName"] = last_name
        if email:
            appointment_payload["email"] = email
        if phone:
            appointment_payload["phone"] = phone

        try:
            a_resp = requests.post(
                f"{BASE_URL}/appointments",
                json=appointment_payload,
                auth=(user_id, api_key),
                headers=HEADERS,
                timeout=DEFAULT_TIMEOUT,
            )
            a_resp.raise_for_status()
            a_data = a_resp.json()
            # 201 created
            return make_response(HTTPStatus.CREATED, {"data": a_data})
        except HTTPError as http_err:
            status = http_err.response.status_code if http_err.response is not None else 502
            content = _safe_content(http_err)
            return make_response(HTTPStatus.BAD_GATEWAY, {
                "success": False,
                "error": "Error al crear la cita en Acuity",
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


def _safe_content(http_err: HTTPError):
    try:
        if http_err.response is not None:
            try:
                return http_err.response.json()
            except Exception:
                return http_err.response.text
    except Exception:
        return None
    return None
