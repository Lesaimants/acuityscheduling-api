from aws_cdk import (
    RemovalPolicy,
    aws_dynamodb as _dynamodb,
)
from constructs import Construct


class Tables(Construct):
    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        self.users_links = self.create_table(
            f"{scope.node.id}-user-links", "customerId", "profile"
        )

    def create_table(self, table_name, pk, sk=None, time_to_live_attribute=None):
        if sk is not None:
            sk = _dynamodb.Attribute(name=sk, type=_dynamodb.AttributeType.STRING)
        return _dynamodb.Table(
            self,
            table_name,
            table_name=table_name,
            partition_key=_dynamodb.Attribute(
                name=pk, type=_dynamodb.AttributeType.STRING
            ),
            sort_key=sk,
            billing_mode=_dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            stream=_dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            time_to_live_attribute=time_to_live_attribute,
        )
