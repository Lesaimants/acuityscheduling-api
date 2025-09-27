import json
import logging
from http import HTTPStatus

from pydantic_core._pydantic_core import ValidationError

from decimalencoder import DecimalEncoder

logger = logging.getLogger()


def make_response(status_code, body=None) -> dict:
    """
    Creates a response dictionary with the given status code, body, and exception.

    Args:
        status_code (int): The HTTP status code of the response.
        body (dict, optional): The body of the response. Defaults to None.

    Returns:
        dict: The response dictionary with the following keys:
            - "statusCode" (int): The HTTP status code of the response.
            - "body" (str): The body of the response.
            - "isBase64Encoded" (bool): Indicates whether the body is base64 encoded.
            - "headers" (dict): The headers of the response.

    If the status code is greater than or equal to HTTPStatus.BAD_REQUEST, the response dictionary is logged with a warning level.
    If an exception is provided, it is logged with an error level.
    """
    messages = {
        HTTPStatus.OK: json.dumps(body, cls=DecimalEncoder),
        HTTPStatus.BAD_REQUEST: json.dumps(
            {"error": "Petición invalida"}, cls=DecimalEncoder
        ),
        HTTPStatus.NOT_FOUND: json.dumps(
            {"error": "Recurso no encontrado"}, cls=DecimalEncoder
        ),
        HTTPStatus.NOT_ACCEPTABLE: json.dumps(
            {"error": "Entrada invalida"}, cls=DecimalEncoder
        ),
        HTTPStatus.INTERNAL_SERVER_ERROR: json.dumps(
            {"error": "Ocurrió un error inesperado. Contacte a soporte"},
            cls=DecimalEncoder,
        ),
    }

    access_control_allow_headers = (
        "Content-Type,Authorization,Accept,Accept-Encoding,Connection,x-api-key,"
        "clientKey,clientSecret"
    )
    response = {
        "statusCode": status_code,
        "body": (
            json.dumps(body, cls=DecimalEncoder)
            if body is not None
            else messages.get(HTTPStatus(status_code))
        ),
        "isBase64Encoded": False,
        "headers": {
            "Access-Control-Allow-Headers": access_control_allow_headers,
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,PATCH,DELETE,HEAD",
            "Access-Control-Max-Age": "86400",
        },
    }

    if status_code >= HTTPStatus.BAD_REQUEST:
        logger.warning(response)

    return response


def ok(message: str, data=None) -> dict:
    """
    Creates a successful response dictionary with the given message and data.

    Args:
        message (str): The success message.
        data (dict, optional): The data associated with the response. Defaults to None.

    Returns:
        dict: The response dictionary with the following keys:
            - "statusCode" (int): The HTTP status code of the response.
            - "body" (dict): The body of the response containing the following keys:
                - "success" (bool): Indicates whether the request was successful.
                - "message" (str): The success message.
                - "data" (dict): The data associated with the response.
            - "isBase64Encoded" (bool): Indicates whether the body is base64 encoded.
            - "headers" (dict): The headers of the response.
    """
    return make_response(
        HTTPStatus.OK,
        {
            "success": True,
            "message": message,
            "data": data,
        },
    )


def bad_request(error: str, data: dict = None) -> dict:
    """
    Creates a failed response dictionary with the given error and data.

    Args:
        error (str): The error message.
        data (dict, optional): The data associated with the error. Defaults to None.

    Returns:
        dict: The response dictionary with the following keys:
            - "statusCode" (int): The HTTP status code of the response.
            - "body" (dict): The body of the response containing the following keys:
                - "success" (bool): Indicates whether the request was successful.
                - "error" (str): The error message.
                - "data" (dict): The data associated with the error.
            - "isBase64Encoded" (bool): Indicates whether the body is base64 encoded.
            - "headers" (dict): The headers of the response.
    """
    body = {
        "success": False,
        "error": error,
    }
    if data:
        body["data"] = data

    return make_response(HTTPStatus.BAD_REQUEST, body)


