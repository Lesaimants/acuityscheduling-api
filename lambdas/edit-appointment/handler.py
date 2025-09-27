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
    "Content-Type": "application/json",
    "User-Agent": "edit-appointment-lambda/1.0",
}


user_id = os.environ.get("ACUITY_USER_ID")
api_key = os.environ.get("ACUITY_API_KEY")
db_links = DBUserLinks()


@validation
def function_handler(event, __, request_body: RequestBody):
    try:
        # 1) Authorizer context
        auth_ctx = ((event or {}).get("requestContext") or {}).get("authorizer") or {}
        shopify_customer_id = str(auth_ctx.get("shopifyCustomerId")) if auth_ctx.get("shopifyCustomerId") is not None else None
        email = str(auth_ctx.get("email")) if auth_ctx.get("email") is not None else None
        first_name = str(auth_ctx.get("firstName")) if auth_ctx.get("firstName") is not None else ""
        last_name = str(auth_ctx.get("lastName")) if auth_ctx.get("lastName") is not None else ""
        phone = str(auth_ctx.get("phone")) if auth_ctx.get("phone") is not None else ""
        shop_domain = str(auth_ctx.get("shopDomain")) if auth_ctx.get("shopDomain") is not None else ""

        # Requiere al menos teléfono o email
        if (not phone or phone.strip() == "") and (not email or str(email).strip() == ""):
            return make_response(HTTPStatus.UNAUTHORIZED, {
                "success": False,
                "error": "No autorizado: faltan datos del usuario (teléfono o email)",
            })

        appointment_id = str(request_body.appointmentId)
        action = request_body.action

        # 2) Guardar/actualizar perfil en Dynamo sin acuityClientId
        if shopify_customer_id:
            db_links.upsert_profile(shopify_customer_id, {
                "email": email,
                "shopDomain": shop_domain or "",
                "firstName": first_name or "",
                "lastName": last_name or "",
                "phone": phone or "",
            })

        # 3) Validar propiedad de la cita por teléfono o email
        try:
            get_resp = requests.get(
                f"{BASE_URL}/appointments/{appointment_id}",
                auth=(user_id, api_key),
                headers=HEADERS,
                timeout=DEFAULT_TIMEOUT,
            )
            if get_resp.status_code == 404:
                return not_found("La cita no existe")
            get_resp.raise_for_status()
            appt = get_resp.json() or {}

            # Extraer datos del cliente de la cita (defensivo)
            appt_phone = appt.get("phone")
            if appt_phone is None:
                appt_phone = (appt.get("client") or {}).get("phone")
            appt_email = appt.get("email")
            if appt_email is None:
                appt_email = (appt.get("client") or {}).get("email")

            # Comparar por teléfono normalizado, si no hay, por email
            is_owner = False
            if phone and appt_phone:
                is_owner = normalize_phone(phone) == normalize_phone(str(appt_phone))
            if not is_owner and email and appt_email:
                is_owner = str(email).strip().lower() == str(appt_email).strip().lower()

            if not is_owner:
                return not_found("La cita no pertenece al usuario autenticado")
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

        # 4) Execute action
        if action == "reschedule":
            if not request_body.datetime:
                return bad_request("Parámetro faltante: datetime")
            payload = {
                "datetime": request_body.datetime,
            }
            if request_body.calendarID is not None:
                payload["calendarID"] = request_body.calendarID
            if request_body.appointmentTypeID is not None:
                payload["appointmentTypeID"] = request_body.appointmentTypeID
            if request_body.timezone is not None:
                payload["timezone"] = request_body.timezone

            try:
                put_resp = requests.put(
                    f"{BASE_URL}/appointments/{appointment_id}/reschedule",
                    json=payload,
                    auth=(user_id, api_key),
                    headers=HEADERS,
                    timeout=DEFAULT_TIMEOUT,
                )
                if put_resp.status_code == 404:
                    return not_found("No fue posible reprogramar la cita")
                put_resp.raise_for_status()
                data = put_resp.json()
                return make_response(HTTPStatus.OK, {"data": data, "meta": {"action": "reschedule", "appointmentId": appointment_id}})
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

        elif action == "update":
            if request_body.notes is None and request_body.label is None and request_body.fields is None:
                return bad_request("Debe enviar al menos uno de los campos editables: notes, label o fields")
            payload = {}
            if request_body.notes is not None:
                payload["notes"] = request_body.notes
            if request_body.label is not None and str(request_body.label).strip() != "":
                # Acuity accepts array of objects; we'll send one element
                payload["label"] = [{"name": str(request_body.label)}]
            if request_body.fields is not None:
                payload["fields"] = request_body.fields
            if request_body.admin is True:
                payload["admin"] = True

            try:
                put_resp = requests.put(
                    f"{BASE_URL}/appointments/{appointment_id}",
                    json=payload,
                    auth=(user_id, api_key),
                    headers=HEADERS,
                    timeout=DEFAULT_TIMEOUT,
                )
                if put_resp.status_code == 404:
                    return not_found("No existe la cita o no hay cambios que aplicar")
                put_resp.raise_for_status()
                data = put_resp.json()
                return make_response(HTTPStatus.OK, {"data": data, "meta": {"action": "update", "appointmentId": appointment_id}})
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
        else:
            return bad_request("Acción inválida. Use 'update' o 'reschedule'")

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error("*** xml tb_lineno: {}".format(exc_traceback.tb_lineno))
        logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
        return internal_server_error("Ocurrió un error inesperado. Contacte a soporte")


def normalize_phone(p: str | None) -> str | None:
    if p is None:
        return None
    s = str(p)
    # Keep leading + and digits, remove spaces, dashes, parentheses and other formatting
    out = []
    for i, ch in enumerate(s):
        if ch.isdigit():
            out.append(ch)
        elif ch == '+' and len(out) == 0:
            out.append(ch)
        # ignore other chars
    return ''.join(out)


def _safe_content(http_err: HTTPError):
    try:
        if http_err.response is not None:
            return http_err.response.json()
        return None
    except Exception:
        return http_err.response.text if http_err.response is not None else None
