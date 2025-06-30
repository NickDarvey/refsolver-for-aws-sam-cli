"""Test fixtures for AWS SAM CLI RefSolver."""
import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, create_autospec

import boto3
import pytest

_EXAMPLE_DIR = Path(__file__).parent / "example"
_OUT_DIR = "cdk.out"

def _run_cdk(args: list[str]) -> Path:

    old_cwd = os.getcwd()
    os.chdir(_EXAMPLE_DIR)

    try:
        return subprocess.run(
            ["cdk"] + args,
            check=True,
            text=True,
        )
            
    finally:
        os.chdir(old_cwd)

def pytest_addoption(parser: pytest.Parser):
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

    _run_cdk(["synth", "--output", _OUT_DIR])
    return _EXAMPLE_DIR / _OUT_DIR


@pytest.fixture(scope="session")
def session(request: pytest.FixtureRequest) -> boto3.Session:
    """Provide either a mocked or real boto3 session based on --integration flag."""
    if request.config.getoption("--integration"):
        _run_cdk(["deploy", "--app", _OUT_DIR, "--require-approval", "never"])
        
        # Register cleanup to destroy stack after tests
        def cleanup():
            try:
                _run_cdk(["destroy", "--app", _OUT_DIR, "--require-approval", "never"])
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to destroy CDK stack: {e}")
        
        request.addfinalizer(cleanup)
        return boto3.Session()
        
    mock_session = create_autospec(boto3.Session)
    mock_client = MagicMock()
    mock_client.describe_stack_resource.return_value = {
        'StackResourceDetail': {
            'PhysicalResourceId': 'mock-resource-id'
        }
    }
    
    # Configure the mock session to return our mock client
    mock_session.client.return_value = mock_client
    return mock_session
