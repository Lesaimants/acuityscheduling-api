from aws_cdk import Stack, aws_cognito as _cognito
from constructs import Construct

from project.api_gateway import ApiGateway
from project.lambdas import Lambdas
from project.permissions import Permissions
from project.tables import Tables


class ProjectStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        permissions = Permissions(
            self,
            f"{construct_id}-permissions",
            self.account,
            self.region,
        )

        tables = Tables(self, f"{construct_id}-tables")

        lambdas = Lambdas(
            self,
            f"{construct_id}-lambdas",
            tables,
            permissions,
            config,
        )

        rest_api = ApiGateway(self, f"{construct_id}-api-gateway", lambdas)

        self.api = rest_api.api
