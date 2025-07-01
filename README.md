# Refsolver for AWS SAM CLI

A Python library that enables **hybrid development** with AWS SAM CLI. Run your Lambda functions locally with (full breakpoint debugging) while they interact with real AWS resources in your sandbox account.

This library resolves CloudFormation references like `{"Ref": "MyBucket"}` to actual AWS resource names, allowing you to:

- **Test against real AWS behavior**: no emulation, no approximation, just real AWS services
- **Skip manual resource naming**: no need to hardcode physical resource names or manage environment configs
- **Preserve CDK abstractions**: keep using logical IDs while connecting to actual deployed infrastructure
- **Enable true hybrid development**: local code execution with cloud resource interactions

## Installation

```bash
pip install aws-sam-cli-refsolver
```

## Usage

### Basic Workflow: Local Lambda + Real AWS Resources

```python
import boto3
from pathlib import Path
from aws_sam_cli_refsolver import load_assembly, find_resource, resolve_ref

# 1. Load your CDK assembly (after cdk synth)
assembly = load_assembly(Path("cdk.out"))

# 2. Find the Lambda function definition
function_resource = find_resource(assembly, "MyDataProcessor", "AWS::Lambda::Function")
resource_def, stack, cfn_logical_id = function_resource

# 3. Get the Lambda's environment variables (contains refs to other resources)
env_vars = resource_def['Properties']['Environment']['Variables']
# env_vars might be: {'BUCKET_NAME': {'Ref': 'MyBucketABC123'}, 'TABLE_NAME': {'Ref': 'MyTableXYZ789'}}

# 4. Resolve CloudFormation refs to actual AWS resource names
session = boto3.Session(profile_name='sandbox')
resolved_env = {}
for key, value in env_vars.items():
    if isinstance(value, dict) and 'Ref' in value:
        # Resolve {"Ref": "MyBucketABC123"} to actual bucket name
        resolved_env[key] = resolve_ref(stack, session, value)
    else:
        resolved_env[key] = value

print(resolved_env)
# Output: {'BUCKET_NAME': 'mystack-mybucket-a1b2c3d4e5f6', 'TABLE_NAME': 'MyStack-MyTable-X7Y8Z9'}

# 5. Use these resolved values with sam local invoke
# Now your local Lambda can connect to real AWS resources!
```

### Real Example: Lambda Reading from S3

Suppose you have a CDK stack with a Lambda that processes files from S3:

```python
# Your CDK code creates:
# - Lambda function "FileProcessor" 
# - S3 bucket "DocumentBucket"
# - Lambda has environment variable BUCKET_NAME = {"Ref": "DocumentBucket"}

# After CDK synthesis, resolve the actual bucket name:
assembly = load_assembly(Path("cdk.out"))
function_resource = find_resource(assembly, "FileProcessor", "AWS::Lambda::Function")

if function_resource:
    resource_def, stack, _ = function_resource
    bucket_ref = resource_def['Properties']['Environment']['Variables']['BUCKET_NAME']
    # bucket_ref = {"Ref": "DocumentBucketF4E5D6C7"}
    
    session = boto3.Session(profile_name='sandbox')
    actual_bucket_name = resolve_ref(stack, session, bucket_ref)
    # actual_bucket_name = "mystack-documentbucket-a1b2c3d4e5f6"
    
    # Now run your Lambda locally with the real bucket name:
    # sam local invoke FileProcessor -e event.json --env-vars env.json
    # where env.json contains: {"FileProcessor": {"BUCKET_NAME": "mystack-documentbucket-a1b2c3d4e5f6"}}
```

### Extracting Environment Variables

```python
from aws_sam_cli_refsolver import extract_lambda_function_environment_vars

# Extract all environment variables from a Lambda function
function_resource = find_resource(assembly, "MyFunction", "AWS::Lambda::Function")
if function_resource:
    env_vars = extract_lambda_function_environment_vars(function_resource)
    print(env_vars)
    # Output: {
    #   'BUCKET_NAME': {'Ref': 'MyBucketABC123'},
    #   'TABLE_NAME': {'Ref': 'MyTableXYZ789'},
    #   'API_URL': 'https://api.example.com'  # Non-ref values passed through
    # }
```

### Integration with SAM CLI

Typical development workflow:

1. **Deploy infrastructure**: `cdk deploy` to create S3 buckets, DynamoDB tables, etc.
2. **Synthesize locally**: `cdk synth` to generate CloudFormation templates
3. **Resolve references**: Use this library to get real AWS resource names
4. **Run locally**: `sam local invoke` with resolved environment variables
5. **Develop iteratively**: Make code changes and test against real AWS resources

```bash
# 1. Deploy your CDK stack to create AWS resources
cdk deploy --profile sandbox

# 2. Use this library to resolve refs and create env.json
python resolve_refs.py  # Your script using this library

# 3. Run Lambda locally with real AWS resource names
sam local invoke MyFunction --env-vars env.json --profile sandbox
```

## Development

This project uses Poetry for dependency management and Ruff for code quality.

### Setup
```bash
# Install dependencies
poetry install --with dev
```

### Code Quality
```bash
# Format code
poetry run ruff format .

# Lint code
poetry run ruff check .

# Fix linting issues automatically
poetry run ruff check . --fix
```

### Testing
```bash
# Run tests
poetry run pytest

# Run tests with verbose output
poetry run pytest -v

# Run integration tests (requires AWS credentials configured, such as SSO)
AWS_PROFILE=sandbox poetry run pytest --integration

# Run specific test file
poetry run pytest tests/test_hello.py

# Run tests with coverage
poetry run pytest --cov=aws_sam_cli_refsolver
```

## API Reference

### Core Functions

- **`load_assembly(cdk_out_dir: Path) -> CDKAssembly`** - Load CDK cloud assembly from synthesis output
- **`find_resource(assembly, logical_id: str, resource_type: str) -> Optional[tuple]`** - Find resources by CDK construct ID
- **`resolve_ref(stack, session: boto3.Session, ref: dict) -> str`** - Resolve CloudFormation refs to physical AWS resource IDs
- **`extract_lambda_function_environment_vars(resource_tuple) -> Dict[str, Any]`** - Extract Lambda environment variables
- **`extract_ecs_task_definition_environment_vars(resource_tuple) -> Dict[str, Any]`** - Extract ECS task environment variables

### Build and Package
```bash
# Build the package
poetry build

# Install the package locally for testing
pip install -e .
```

## License

MIT License - see LICENSE file for details.

