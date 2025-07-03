"""Command-line interface for AWS SAM CLI Reference Resolver."""
import argparse
import json
import sys
from pathlib import Path

import boto3

from . import load_assembly, generate_sam_env_vars


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Generate SAM CLI environment variables with resolved CloudFormation references"
    )
    
    parser.add_argument(
        "--app",
        type=Path,
        required=True,
        help="Path to the CDK assembly directory (e.g., cdk.out)"
    )
    
    parser.add_argument(
        "--function-name",
        required=True,
        help="CDK logical ID of the Lambda function"
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (default: {function_name}.env.json)"
    )
    
    parser.add_argument(
        "--profile",
        help="AWS profile to use for resolving references"
    )
    
    args = parser.parse_args()
    
    # Set default output file if not provided
    if args.output is None:
        args.output = Path(f"{args.function_name}.env.json")
    
    try:
        # Load CDK assembly
        assembly = load_assembly(args.app)
        
        # Create boto3 session
        session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
        
        # Generate environment variables
        env_vars = generate_sam_env_vars(assembly, session, args.function_name)
        
        # Write to output file
        with open(args.output, 'w') as f:
            json.dump(env_vars, f, indent=2)
        
        print(f"Environment variables written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()