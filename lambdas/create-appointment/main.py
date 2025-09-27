import os
import traceback
import boto3
import sys
import json

boto3.setup_default_session(profile_name="digicaster", region_name="us-east-1")
os.environ["ACUITY_USER_ID"] = "36965644"
os.environ["ACUITY_API_KEY"] = "12582f92e902ae1d3d28343b0bab84fc"
os.environ["SHOPIFY_STORE_DOMAIN"] = "les-aimants.myshopify.com"
os.environ["SHOPIFY_STOREFRONT_ACCESS_TOKEN"] = "495be658c9a93ba95807d1a826ef63ea"
os.environ["SHOPIFY_API_VERSION"] = "2024-07"
os.environ["USER_LINKS_TABLE"] = "AcuityAppointmentsStack-user-links"
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
        event = {'resource': '/', 'path': '/', 'httpMethod': 'POST',
                 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br',
                             'Authorization': 'Bearer c010dc2ec6f9ce58433071db957c4595',
                             'CloudFront-Forwarded-Proto': 'https', 'CloudFront-Is-Desktop-Viewer': 'true',
                             'CloudFront-Is-Mobile-Viewer': 'false', 'CloudFront-Is-SmartTV-Viewer': 'false',
                             'CloudFront-Is-Tablet-Viewer': 'false', 'CloudFront-Viewer-ASN': '14593',
                             'CloudFront-Viewer-Country': 'MX', 'Content-Type': 'application/json',
                             'Host': 'cj8reit303.execute-api.us-east-1.amazonaws.com',
                             'Postman-Token': '82de9682-fb06-42fa-b5e8-b1954d5a6fa8',
                             'User-Agent': 'PostmanRuntime/7.46.1',
                             'Via': '1.1 4969d3779d2434ea67cd63de6552e5a2.cloudfront.net (CloudFront)',
                             'X-Amz-Cf-Id': 'GpgBi02wy_s2NPfmiLlE75nLlhReQNKbX-rNhws7RVZOC_WxRRTLWA==',
                             'X-Amzn-Trace-Id': 'Root=1-68cb7b9b-3dd6cd7463b5af617dcdc074',
                             'X-Forwarded-For': '143.105.18.199, 15.158.230.73', 'X-Forwarded-Port': '443',
                             'X-Forwarded-Proto': 'https'},
                 'multiValueHeaders': {'Accept': ['*/*'], 'Accept-Encoding': ['gzip, deflate, br'],
                                       'Authorization': ['Bearer c010dc2ec6f9ce58433071db957c4595'],
                                       'CloudFront-Forwarded-Proto': ['https'],
                                       'CloudFront-Is-Desktop-Viewer': ['true'],
                                       'CloudFront-Is-Mobile-Viewer': ['false'],
                                       'CloudFront-Is-SmartTV-Viewer': ['false'],
                                       'CloudFront-Is-Tablet-Viewer': ['false'], 'CloudFront-Viewer-ASN': ['14593'],
                                       'CloudFront-Viewer-Country': ['MX'], 'Content-Type': ['application/json'],
                                       'Host': ['cj8reit303.execute-api.us-east-1.amazonaws.com'],
                                       'Postman-Token': ['82de9682-fb06-42fa-b5e8-b1954d5a6fa8'],
                                       'User-Agent': ['PostmanRuntime/7.46.1'],
                                       'Via': ['1.1 4969d3779d2434ea67cd63de6552e5a2.cloudfront.net (CloudFront)'],
                                       'X-Amz-Cf-Id': ['GpgBi02wy_s2NPfmiLlE75nLlhReQNKbX-rNhws7RVZOC_WxRRTLWA=='],
                                       'X-Amzn-Trace-Id': ['Root=1-68cb7b9b-3dd6cd7463b5af617dcdc074'],
                                       'X-Forwarded-For': ['143.105.18.199, 15.158.230.73'],
                                       'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']},
                 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': None,
                 'stageVariables': None, 'requestContext': {'resourceId': 'sa2t7axg87',
                                                            'authorizer': {'firstName': 'Jondalar',
                                                                           'lastName': 'Rodriguez Díaz',
                                                                           'shopifyCustomerId': '7788624150711',
                                                                           'phone': '+525580311366',
                                                                           'principalId': '7788624150711',
                                                                           'shopDomain': 'les-aimants.myshopify.com',
                                                                           'integrationLatency': 0,
                                                                           'shopifyCustomerGID': 'gid://shopify/Customer/7788624150711',
                                                                           'tokenType': 'shopify_customer_access_token',
                                                                           'email': 'jondalar59@gmail.com'},
                                                            'resourcePath': '/', 'httpMethod': 'POST',
                                                            'extendedRequestId': 'RFBATFrVoAMETzQ=',
                                                            'requestTime': '18/Sep/2025:03:25:15 +0000',
                                                            'path': '/prod/', 'accountId': '420988533524',
                                                            'protocol': 'HTTP/1.1', 'stage': 'prod',
                                                            'domainPrefix': 'cj8reit303',
                                                            'requestTimeEpoch': 1758165915165,
                                                            'requestId': '66cd64e0-f3c0-4a50-be6c-61d412b715cd',
                                                            'identity': {'cognitoIdentityPoolId': None,
                                                                         'accountId': None, 'cognitoIdentityId': None,
                                                                         'caller': None, 'sourceIp': '143.105.18.199',
                                                                         'principalOrgId': None, 'accessKey': None,
                                                                         'cognitoAuthenticationType': None,
                                                                         'cognitoAuthenticationProvider': None,
                                                                         'userArn': None,
                                                                         'userAgent': 'PostmanRuntime/7.46.1',
                                                                         'user': None},
                                                            'domainName': 'cj8reit303.execute-api.us-east-1.amazonaws.com',
                                                            'deploymentId': '6kt59v', 'apiId': 'cj8reit303'},
                 'body': '{\r\n    "datetime": "2025-09-19T15:10:00-0600",\r\n    "calendarID": "12760279",\r\n    "appointmentTypeID": "83538139"\r\n}',
                 'isBase64Encoded': False}
        result = function_handler(event, {})
        print(json.dumps(result, cls=DecimalEncoder))
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** tb_lineno: {}".format(exc_traceback.tb_lineno))
        print(traceback.format_exception(exc_type, exc_value, exc_traceback))
