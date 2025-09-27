import os
from aws_cdk import (
    Duration,
    aws_lambda as _lambda,
    aws_iam as _iam,
    aws_logs as _logs,
    RemovalPolicy,
)
from constructs import Construct
from project.permissions import Permissions
from project.tables import Tables


class Lambdas(Construct):
    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            tables: Tables,
            permissions: Permissions,
            config: dict
    ) -> None:
        super().__init__(scope, construct_id)

        self.base_name = construct_id

        environment = {
            "USER_LINKS_TABLE": tables.users_links.table_name,
            "ACUITY_USER_ID": config["ACUITY_USER_ID"],
            "ACUITY_API_KEY": config["ACUITY_API_KEY"],
            "SHOPIFY_STORE_DOMAIN": config["SHOPIFY_STORE_DOMAIN"],
            "SHOPIFY_STOREFRONT_ACCESS_TOKEN": config["SHOPIFY_STOREFRONT_ACCESS_TOKEN"],
            "SHOPIFY_API_VERSION": config["SHOPIFY_API_VERSION"],
        }

        # Layer
        self.layer = _lambda.LayerVersion(
            self,
            f"{scope.node.id}-dependencies",
            code=_lambda.Code.from_asset("layers/dependencies"),
            compatible_runtimes=[
                _lambda.Runtime.PYTHON_3_12,
            ],
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.authorizer = self.create_function("authorizer", environment, config, permissions.role)
        self.get_calendars = self.create_function("get-calendars", environment, config, permissions.role)
        self.get_appointments = self.create_function("get-appointments", environment, config, permissions.role)
        self.get_user_appointment = self.create_function("get-user-appointment", environment, config, permissions.role)
        self.create_appointment = self.create_function("create-appointment", environment, config, permissions.role)
        self.edit_appointment = self.create_function("edit-appointment", environment, config, permissions.role)
        self.cancel_appointment = self.create_function("cancel-appointment", environment, config, permissions.role)
        self.get_appointment_types = self.create_function("get-appointment-types", environment, config, permissions.role)
        self.customer_token = self.create_function("customer-token", environment, config, permissions.role)

    def create_function(self, function_name: str, environment: dict, config: dict, role: _iam.Role, duration: int = 30):
        """
        Creates an AWS Lambda function with the specified properties and configurations.

        :param function_name: Name of the Lambda function
        :param environment: Dictionary containing Lambda function's environment variables
        :param config: Dictionary containing additional configuration settings, such as log retention
        :param role: IAM role assigned to the Lambda function
        :param duration: Timeout duration for the Lambda function execution in seconds; defaults to 30
        :return: The created AWS Lambda function object
        """
        function_lambda = _lambda.Function(
            self,
            f"{self.base_name}-{function_name}",
            function_name=f"{self.base_name}-{function_name}",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset(f"./lambdas/{function_name}"),
            handler="handler.function_handler",
            environment=environment,
            memory_size=128,
            timeout=Duration.seconds(duration),
            layers=[self.layer],
            role=role,
            log_retention=_logs.RetentionDays(config["LOG_RETENTION_TIME"]),
        )
        return function_lambda
