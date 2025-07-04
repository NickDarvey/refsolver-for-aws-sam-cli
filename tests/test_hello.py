"""Test cases for hello function."""
from pathlib import Path

import boto3
import pytest

from aws_sam_cli_refsolver import (
    load_assembly,
    find_resource,
    resolve_ref,
    extract_lambda_function_environment_vars,
    extract_ecs_task_definition_environment_vars,
    generate_sam_env_vars,
)


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


def test_resolve_ref(cdk_out: Path, session: boto3.Session):
    """Test resolving CloudFormation refs to physical IDs."""
    # Load assembly and find a resource
    assembly = load_assembly(cdk_out)
    result = find_resource(assembly, "ExampleBucket", "AWS::S3::Bucket")
    assert result is not None
    _, stack, logical_id = result
    
    physical_id = resolve_ref(stack, session, {'Ref': logical_id})
    
    # Verify we got a valid physical ID
    assert isinstance(physical_id, str)
    assert physical_id

    # Test invalid inputs
    with pytest.raises(TypeError, match="ref must be a dict"):
        resolve_ref(stack, session, 'ExampleBucket')
    
    with pytest.raises(ValueError, match="ref dict must contain 'Ref' key"):
        resolve_ref(stack, session, {})
    
    with pytest.raises(ValueError, match="ref\\['Ref'\\] must be a non-empty string"):
        resolve_ref(stack, session, {'Ref': ''})


def test_find_resource(cdk_out: Path):
    """Test finding resources by CDK logical ID."""
    assembly = load_assembly(cdk_out)
    
    # Find the Lambda function
    result = find_resource(assembly, "ExampleFunction", "AWS::Lambda::Function")
    assert result is not None
    function_def, stack, function_id = result
    assert function_id.startswith("ExampleFunction")
    assert function_def["Type"] == "AWS::Lambda::Function"
    assert stack.stack_name == "ExampleStack"
    
    # Find the DynamoDB table
    result = find_resource(assembly, "ExampleTable", "AWS::DynamoDB::Table")
    assert result is not None
    table_def, stack, table_id = result
    assert table_id.startswith("ExampleTable")
    assert table_def["Type"] == "AWS::DynamoDB::Table"
    assert stack.stack_name == "ExampleStack"
    
    # Test non-existent resource
    missing = find_resource(assembly, "NonExistentResource", "AWS::Lambda::Function")
    assert missing is None


def test_generate_sam_env_vars_success(cdk_out: Path, session: boto3.Session):
    """Test generating SAM CLI environment variables for valid function."""
    # Arrange
    assembly = load_assembly(cdk_out)
    
    # Act
    env_vars = generate_sam_env_vars(assembly, session, "ExampleFunction")
    
    # Assert
    assert isinstance(env_vars, dict)
    assert "ExampleFunction" in env_vars
    function_env = env_vars["ExampleFunction"]
    assert "BUCKET_NAME" in function_env
    assert "TABLE_NAME" in function_env
    assert isinstance(function_env["BUCKET_NAME"], str)
    assert isinstance(function_env["TABLE_NAME"], str)
    assert function_env["BUCKET_NAME"]
    assert function_env["TABLE_NAME"]


def test_generate_sam_env_vars_function_not_found(cdk_out: Path, session: boto3.Session):
    """Test error when Lambda function does not exist."""
    # Arrange
    assembly = load_assembly(cdk_out)
    
    # Act & Assert
    with pytest.raises(ValueError, match="Lambda function 'NonExistentFunction' not found"):
        generate_sam_env_vars(assembly, session, "NonExistentFunction")
