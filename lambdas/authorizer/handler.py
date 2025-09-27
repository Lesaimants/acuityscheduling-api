import logging
import os
import sys
import traceback
from typing import Dict, Any, Optional
import requests

import json
logger = logging.getLogger()
logger.setLevel(logging.INFO)

DEFAULT_TIMEOUT = 8  # seconds
DEFAULT_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2024-07")
shop_domain = os.getenv("SHOPIFY_STORE_DOMAIN")
storefront_token = os.getenv("SHOPIFY_STOREFRONT_ACCESS_TOKEN")


SHOPIFY_CUSTOMER_QUERY = (
    "query customerByToken($token: String!) { "
    "customer(customerAccessToken: $token) { id email firstName lastName phone } "
    "}"
)


def function_handler(event, context):
    try:
        print(event)
        token = _extract_bearer_token(event.get("headers", {}) or {})
        if not token:
            return _unauthorized(event)

        data = _shopify_graphql_request(shop_domain, storefront_token, token)
        if not data:
            return _unauthorized(event)

        customer = (((data or {}).get("data") or {}).get("customer")) if isinstance(data, dict) else None
        if not customer or not isinstance(customer, dict) or not customer.get("id"):
            return _unauthorized(event)

        gid = str(customer.get("id"))
        email = str(customer.get("email") or "")
        first_name = str(customer.get("firstName") or "")
        last_name = str(customer.get("lastName") or "")
        phone = str(customer.get("phone") or "")
        customer_id_num = parse_customer_gid(gid)
        if customer_id_num == "anonymous":
            return _unauthorized(event)

        # Build Allow policy with context
        method_arn = event.get("methodArn", "*")
        context_dict = {
            "shopifyCustomerGID": gid,
            "shopifyCustomerId": customer_id_num,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "phone": phone,
            "shopDomain": shop_domain,
            "tokenType": "shopify_customer_access_token",
        }
        print("arn:aws:execute-api:*:*:*/*")
        return build_policy(customer_id_num, "Allow", "arn:aws:execute-api:*:*:*/*", context_dict)
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error("Authorizer exception at line {}".format(exc_traceback.tb_lineno))
        logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
        return _unauthorized(event)


def parse_customer_gid(gid: Optional[str]) -> str:
    try:
        if not gid:
            return "anonymous"
        # Expected format: gid://shopify/Customer/123456789
        parts = str(gid).strip().split("/")
        num = parts[-1]
        return str(int(num))  # normalize and validate numeric
    except Exception:
        return "anonymous"


def build_policy(principal_id: str, effect: str, resource_arn: str, context_dict: Dict[str, str]) -> Dict[str, Any]:
    # Ensure all context values are strings
    context = {k: ("" if v is None else str(v)) for k, v in (context_dict or {}).items()}
    return {
        "principalId": principal_id or "anonymous",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource_arn,
                }
            ],
        },
        "context": context,
    }


def _wildcard_method_arn(method_arn: str) -> str:
    try:
        if not method_arn or not isinstance(method_arn, str):
            return "*"
        # Expected: arn:aws:execute-api:{region}:{accountId}:{apiId}/{stage}/{httpVerb}/{resourcePath}
        parts = method_arn.split(":", 5)
        if len(parts) < 6:
            return method_arn
        prefix = ":".join(parts[:5])  # arn:aws:execute-api:{region}:{accountId}
        rest = parts[5]  # {apiId}/{stage}/{httpVerb}/{resourcePath}
        # Now split rest by '/'
        rest_parts = rest.split("/")
        # rest_parts[0]=apiId, [1]=stage
        if len(rest_parts) < 2:
            return method_arn
        api_id = rest_parts[0]
        stage = rest_parts[1]
        return f"{prefix}:{api_id}/{stage}/*/*"
    except Exception:
        return method_arn


def _unauthorized(event):
    return {
        "principalId": "user",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Deny",
                    "Resource": event.get("methodArn", ""),
                }
            ],
        }
    }


def _extract_bearer_token(headers) -> Optional[str]:
    authorization = None
    if 'authorization' in headers:
        authorization = headers.get('authorization')
    if 'Authorization' in headers:
        authorization = headers.get('Authorization')
    if 'AUTHORIZATION' in headers:
        authorization = headers.get('AUTHORIZATION')

    if authorization and len(authorization) > 0:
        return authorization[7:]
    return None


def _shopify_graphql_request(shop_domain: str, storefront_token: str, customer_token: str) -> Optional[Dict[str, Any]]:
    url = f"https://{shop_domain}/api/{DEFAULT_API_VERSION}/graphql.json"
    payload = {"query": SHOPIFY_CUSTOMER_QUERY, "variables": {"token": customer_token}}
    body = json.dumps(payload).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Storefront-Access-Token": storefront_token,
    }
    timeout = DEFAULT_TIMEOUT

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)  # type: ignore
        status = resp.status_code
        text = resp.text

        if status < 200 or status >= 300:
            logger.error(f"Shopify GraphQL HTTP error: {status}")
            return None
        data = json.loads(text)
        return data
    except Exception as e:
        logger.error(f"Error calling Shopify GraphQL: {e}")
        return None
