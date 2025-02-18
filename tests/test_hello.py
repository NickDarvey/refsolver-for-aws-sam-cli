"""Test cases for hello function."""
from pathlib import Path

import pytest
from aws_cdk import cx_api
from aws_sam_cli_refsolver import hello, load_assembly, find_resource


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


def test_find_resource(cdk_out: Path):
    """Test finding resources by CDK logical ID."""
    assembly = load_assembly(cdk_out)
    
    # Find the Lambda function
    function = find_resource(assembly, "ExampleFunction")
    assert function is not None
    assert function["Type"] == "AWS::Lambda::Function"
    
    # Find the DynamoDB table
    table = find_resource(assembly, "ExampleTable")
    assert table is not None
    assert table["Type"] == "AWS::DynamoDB::Table"
    
    # Test non-existent resource
    missing = find_resource(assembly, "NonExistentResource")
    assert missing is None
