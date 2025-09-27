from aws_cdk import (
    aws_apigateway as _apigw,
    Duration,
)
from constructs import Construct

from project.lambdas import Lambdas


class ApiGateway(Construct):

    def __init__(self, scope: Construct, _id: str, lambdas: Lambdas):
        super().__init__(scope, _id)

        rest_api = _apigw.RestApi(
            self,
            f"{scope.node.id}-api",
            rest_api_name=f"{scope.node.id}-api",
            default_cors_preflight_options=_apigw.CorsOptions(
                status_code=200,
                allow_origins=_apigw.Cors.ALL_ORIGINS,
                allow_methods=_apigw.Cors.ALL_METHODS,
            ),
        )

        self.api = rest_api

        self.auth = _apigw.RequestAuthorizer(
            self, 'authorizer',
            identity_sources=['method.request.header.authorization'],
            handler=lambdas.authorizer,
            results_cache_ttl=Duration.seconds(1)
        )

        # /availability
        availability_resource = self.api.root.add_resource("availability")
        # /user-appointments
        user_appointments_resource = self.api.root.add_resource("user-appointments")
        # /cancel
        cancel_resource = self.api.root.add_resource("cancel")
        # /appointment-types
        appointment_types_resource = self.api.root.add_resource("appointment-types")
        # /customer-token
        customer_token_resource = self.api.root.add_resource("customer-token")

        self.add_method("POST", self.api.root, lambdas.create_appointment)
        self.add_method("PUT", self.api.root, lambdas.edit_appointment)
        self.add_method("GET", self.api.root, lambdas.get_calendars)
        self.add_method("POST", availability_resource, lambdas.get_appointments)
        self.add_method("POST", user_appointments_resource, lambdas.get_user_appointment)
        self.add_method("POST", cancel_resource, lambdas.cancel_appointment)
        self.add_method("GET", appointment_types_resource, lambdas.get_appointment_types)
        self.add_method("POST", customer_token_resource, lambdas.customer_token, auth=False)

    def add_method(self, method, resource: _apigw.Resource, function_name, auth=True):
        lambda_integration = _apigw.LambdaIntegration(
            function_name,
            proxy=True,
            passthrough_behavior=_apigw.PassthroughBehavior.NEVER,
        )
        params = {
            "http_method": method,
            "integration": lambda_integration,
            "method_responses": [
                _apigw.MethodResponse(
                    status_code="200",
                )
            ],
        }
        if auth:
            params["authorization_type"] = _apigw.AuthorizationType.CUSTOM
            params["authorizer"] = self.auth
        resource.add_method(**params)
