"""Test fixtures for AWS SAM CLI RefSolver."""
import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import boto3
import pytest
from aws_cdk import cx_api

@pytest.fixture(autouse=True)
def mock_boto3(monkeypatch):
    """Mock boto3 CloudFormation client for offline testing."""
    mock_client = MagicMock()
    mock_client.describe_stack_resource.return_value = {
        'StackResourceDetail': {
            'PhysicalResourceId': 'mock-resource-id'
        }
    }
    
    def mock_client_creator(*args, **kwargs):
        if args and args[0] == 'cloudformation':
            return mock_client
        return boto3.client(*args, **kwargs)
    
    monkeypatch.setattr(boto3, 'client', mock_client_creator)
    return mock_client

def pytest_addoption(parser):
    """Add integration test option to pytest."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests against AWS account"
    )

@pytest.fixture(scope="session")
def cdk_out() -> Path:
    """Synthesize the CDK app before running tests."""
    example_dir = Path(__file__).parent / "example"
    out_dir = "cdk.out"

    # Change to example directory since cdk synth expects to run there
    old_cwd = os.getcwd()
    os.chdir(example_dir)

    try:
        print("\nStarting CDK synthesis...")
        
        result = subprocess.run(
            ["cdk", "synth", "--output", out_dir],
            check=True,
            text=True,
        )
        
        print("CDK synthesis completed")
    finally:
        os.chdir(old_cwd)

    out_path = example_dir / out_dir
    return out_path
