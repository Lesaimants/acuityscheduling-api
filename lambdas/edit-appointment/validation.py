import sys
import json
import logging
import traceback
from pydantic import ValidationError
from http_utils import not_acceptable, handle_error_validation

from validation_model import RequestBody

logger = logging.getLogger()


def validation(function):
    def wrapper(*args, **kwargs):
        try:
            event = args[0]
            print(event)
            request_body = __validation(event)
            kwargs["request_body"] = request_body
        except ValidationError as error:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(
                "{} *** xml tb_lineno: {}".format(
                    function.__name__, exc_traceback.tb_lineno
                )
            )
            logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
            return not_acceptable(handle_error_validation(error))
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(
                "{} *** xml tb_lineno: {}".format(
                    function.__name__, exc_traceback.tb_lineno
                )
            )
            logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
            return not_acceptable("Invalid input")
        return function(*args, **kwargs)

    return wrapper


def __validation(event) -> RequestBody:
    body = event.get("body")
    body = json.loads(body)
    return RequestBody(**body)
