import os
import traceback
import boto3
import sys
import json

# boto3.setup_default_session(profile_name="batrabajo", region_name="us-west-2")
os.environ["ACUITY_USER_ID"] = "31532355"
os.environ["ACUITY_API_KEY"] = "f1d28177592296ae44d57cd84b3d3c5c"
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
        event = {'resource': '/register', 'path': '/register', 'httpMethod': 'POST',
                 'headers': {'Accept': 'application/json', 'Accept-Encoding': 'gzip',
                             'Authorization': 'Bearer eyJraWQiOiIrWlFsMWo5V255VWxRRU5tSXljd0NSYXVDRzNYQzd1NmpcL1FLR1VWVzNLUT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI1ODExMDNlMC1iMGIxLTcwMmQtYWM0MC1lYmMxOWI5M2Q3NzMiLCJiaXJ0aGRhdGUiOiIwMVwvMDhcLzIwMDMiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtd2VzdC0yLmFtYXpvbmF3cy5jb21cL3VzLXdlc3QtMl9aSzZwMDVDRVoiLCJjb2duaXRvOnVzZXJuYW1lIjoiNTgxMTAzZTAtYjBiMS03MDJkLWFjNDAtZWJjMTliOTNkNzczIiwib3JpZ2luX2p0aSI6ImVmZjkyMGVkLTg4OWYtNDRkNy1iMjFlLTA2ZjBiZGVmNzQxMSIsImF1ZCI6IjdjMzFwdHBqaW9yYmI1dG40YzBoYzFkc3MyIiwiZXZlbnRfaWQiOiI2MDUyMjI3OC03ZjFmLTQ1ODEtYTgxMS1lMGM1NjA4ZGFiMzciLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTc1NzYyODE1MiwibmFtZSI6Ik1hbnVlbCIsInBob25lX251bWJlciI6Iis1MjgxMjg2OTY4NTIiLCJleHAiOjE3NTc2NDE0OTgsImlhdCI6MTc1NzYzNzg5OCwiZmFtaWx5X25hbWUiOiJDYW1hY2hvIiwianRpIjoiNmI3ZGQ2ODktOTc5OC00MDM1LTk0ODctYjE5NGNmZjU2YTAzIn0.BBwpnQ1bb3ssvdy5-e7ZP3_GV9r2wnFklODyVB7wPpFZvitGCdC5-cUbgDIUh2iQ5_NS4O8dkpFK4msoa3W5wOxANQt1M8bVPxmmag3COrXi-FGgSbnwkVvtmIkTcFgKcO2o6lXqRrkq1pcaLQZYfUsx-7MqhRHeCPt5aZ3fiqaqpvm2RGxVADQrf84gioT_O-OAyFYLYMfSn-KLNLDZjtfC1G1nUuxMruNLVtk7jAmdMLWEvmRiSnp5ufTk72_TtfTn7ahCRFUlX4p32d2CIZIl3jccylGvlxM2ptYcBWdU91OIJCPjYIhl7fPUZRHMBAsVLPgW0VnNRUlaoRdayw',
                             'CloudFront-Forwarded-Proto': 'https', 'CloudFront-Is-Desktop-Viewer': 'true',
                             'CloudFront-Is-Mobile-Viewer': 'false', 'CloudFront-Is-SmartTV-Viewer': 'false',
                             'CloudFront-Is-Tablet-Viewer': 'false', 'CloudFront-Viewer-ASN': '13999',
                             'CloudFront-Viewer-Country': 'MX', 'content-type': 'application/json; charset=utf-8',
                             'Host': '1a68wjdrn2.execute-api.us-west-2.amazonaws.com',
                             'User-Agent': 'Dart/3.8 (dart:io)',
                             'Via': '1.1 43816d50fff35ee328edb5ad571aa7f4.cloudfront.net (CloudFront)',
                             'X-Amz-Cf-Id': '24R8POoC0pfPmD5pG9cdbRILyMutproUUmWAqxrhxCLN0gnXL0o3gw==',
                             'X-Amzn-Trace-Id': 'Root=1-68c36d0c-7206c3be31c41faf6d9b480c',
                             'X-Forwarded-For': '177.227.58.104, 18.68.36.15', 'X-Forwarded-Port': '443',
                             'X-Forwarded-Proto': 'https'},
                 'multiValueHeaders': {'Accept': ['application/json'], 'Accept-Encoding': ['gzip'], 'Authorization': [
                     'Bearer eyJraWQiOiIrWlFsMWo5V255VWxRRU5tSXljd0NSYXVDRzNYQzd1NmpcL1FLR1VWVzNLUT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI1ODExMDNlMC1iMGIxLTcwMmQtYWM0MC1lYmMxOWI5M2Q3NzMiLCJiaXJ0aGRhdGUiOiIwMVwvMDhcLzIwMDMiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtd2VzdC0yLmFtYXpvbmF3cy5jb21cL3VzLXdlc3QtMl9aSzZwMDVDRVoiLCJjb2duaXRvOnVzZXJuYW1lIjoiNTgxMTAzZTAtYjBiMS03MDJkLWFjNDAtZWJjMTliOTNkNzczIiwib3JpZ2luX2p0aSI6ImVmZjkyMGVkLTg4OWYtNDRkNy1iMjFlLTA2ZjBiZGVmNzQxMSIsImF1ZCI6IjdjMzFwdHBqaW9yYmI1dG40YzBoYzFkc3MyIiwiZXZlbnRfaWQiOiI2MDUyMjI3OC03ZjFmLTQ1ODEtYTgxMS1lMGM1NjA4ZGFiMzciLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTc1NzYyODE1MiwibmFtZSI6Ik1hbnVlbCIsInBob25lX251bWJlciI6Iis1MjgxMjg2OTY4NTIiLCJleHAiOjE3NTc2NDE0OTgsImlhdCI6MTc1NzYzNzg5OCwiZmFtaWx5X25hbWUiOiJDYW1hY2hvIiwianRpIjoiNmI3ZGQ2ODktOTc5OC00MDM1LTk0ODctYjE5NGNmZjU2YTAzIn0.BBwpnQ1bb3ssvdy5-e7ZP3_GV9r2wnFklODyVB7wPpFZvitGCdC5-cUbgDIUh2iQ5_NS4O8dkpFK4msoa3W5wOxANQt1M8bVPxmmag3COrXi-FGgSbnwkVvtmIkTcFgKcO2o6lXqRrkq1pcaLQZYfUsx-7MqhRHeCPt5aZ3fiqaqpvm2RGxVADQrf84gioT_O-OAyFYLYMfSn-KLNLDZjtfC1G1nUuxMruNLVtk7jAmdMLWEvmRiSnp5ufTk72_TtfTn7ahCRFUlX4p32d2CIZIl3jccylGvlxM2ptYcBWdU91OIJCPjYIhl7fPUZRHMBAsVLPgW0VnNRUlaoRdayw'],
                                       'CloudFront-Forwarded-Proto': ['https'],
                                       'CloudFront-Is-Desktop-Viewer': ['true'],
                                       'CloudFront-Is-Mobile-Viewer': ['false'],
                                       'CloudFront-Is-SmartTV-Viewer': ['false'],
                                       'CloudFront-Is-Tablet-Viewer': ['false'], 'CloudFront-Viewer-ASN': ['13999'],
                                       'CloudFront-Viewer-Country': ['MX'],
                                       'content-type': ['application/json; charset=utf-8'],
                                       'Host': ['1a68wjdrn2.execute-api.us-west-2.amazonaws.com'],
                                       'User-Agent': ['Dart/3.8 (dart:io)'],
                                       'Via': ['1.1 43816d50fff35ee328edb5ad571aa7f4.cloudfront.net (CloudFront)'],
                                       'X-Amz-Cf-Id': ['24R8POoC0pfPmD5pG9cdbRILyMutproUUmWAqxrhxCLN0gnXL0o3gw=='],
                                       'X-Amzn-Trace-Id': ['Root=1-68c36d0c-7206c3be31c41faf6d9b480c'],
                                       'X-Forwarded-For': ['177.227.58.104, 18.68.36.15'], 'X-Forwarded-Port': ['443'],
                                       'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None,
                 'multiValueQueryStringParameters': None, 'pathParameters': None, 'stageVariables': None,
                 'requestContext': {'resourceId': '39pplo', 'authorizer': {
                     'claims': {'sub': '581103e0-b0b1-702d-ac40-ebc19b93d773', 'birthdate': '01/08/2003',
                                'iss': 'https://cognito-idp.us-west-2.amazonaws.com/us-west-2_ZK6p05CEZ',
                                'cognito:username': '581103e0-b0b1-702d-ac40-ebc19b93d773',
                                'origin_jti': 'eff920ed-889f-44d7-b21e-06f0bdef7411',
                                'aud': '7c31ptpjiorbb5tn4c0hc1dss2', 'event_id': '60522278-7f1f-4581-a811-e0c5608dab37',
                                'token_use': 'id', 'auth_time': '1757628152', 'name': 'Manuel',
                                'phone_number': '+528128696852', 'exp': 'Fri Sep 12 01:44:58 UTC 2025',
                                'iat': 'Fri Sep 12 00:44:58 UTC 2025', 'family_name': 'Camacho',
                                'jti': '6b7dd689-9798-4035-9487-b194cff56a03'}}, 'resourcePath': '/register',
                                    'httpMethod': 'POST', 'extendedRequestId': 'Qw36EEIEvHcEFJg=',
                                    'requestTime': '12/Sep/2025:00:45:00 +0000', 'path': '/prod/register',
                                    'accountId': '501930762946', 'protocol': 'HTTP/1.1', 'stage': 'prod',
                                    'domainPrefix': '1a68wjdrn2', 'requestTimeEpoch': 1757637900818,
                                    'requestId': '1c06c9f8-34a7-42ef-b7e3-0afcfbfefe05',
                                    'identity': {'cognitoIdentityPoolId': None, 'accountId': None,
                                                 'cognitoIdentityId': None, 'caller': None,
                                                 'sourceIp': '177.227.58.104', 'principalOrgId': None,
                                                 'accessKey': None, 'cognitoAuthenticationType': None,
                                                 'cognitoAuthenticationProvider': None, 'userArn': None,
                                                 'userAgent': 'Dart/3.8 (dart:io)', 'user': None},
                                    'domainName': '1a68wjdrn2.execute-api.us-west-2.amazonaws.com',
                                    'deploymentId': '8khq6p', 'apiId': '1a68wjdrn2'},
                 'body': json.dumps(body, cls=DecimalEncoder),
                 'isBase64Encoded': False}
        result = function_handler(event, {})
        print(json.dumps(result, cls=DecimalEncoder))
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** tb_lineno: {}".format(exc_traceback.tb_lineno))
        print(traceback.format_exception(exc_type, exc_value, exc_traceback))
