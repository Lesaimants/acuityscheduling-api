import decimal
import json
import math
import logging
import sys
import traceback
from datetime import datetime

logger = logging.getLogger()


# This is a workaround for: http://bugs.python.org/issue16535
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        """
        Override the default method of the JSONEncoder class to handle
        custom objects such as datetime and decimal.

        :param obj: The object to be encoded.
        :type obj: Any
        :return: The encoded object.
        :rtype: Any
        """
        try:
            if isinstance(obj, datetime):
                return obj.__str__()
            if isinstance(obj, decimal.Decimal):
                number = float(obj)
                part_float, part_int = math.modf(number)
                if abs(part_float) > 0:
                    return number
                return int(part_int)
            return super(DecimalEncoder, self).default(obj)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error("*** xml tb_lineno: {}".format(exc_traceback.tb_lineno))
            logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
