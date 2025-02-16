"""Test cases for hello function."""
import pytest
from aws_sam_cli_refsolver import hello


def test_hello():
    """Test hello function returns expected greeting."""
    assert hello() == "Hello from AWS SAM CLI RefSolver!"
