import boto3
import sys
import traceback
import logging
from typing_extensions import List

logger = logging.getLogger()
MAX_SIZE_SLICE = 99


class DBTransactionItems:
    def __init__(self):
        """
        Initialize the object by setting up the 'client' attribute with a
        connection to the 'dynamodb' service.
        """
        self.client = boto3.client("dynamodb")

    def write(self, transact_items: List[dict]):
        """
        Writes a list of transaction items to DynamoDB.

        Args:
            transact_items (List[dict]): A list of transaction items to be written.

        Returns:
            bool: True if the write operation is successful, False otherwise.
        """
        try:
            total = len(transact_items)
            results = []
            for i in range(MAX_SIZE_SLICE, total + MAX_SIZE_SLICE, MAX_SIZE_SLICE):
                __slice = transact_items[i - MAX_SIZE_SLICE : i]
                result = self.client.transact_write_items(TransactItems=__slice)
                results.append(result)
            filtered_results = list(filter(lambda j: not j, results))
            return len(filtered_results) == 0
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(
                "TransactionItems.write *** xml tb_lineno: {}".format(
                    exc_traceback.tb_lineno
                )
            )
            logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
            return False
