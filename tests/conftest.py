"""Test fixtures for AWS SAM CLI RefSolver."""
import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import boto3
import pytest
from aws_cdk import cx_api


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

@pytest.fixture
def session(request) -> boto3.Session:
    """Provide either a mocked or real boto3 session based on --integration flag."""
    if request.config.getoption("--integration"):
        return boto3.Session()
        
    mock_session = MagicMock()
    mock_client = MagicMock()
    mock_client.describe_stack_resource.return_value = {
        'StackResourceDetail': {
            'PhysicalResourceId': 'mock-resource-id'
        }
    }
    
    # Configure the mock session to return our mock client
    mock_session.client.return_value = mock_client
    return mock_session
