# Refsolver for AWS SAM CLI

A Python library for resolving CloudFormation Refs in AWS SAM CLI templates.

## Installation

```bash
pip install aws-sam-cli-refsolver
```

## Usage

```python
from aws_sam_cli_refsolver import hello

greeting = hello()
print(greeting)  # Outputs: Hello from AWS SAM CLI RefSolver!
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

### Build and Package
```bash
# Build the package
poetry build

# Install the package locally for testing
pip install -e .
```

## License

MIT License - see LICENSE file for details.

