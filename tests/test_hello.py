"""Test cases for hello function."""
from pathlib import Path

import pytest
from aws_cdk import cx_api
from aws_sam_cli_refsolver import hello, load_assembly


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
    assert "ExampleStack" in [stack.stack_name for stack in cdk_assembly.stacks]
