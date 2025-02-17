"""AWS SAM CLI Reference Resolver package."""
from pathlib import Path

from aws_cdk import cx_api

__version__ = "0.1.0"


def hello() -> str:
    """Return a friendly greeting."""
    return "Hello from AWS SAM CLI RefSolver!"


def load_assembly(cdk_out_dir: Path) -> cx_api.CloudAssembly:
    """Load CDK cloud assembly from the given output directory.
    
    Args:
        cdk_out_dir: Path to the CDK output directory containing assembly.json
        
    Returns:
        The loaded CloudAssembly object
    """
    return cx_api.CloudAssembly(cdk_out_dir)
