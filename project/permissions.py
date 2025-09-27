from aws_cdk import (
    aws_iam as _iam,
)
from constructs import Construct


class Permissions(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        account: str,
        region: str,
    ) -> None:
        """
        Initializes the Permissions object.

        Args:
            scope (Construct): The parent Construct.
            construct_id (str): The ID of the Construct.
            account (str): The AWS account ID.
            region (str): The AWS region.

        Returns:
            None
        """
        super().__init__(scope, construct_id)

        dynamodb_policy = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            actions=[
                "dynamodb:GetItem",
                "dynamodb:Query",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
            ],
            resources=[
                f"arn:aws:dynamodb:{region}:{account}:table/{scope.node.id}*",
            ],
        )

        dynamodb_index_policy = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            actions=[
                "dynamodb:Query",
            ],
            resources=[
                f"arn:aws:dynamodb:{region}:{account}:table/{scope.node.id}*/index/*",
            ],
        )

        dynamodb_stream_policy = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            actions=[
                "dynamodb:DescribeStream",
                "dynamodb:GetRecords",
                "dynamodb:GetShardIterator",
                "dynamodb:ListStreams",
            ],
            resources=[
                f"arn:aws:dynamodb:{region}:{account}:table/{scope.node.id}*/stream/*",
            ],
        )

        logs_policy = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            actions=[
                "logs:CreateLogStream",
                "logs:CreateLogGroup",
                "logs:PutLogEvents",
            ],
            resources=[
                f"arn:aws:logs:{region}:{account}:log-group:/aws/lambda/{scope.node.id}*:*",
                f"arn:aws:logs:{region}:{account}:log-group:/aws/lambda/{scope.node.id}*:*:*",
            ],
        )

        self.role = _iam.Role(
            scope,
            f"{scope.node.id}-lambda_role",
            assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        self.role.add_to_policy(dynamodb_policy)
        self.role.add_to_policy(dynamodb_index_policy)
        self.role.add_to_policy(dynamodb_stream_policy)
        self.role.add_to_policy(logs_policy)