def not_found(error: str, data: dict = None) -> dict:
    """
    Creates a failed response dictionary with the given error and data.

    Args:
        error (str): The error message.
        data (dict, optional): The data associated with the error. Defaults to None.

    Returns:
        dict: The response dictionary with the following keys:
            - "statusCode" (int): The HTTP status code of the response.
            - "body" (dict): The body of the response containing the following keys:
                - "success" (bool): Indicates whether the request was successful.
                - "error" (str): The error message.
                - "data" (dict): The data associated with the error.
            - "isBase64Encoded" (bool): Indicates whether the body is base64 encoded.
            - "headers" (dict): The headers of the response.
    """
    body = {
        "success": False,
        "error": error,
    }
    if data:
        body["data"] = data

    return make_response(HTTPStatus.NOT_FOUND, body)


def not_acceptable(error: str, data: dict = None) -> dict:
    """
    Creates a failed response dictionary with the given error and data.

    Args:
        error (str): The error message.
        data (dict, optional): The data associated with the error. Defaults to None.

    Returns:
        dict: The response dictionary with the following keys:
            - "success" (bool): Indicates whether the request was successful.
            - "error" (str): The error message.
            - "data" (dict): The data associated with the error.
            - "statusCode" (int): The HTTP status code of the response.
            - "isBase64Encoded" (bool): Indicates whether the body is base64 encoded.
            - "headers" (dict): The headers of the response.
    """
    body = {
        "success": False,
        "error": error,
    }
    if data:
        body["data"] = data

    return make_response(HTTPStatus.NOT_ACCEPTABLE, body)


def internal_server_error(error: str, data: dict = None) -> dict:
    """
    Creates an internal server error response dictionary with the given error and data.

    Args:
        error (str): The error message.
        data (dict, optional): The data associated with the error. Defaults to None.

    Returns:
        dict: The response dictionary with the following keys:
            - "statusCode" (int): The HTTP status code of the response.
            - "body" (dict): The body of the response containing the following keys:
                - "success" (bool): Indicates whether the request was successful.
                - "error" (str): The error message.
                - "data" (dict): The data associated with the error.
            - "isBase64Encoded" (bool): Indicates whether the body is base64 encoded.
            - "headers" (dict): The headers of the response.
    """
    body = {
        "success": False,
        "error": error,
    }
    if data:
        body["data"] = data

    return make_response(HTTPStatus.INTERNAL_SERVER_ERROR, body)


def get_client_key(headers: dict) -> str or None:
    """
    Retrieves a client key from the provided headers.

    This function checks for the presence of a client key in the headers,
    regardless of case, and returns the key if found. If no key is found or
    the key is empty, the function returns None.

    Parameters:
        headers (dict): A dictionary of headers to search for the client key.

    Returns:
        str or None: The client key if found, otherwise None.
    """
    client_key = None
    if "clientKey" in headers:
        client_key = headers.get("clientKey")
    if "ClientKey" in headers:
        client_key = headers.get("ClientKey")
    if "clientkey" in headers:
        client_key = headers.get("clientkey")
    if "CLIENTKEY" in headers:
        client_key = headers.get("CLIENTKEY")

    if client_key and len(client_key) > 0:
        return client_key
    return None


def get_client_secret(headers: dict) -> str or None:
    """
    Retrieves a client secret from the provided headers.

    This function checks for the presence of a client secret in the headers,
    regardless of case, and returns the secret if found. If no secret is found or
    the secret is empty, the function returns None.

    Parameters:
        headers (dict): A dictionary of headers to search for the client secret.

    Returns:
        str or None: The client secret if found, otherwise None.
    """
    client_secret = None
    if "clientSecret" in headers:
        client_secret = headers.get("clientSecret")
    if "ClientSecret" in headers:
        client_secret = headers.get("ClientSecret")
    if "clientsecret" in headers:
        client_secret = headers.get("clientsecret")
    if "CLIENTSECRET" in headers:
        client_secret = headers.get("CLIENTSECRET")

    if client_secret and len(client_secret) > 0:
        return client_secret
    return None


def handle_error_validation(ex: ValidationError) -> str:
    """
    This function takes a ValidationError object and returns a string containing
    a human-readable description of the validation errors.

    Parameters:
        ex (ValidationError): The ValidationError object to process.

    Returns:
        str: A string containing a description of the validation errors.
    """
    errors = ex.errors()
    message = ". ".join(
        [
            f"{'.'.join([str(e) for e in error.get('loc')])} {error.get('msg', '')}"
            for error in errors
        ]
    )
    return message
