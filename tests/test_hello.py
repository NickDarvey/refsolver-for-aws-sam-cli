"""Test cases for hello function."""
from pathlib import Path

import pytest
from aws_sam_cli_refsolver import hello


def test_hello():
    """Test hello function returns expected greeting."""
    assert hello() == "Hello from AWS SAM CLI RefSolver!"


def test_cdk_synth(cdk_out: Path):
    """Test CDK synthesis produces output files."""
    assert cdk_out.exists()
    assert any(cdk_out.glob("*.template.json"))
