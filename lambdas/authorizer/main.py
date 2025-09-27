import os
import traceback
import boto3
import sys
import json

# boto3.setup_default_session(profile_name="batrabajo", region_name="us-west-2")
os.environ["ACUITY_USER_ID"] = "31532355"
os.environ["ACUITY_API_KEY"] = "f1d28177592296ae44d57cd84b3d3c5c"
os.environ["SHOPIFY_STORE_DOMAIN"] = "les-aimants.myshopify.com"
os.environ["SHOPIFY_STOREFRONT_ACCESS_TOKEN"] = "495be658c9a93ba95807d1a826ef63ea"
os.environ["SHOPIFY_API_VERSION"] = "2024-07"
from handler import function_handler
from decimalencoder import DecimalEncoder

if __name__ == "__main__":
    try:
        body = {
            "resource": "appointments",
            "start_date": "2025-09-16",
            "end_date": "2025-09-20",
            "application": "lottery"
        }
        event = {'type': 'REQUEST', 'methodArn': 'arn:aws:execute-api:us-east-1:420988533524:cj8reit303/prod/GET/',
                 'resource': '/', 'path': '/', 'httpMethod': 'GET',
                 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br',
                             'Authorization': 'Bearer 5c9dc7665ce7a0aa616779216e27e239',
                             'CloudFront-Forwarded-Proto': 'https', 'CloudFront-Is-Desktop-Viewer': 'true',
                             'CloudFront-Is-Mobile-Viewer': 'false', 'CloudFront-Is-SmartTV-Viewer': 'false',
                             'CloudFront-Is-Tablet-Viewer': 'false', 'CloudFront-Viewer-ASN': '14593',
                             'CloudFront-Viewer-Country': 'MX',
                             'Host': 'cj8reit303.execute-api.us-east-1.amazonaws.com',
                             'Postman-Token': '86f347f7-e76e-443c-8da8-8e41f98b4c7f',
                             'User-Agent': 'PostmanRuntime/7.45.0',
                             'Via': '1.1 7c261084015941dccb6d50655477b04c.cloudfront.net (CloudFront)',
                             'X-Amz-Cf-Id': '1LZtL-pYzIU8hmcQecmTIQAV_V6qoEqStOV4y3mAx4ZaOCwdhgrUGQ==',
                             'X-Amzn-Trace-Id': 'Root=1-68cb2571-2d49f2d01b5467b031f3085f',
                             'X-Forwarded-For': '143.105.18.199, 18.68.36.111', 'X-Forwarded-Port': '443',
                             'X-Forwarded-Proto': 'https'},
                 'multiValueHeaders': {'Accept': ['*/*'], 'Accept-Encoding': ['gzip, deflate, br'],
                                       'Authorization': ['Bearer 5c9dc7665ce7a0aa616779216e27e239'],
                                       'CloudFront-Forwarded-Proto': ['https'],
                                       'CloudFront-Is-Desktop-Viewer': ['true'],
                                       'CloudFront-Is-Mobile-Viewer': ['false'],
                                       'CloudFront-Is-SmartTV-Viewer': ['false'],
                                       'CloudFront-Is-Tablet-Viewer': ['false'], 'CloudFront-Viewer-ASN': ['14593'],
                                       'CloudFront-Viewer-Country': ['MX'],
                                       'Host': ['cj8reit303.execute-api.us-east-1.amazonaws.com'],
                                       'Postman-Token': ['86f347f7-e76e-443c-8da8-8e41f98b4c7f'],
                                       'User-Agent': ['PostmanRuntime/7.45.0'],
                                       'Via': ['1.1 7c261084015941dccb6d50655477b04c.cloudfront.net (CloudFront)'],
                                       'X-Amz-Cf-Id': ['1LZtL-pYzIU8hmcQecmTIQAV_V6qoEqStOV4y3mAx4ZaOCwdhgrUGQ=='],
                                       'X-Amzn-Trace-Id': ['Root=1-68cb2571-2d49f2d01b5467b031f3085f'],
                                       'X-Forwarded-For': ['143.105.18.199, 18.68.36.111'], 'X-Forwarded-Port': ['443'],
                                       'X-Forwarded-Proto': ['https']}, 'queryStringParameters': {},
                 'multiValueQueryStringParameters': {}, 'pathParameters': {}, 'stageVariables': {},
                 'requestContext': {'resourceId': 'sa2t7axg87', 'resourcePath': '/', 'httpMethod': 'GET',
                                    'extendedRequestId': 'RELJ2E1WoAMEiYg=',
                                    'requestTime': '17/Sep/2025:21:17:37 +0000', 'path': '/prod',
                                    'accountId': '420988533524', 'protocol': 'HTTP/1.1', 'stage': 'prod',
                                    'domainPrefix': 'cj8reit303', 'requestTimeEpoch': 1758143857805,
                                    'requestId': 'ac5818a8-6ff2-47ad-8710-066b80565d03',
                                    'identity': {'cognitoIdentityPoolId': None, 'accountId': None,
                                                 'cognitoIdentityId': None, 'caller': None,
                                                 'sourceIp': '143.105.18.199', 'principalOrgId': None,
                                                 'accessKey': None, 'cognitoAuthenticationType': None,
                                                 'cognitoAuthenticationProvider': None, 'userArn': None,
                                                 'userAgent': 'PostmanRuntime/7.45.0', 'user': None},
                                    'domainName': 'cj8reit303.execute-api.us-east-1.amazonaws.com',
                                    'deploymentId': '6kt59v', 'apiId': 'cj8reit303'}}
        result = function_handler(event, {})
        print(json.dumps(result, cls=DecimalEncoder))
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** tb_lineno: {}".format(exc_traceback.tb_lineno))
        print(traceback.format_exception(exc_type, exc_value, exc_traceback))
