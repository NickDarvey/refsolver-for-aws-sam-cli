"""Test fixtures for AWS SAM CLI RefSolver."""
import os
import subprocess
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def cdk_out(request) -> Path:
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

    return example_dir / out_dir
