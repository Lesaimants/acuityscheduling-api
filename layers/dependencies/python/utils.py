import logging
import uuid
import datetime
import pytz
import time
import random

logger = logging.getLogger()


def is_valid_uuid(value: str) -> bool:
    """
    Checks if the given string is a valid UUID.

    Args:
        value (str): The string to be checked.

    Returns:
        bool: True if the string is a valid UUID, False otherwise.
    """
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def locale_now(format_date: str = "%Y%m%d%H%M%S%f") -> str:
    """
    Returns the current date and time in the locale timezone ("America/Mexico_City")
    in the format defined by the format_date parameter.

    Args:
        format_date (str): The format string to be used by the strftime function.
            Defaults to "%Y%m%d%H%M%S%f".

    Returns:
        str: The current date and time in the locale timezone in the specified format.
    """
    now = datetime.datetime.now(tz=pytz.timezone("America/Mexico_City"))
    return now.strftime(format_date)


def get_timestamp(
    body=None,
    millisecond: bool = False,
    timezone: datetime.timezone = datetime.timezone.utc,
) -> str:
    """
    Returns a timestamp string in the format "%Y-%m-%dT%H:%M:%S.000Z" based on the provided body and timezone.

    Args:
        body (dict or int or float, optional): The body to extract the timestamp from. Defaults to None.
        millisecond (bool, optional): Whether the timestamp is in milliseconds. Defaults to False.
        timezone (datetime.timezone, optional): The timezone to use for the timestamp. Defaults to datetime.timezone.utc.

    Returns:
        str: The timestamp string.
    """
    if body and type(body) is dict:
        if (created_at := body.get("created_at")) and type(created_at) is int:
            dt_object = datetime.datetime.fromtimestamp(
                created_at / (1000 if millisecond else 1), timezone
            )
            return (
                (
                    dt_object.strftime("%Y-%m-%dT%H:%M:%S")
                    + dt_object.strftime(".%f")[:4]
                    + "Z"
                )
                if millisecond
                else dt_object.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            )
        elif (created_at := body.get("createdAt")) and type(created_at) is int:
            dt_object = datetime.datetime.fromtimestamp(
                created_at / (1000 if millisecond else 1), timezone
            )
            return (
                (
                    dt_object.strftime("%Y-%m-%dT%H:%M:%S")
                    + dt_object.strftime(".%f")[:4]
                    + "Z"
                )
                if millisecond
                else dt_object.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            )
        elif (timestamp := body.get("timestamp")) and type(timestamp) is int:
            dt_object = datetime.datetime.fromtimestamp(
                timestamp / (1000 if millisecond else 1), timezone
            )
            return (
                (
                    dt_object.strftime("%Y-%m-%dT%H:%M:%S")
                    + dt_object.strftime(".%f")[:4]
                    + "Z"
                )
                if millisecond
                else dt_object.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            )
    if body and type(body) is (int or float):
        dt_object = datetime.datetime.fromtimestamp(
            body / (1000 if millisecond else 1), timezone
        )
        return (
            (
                dt_object.strftime("%Y-%m-%dT%H:%M:%S")
                + dt_object.strftime(".%f")[:4]
                + "Z"
            )
            if millisecond
            else dt_object.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        )

    dt_object = datetime.datetime.now(timezone)
    return (
        (dt_object.strftime("%Y-%m-%dT%H:%M:%S") + dt_object.strftime(".%f")[:4] + "Z")
        if millisecond
        else dt_object.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    )


def generate_uuid():
    """
    Generates a random UUID (Universally Unique Identifier) string.

    This function uses a combination of random numbers and a predefined format to create a unique identifier.

    Parameters:
    None

    Returns:
    str: A random UUID string.
    """
    random_string = ""
    random_str_seq = "0123456789ABCDEF"
    uuid_format = [8, 4, 4, 4, 16]
    now = int(time.time() * 1000)
    random.seed(a=now, version=2)
    index = 0
    for n in uuid_format:
        start = 0
        if index == 2:
            random_string += "4"
            start = 1
        index += 1
        for i in range(start, n):
            random_string += str(
                random_str_seq[random.randint(0, len(random_str_seq) - 1)]
            )
        if index <= 4:
            random_string += "-"
    return random_string


def get_cognito_username(event: dict) -> str:
    """
    Extracts the username from a Cognito User Pool Authorizer event.

    The username is extracted from the "sub" claim in the authorizer event.

    Args:
        event (dict): The event object from the Cognito User Pool Authorizer.

    Returns:
        str: The username if found, otherwise None.
    """
    response = None
    if (
        sub := event.get("requestContext", {})
        .get("authorizer", {})
        .get("claims", {})
        .get("sub")
    ):
        response = sub

    return response


def get_cognito_user_pool_id(event: dict) -> str:
    response = None
    if (
        iss := event.get("requestContext", {})
        .get("authorizer", {})
        .get("claims", {})
        .get("iss")
    ):
        if parts := iss.split("/"):
            response = parts[len(parts) - 1]
    return response
