import logging
import traceback
import sys

logger = logging.getLogger()


def catch(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as error:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(
                "{} *** xml tb_lineno: {}".format(
                    function.__name__, exc_traceback.tb_lineno
                )
            )
            logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))

    return wrapper


def catch_and_raise(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as error:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(
                "{} *** xml tb_lineno: {}".format(
                    function.__name__, exc_traceback.tb_lineno
                )
            )
            logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise error

    return wrapper
