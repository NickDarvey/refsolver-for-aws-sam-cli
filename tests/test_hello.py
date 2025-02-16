"""Test cases for hello function."""
from pathlib import Path

import pytest
from aws_sam_cli_refsolver import hello


def test_hello():
    """Test hello function returns expected greeting."""
    assert hello() == "Hello from AWS SAM CLI RefSolver!"


def test_cdk_synth(cdk_out_dir: Path):
    """Test CDK synthesis produces output files."""
    assert cdk_out_dir.exists()
    assert any(cdk_out_dir.glob("*.template.json"))
