"""Test cases for hello function."""
from pathlib import Path

import pytest
from aws_cdk import cx_api
from aws_sam_cli_refsolver import (
    hello,
    load_assembly,
    find_resource,
    resolve_ref,
    extract_lambda_function_environment_vars,
    extract_ecs_task_definition_environment_vars,
)


def test_hello():
    """Test hello function returns expected greeting."""
    assert hello() == "Hello from AWS SAM CLI RefSolver!"


def test_cdk_synth(cdk_out: Path):
    """Test CDK synthesis produces output files."""
    assert cdk_out.exists()
    assert any(cdk_out.glob("*.template.json"))


def test_load_assembly(cdk_out: Path):
    """Test loading CDK assembly."""
    assembly = load_assembly(cdk_out)
    assert assembly is not None
    assert len(assembly.stacks) > 0
    assert "ExampleStack" in [stack.stack_name for stack in assembly.stacks]


def test_extract_lambda_function_environment_vars(cdk_out: Path):
    """Test extracting environment variables from Lambda function."""
    assembly = load_assembly(cdk_out)
    
    # Test with wrong resource type
    table = find_resource(assembly, "ExampleTable", "AWS::DynamoDB::Table")
    with pytest.raises(ValueError, match="must be of type AWS::Lambda::Function"):
        extract_lambda_function_environment_vars(table)
    """Test extracting environment variables from Lambda function."""
    assembly = load_assembly(cdk_out)
    
    # Find the Lambda function
    function = find_resource(assembly, "ExampleFunction", "AWS::Lambda::Function")
    assert function is not None
    
    # Extract environment variables
    env_vars = extract_lambda_function_environment_vars(function)
    assert env_vars is not None
    assert "BUCKET_NAME" in env_vars
    assert "TABLE_NAME" in env_vars
    assert env_vars["BUCKET_NAME"] == {"Ref": "ExampleBucketDC717CF4"}
    assert env_vars["TABLE_NAME"] == {"Ref": "ExampleTable114D508F"}


def test_extract_ecs_task_definition_environment_vars(cdk_out: Path):
    """Test extracting environment variables from task definition."""
    assembly = load_assembly(cdk_out)
    
    # Test with wrong resource type
    table = find_resource(assembly, "ExampleTable", "AWS::DynamoDB::Table")
    with pytest.raises(ValueError, match="must be of type AWS::ECS::TaskDefinition"):
        extract_ecs_task_definition_environment_vars(table)
    """Test extracting environment variables from task definition."""
    assembly = load_assembly(cdk_out)
    
    # Find the task definition
    task_def = find_resource(assembly, "ExampleFargateService", "AWS::ECS::TaskDefinition")
    assert task_def is not None
    
    # Extract environment variables
    env_vars = extract_ecs_task_definition_environment_vars(task_def)
    assert env_vars is not None
    assert "BUCKET_NAME" in env_vars
    assert "TABLE_NAME" in env_vars
    assert env_vars["BUCKET_NAME"] == {"Ref": "ExampleBucketDC717CF4"}
    assert env_vars["TABLE_NAME"] == {"Ref": "ExampleTable114D508F"}


def test_resolve_ref(mocker, cdk_out: Path):
    """Test resolving CloudFormation refs to physical IDs."""
    # Load assembly and find a resource
    assembly = load_assembly(cdk_out)
    result = find_resource(assembly, "ExampleBucket", "AWS::S3::Bucket")
    assert result is not None
    bucket, stack = result
    
    # Mock the CloudFormation client
    mock_cfn = mocker.patch('boto3.client')
    mock_cfn.return_value.describe_stack_resource.return_value = {
        'StackResourceDetail': {
            'PhysicalResourceId': 'my-stack-bucket-u4d24n1mpl0y'
        }
    }
    
    # Test with valid dict ref
    ref = {'Ref': 'ExampleBucket'}
    assert resolve_ref(stack, ref) == 'my-stack-bucket-u4d24n1mpl0y'
    
    # Test invalid inputs
    with pytest.raises(TypeError, match="ref must be a dict"):
        resolve_ref(stack, 'ExampleBucket')
    
    with pytest.raises(ValueError, match="ref dict must contain 'Ref' key"):
        resolve_ref(stack, {})
    
    with pytest.raises(ValueError, match="ref\\['Ref'\\] must be a non-empty string"):
        resolve_ref(stack, {'Ref': ''})
    
    # Verify correct API call
    mock_cfn.return_value.describe_stack_resource.assert_called_with(
        StackName='ExampleStack',
        LogicalResourceId='ExampleBucket'
    )


def test_find_resource(cdk_out: Path):
    """Test finding resources by CDK logical ID."""
    assembly = load_assembly(cdk_out)
    
    # Find the Lambda function
    result = find_resource(assembly, "ExampleFunction", "AWS::Lambda::Function")
    assert result is not None
    function, stack = result
    assert function["Type"] == "AWS::Lambda::Function"
    assert stack.stack_name == "ExampleStack"
    
    # Find the DynamoDB table
    result = find_resource(assembly, "ExampleTable", "AWS::DynamoDB::Table")
    assert result is not None
    table, stack = result
    assert table["Type"] == "AWS::DynamoDB::Table"
    assert stack.stack_name == "ExampleStack"
    
    # Test non-existent resource
    missing = find_resource(assembly, "NonExistentResource", "AWS::Lambda::Function")
    assert missing is None
