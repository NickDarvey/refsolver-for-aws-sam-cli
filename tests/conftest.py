"""Test fixtures for AWS SAM CLI RefSolver."""
import os
import subprocess
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def example_dir() -> Path:
    """Get the example CDK app directory."""
    return Path(__file__).parent / "example"


@pytest.fixture(scope="session")
def cdk_out_dir(example_dir: Path) -> Path:
    """Get the CDK output directory."""
    return example_dir / "cdk.out"


@pytest.fixture(scope="session", autouse=True)
def synth_app(example_dir: Path, cdk_out_dir: Path):
    """Synthesize the CDK app before running tests."""
    # Change to example directory since cdk synth expects to run there
    old_cwd = os.getcwd()
    os.chdir(example_dir)
    
    try:
        subprocess.run(
            ["cdk", "synth"],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        os.chdir(old_cwd)
