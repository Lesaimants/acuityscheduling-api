import json
import logging
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
from dynamodb_json import json_util

from decimalencoder import DecimalEncoder
from exception_handling import catch_and_raise

dynamodb = boto3.resource("dynamodb")
logger = logging.getLogger()


class DBRepository:
    def __init__(self, name):
        """
        Initializes a DBRepository instance.

        Args:
            name (str): The name of the DynamoDB table.

        Returns:
            None
        """
        self.name = name
        self.table = dynamodb.Table(name)

    @catch_and_raise
    def save(self, item):
        """
        Saves an item to the DynamoDB table.

        Args:
            item (dict): The item to be saved.

        Returns:
            dict: The result of the put_item operation.
        """
        dynamodb_item = json.loads(
            json.dumps(item, cls=DecimalEncoder), parse_float=Decimal
        )
        return self.table.put_item(Item=dynamodb_item)

    @catch_and_raise
    def update(self, key, items):
        """
        Updates an item in the DynamoDB table.

        Args:
            key (dict): The key of the item to be updated.
            items (dict): The attributes to be updated.

        Returns:
            dict: The result of the update_item operation.
        """
        values = {}
        names = {}
        items = json.loads(json.dumps(items, cls=DecimalEncoder), parse_float=Decimal)
        update_expression = ""
        for key_item, value in items.items():
            key_value = ":{}".format(key_item)
            key_name = "#{}".format(key_item)
            names[key_name] = key_item
            if len(update_expression) > 0:
                update_expression = "{}, {}={}".format(
                    update_expression, key_name, key_value
                )
            else:
                update_expression = "SET {}={}".format(key_name, key_value)
            values[key_value] = value
        return self.table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
        )

    @catch_and_raise
    def batch_update(self, rows):
        """
        Updates multiple items in the DynamoDB table in a batch operation.

        Args:
            rows (List[dict]): A list of dictionaries, where each dictionary contains the key and items to be updated.

        Returns:
            None
        """
        with self.table.batch_writer() as batch:
            for row in rows:
                key = row.get("key")
                items = row.get("items")
                names = {}
                values = {}
                update_expression = []
                for key_item, value in items.items():
                    key_value = ":{}".format(key_item)
                    key_name = "#{}".format(key_item)
                    names[key_name] = key_item
                    if type(value) == bool:
                        value = "true" if value else "false"
                    update_expression.append("{}={}".format(key_name, key_value))
                    values[key_value] = value
                update_expression = "SET " + ", ".join(update_expression)
                batch.update_item(
                    Key=key,
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=names,
                    ExpressionAttributeValues=values,
                )

    @catch_and_raise
    def delete(self, key):
        """
        Deletes an item from the DynamoDB table.

        Args:
            key (dict): The key of the item to be deleted.

        Returns:
            bool: True if the item is deleted successfully.
        """
        self.table.delete_item(Key=key)
        return True

    @catch_and_raise
    def get(self, key):
        """
        Retrieves an item from the DynamoDB table based on the provided key.

        Args:
            key (dict): The key of the item to be retrieved.

        Returns:
            dict: The retrieved item, or None if the item does not exist.
        """
        item = self.table.get_item(Key=key)

        if item and item.get("Item"):
            return json_util.loads(item["Item"])

    @catch_and_raise
    def exist(self, key):
        """
        Checks if an item exists in the DynamoDB table based on the provided key.

        Args:
            key (dict): The key of the item to be checked.

        Returns:
            bool: True if the item exists, False otherwise.
        """
        item = self.table.get_item(Key=key, AttributesToGet=list(key.keys()))
        return True if item and item.get("Item") else False

    @catch_and_raise
    def query(
        self,
        key: dict,
        index: str = None,
        last_evaluated_key: dict = None,
        filter_expression: str = None,
        projection_expression: str = None,
        expression_attribute_values: dict = None,
        expression_attribute_names: dict = None,
        scan_index_forward: bool = None,
    ):
        """
        Queries items from the DynamoDB table.

        Args:
            key (dict): The key condition for the query. Each key in the dictionary must match the corresponding attribute in the item.
            index (str, optional): The name of the index to query. Defaults to None.
            last_evaluated_key (dict, optional): The key of the last item evaluated in the previous query. Defaults to None.
            filter_expression (str, optional): A filter expression to apply to the query results. Defaults to None.
            projection_expression (str, optional): A projection expression to specify the attributes to return. Defaults to None.
            expression_attribute_values (dict, optional): A dictionary of attribute values to use in the filter and projection expressions. Defaults to None.
            expression_attribute_names (dict, optional): A dictionary of attribute names to use in the filter and projection expressions. Defaults to None.

        Returns:
            dict: The response from the DynamoDB query operation.
        """
        key_condition = None
        for k, v in key.items():
            key_condition = (
                Key(k).eq(v) if key_condition is None else key_condition & Key(k).eq(v)
            )

        params = {
            "KeyConditionExpression": key_condition,
        }
        if index:
            params["IndexName"] = index
        if filter_expression:
            params["FilterExpression"] = filter_expression
        if expression_attribute_names:
            params["ExpressionAttributeNames"] = expression_attribute_names
        if expression_attribute_values:
            params["ExpressionAttributeValues"] = expression_attribute_values
        if projection_expression:
            params["ProjectionExpression"] = projection_expression
        if last_evaluated_key:
            params["ExclusiveStartKey"] = last_evaluated_key
        if scan_index_forward is not None:
            params["ScanIndexForward"] = scan_index_forward

        response = self.table.query(**params)

        return response

    @catch_and_raise
    def query_all(
        self,
        key: dict,
        index: str = None,
        filter_expression: str = None,
        projection_expression: str = None,
        expression_attribute_values: dict = None,
        expression_attribute_names: dict = None,
        scan_index_forward: bool = None,
    ):
        """
        Queries all items from the DynamoDB table based on the provided key.

        Args:
            key (dict): The key of the items to be queried.
            index (str, optional): The name of the index to query. Defaults to None.
            filter_expression (str, optional): A filter expression to apply to the query results. Defaults to None.
            projection_expression (str, optional): A projection expression to specify the attributes to return. Defaults to None.
            expression_attribute_values (dict, optional): A dictionary of attribute values to use in the filter and projection expressions. Defaults to None.
            expression_attribute_names (dict, optional): A dictionary of attribute names to use in the filter and projection expressions. Defaults to None.

        Returns:
            dict: A dictionary containing the queried items and the count of items.
        """
        key_condition = None
        for k, v in key.items():
            key_condition = (
                Key(k).eq(v) if key_condition is None else key_condition & Key(k).eq(v)
            )

        params = {
            "KeyConditionExpression": key_condition,
        }
        if index:
            params["IndexName"] = index
        if filter_expression:
            params["FilterExpression"] = filter_expression
        if expression_attribute_names:
            params["ExpressionAttributeNames"] = expression_attribute_names
        if expression_attribute_values:
            params["ExpressionAttributeValues"] = expression_attribute_values
        if projection_expression:
            params["ProjectionExpression"] = projection_expression
        if scan_index_forward is not None:
            params["ScanIndexForward"] = scan_index_forward

        result = self.table.query(**params)
        items = result["Items"]
        count = result["Count"]

        while result.get("LastEvaluatedKey"):
            params["ExclusiveStartKey"] = result["LastEvaluatedKey"]
            result = self.table.query(**params)
            items = items + result["Items"]
            count += result["Count"]

        return {"Items": items, "Count": count}

    @catch_and_raise
    def scan(
        self,
        last_evaluated_key: dict = None,
        filter_expression: str = None,
        projection_expression: str = None,
        expression_attribute_values: dict = None,
        expression_attribute_names: dict = None,
    ):
        """
        Scans the DynamoDB table and returns the items.

        Args:
            last_evaluated_key (dict, optional): The key of the last item evaluated in the previous scan operation. Defaults to None.
            filter_expression (str, optional): A filter expression to apply to the scan results. Defaults to None.
            projection_expression (str, optional): A projection expression to specify the attributes to return. Defaults to None.
            expression_attribute_values (dict, optional): A dictionary of attribute values to use in the filter and projection expressions. Defaults to None.
            expression_attribute_names (dict, optional): A dictionary of attribute names to use in the filter and projection expressions. Defaults to None.

        Returns:
            dict: The response from the DynamoDB scan operation.
        """
        params = {}
        if filter_expression:
            params["FilterExpression"] = filter_expression
        if expression_attribute_names:
            params["ExpressionAttributeNames"] = expression_attribute_names
        if expression_attribute_values:
            params["ExpressionAttributeValues"] = expression_attribute_values
        if projection_expression:
            params["ProjectionExpression"] = projection_expression
        if last_evaluated_key:
            params["ExclusiveStartKey"] = last_evaluated_key

        response = self.table.scan(**params)

        return response

    @catch_and_raise
    def scan_all(
        self,
        filter_expression: str = None,
        projection_expression: str = None,
        expression_attribute_values: dict = None,
        expression_attribute_names: dict = None,
    ):
        """
        Scans the DynamoDB table and returns all items.

        Args:
            filter_expression (str, optional): A filter expression to apply to the scan results. Defaults to None.
            projection_expression (str, optional): A projection expression to specify the attributes to return. Defaults to None.
            expression_attribute_values (dict, optional): A dictionary of attribute values to use in the filter and projection expressions. Defaults to None.
            expression_attribute_names (dict, optional): A dictionary of attribute names to use in the filter and projection expressions. Defaults to None.

        Returns:
            dict: A dictionary containing the items and count of all items in the DynamoDB table that match the scan criteria.
        """
        params = {}
        if filter_expression:
            params["FilterExpression"] = filter_expression
        if expression_attribute_names:
            params["ExpressionAttributeNames"] = expression_attribute_names
        if expression_attribute_values:
            params["ExpressionAttributeValues"] = expression_attribute_values
        if projection_expression:
            params["ProjectionExpression"] = projection_expression

        result = self.table.scan(**params)
        items = result["Items"]
        count = result["Count"]

        while result.get("LastEvaluatedKey"):
            params["ExclusiveStartKey"] = result["LastEvaluatedKey"]
            result = self.table.scan(**params)
            items = items + result["Items"]
            count += result["Count"]

        return {"Items": items, "Count": count}
