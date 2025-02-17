from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_lambda as lambda_,
    aws_iam as iam,
)
from constructs import Construct

class ExampleStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create shared resources
        example_bucket = s3.Bucket(self, "ExampleBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        example_table = dynamodb.Table(self, "ExampleTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create VPC for Fargate
        vpc = ec2.Vpc(self, "ExampleVPC",
            max_azs=2
        )

        # Create Fargate Service
        cluster = ecs.Cluster(self, "ExampleCluster", vpc=vpc)
        
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "ExampleFargateService",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset("example-container"),
                environment={
                    "BUCKET_NAME": example_bucket.bucket_name,
                    "TABLE_NAME": example_table.table_name
                }
            )
        )

        # Grant Fargate permissions
        example_bucket.grant_read_write(fargate_service.task_definition.task_role)
        example_table.grant_read_write_data(fargate_service.task_definition.task_role)

        # Create Lambda function
        example_function = lambda_.Function(self, "ExampleFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={
                "BUCKET_NAME": example_bucket.bucket_name,
                "TABLE_NAME": example_table.table_name
            }
        )

        # Grant Lambda permissions
        example_bucket.grant_read_write(example_function)
        example_table.grant_read_write_data(example_function)
