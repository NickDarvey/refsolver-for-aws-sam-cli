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

Setup:
```bash
# Install dependencies
poetry install --with dev

# Format code
poetry run ruff format .

# Lint code
poetry run ruff check .
```

## License

MIT License - see LICENSE file for details.

