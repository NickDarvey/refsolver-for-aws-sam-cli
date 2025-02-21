"""AWS SAM CLI Reference Resolver package."""
from pathlib import Path
from typing import Optional, Dict, Any, Union

import boto3
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
    return cx_api.CloudAssembly(str(cdk_out_dir))


def extract_lambda_function_environment_vars(function: Dict[str, Any]) -> Dict[str, Any]:
    """Extract environment variables from a Lambda function definition.
    
    Args:
        function: The CloudFormation resource definition for a Lambda function
        
    Returns:
        Dictionary mapping environment variable names to their values
        
    Example:
        >>> func = find_resource(assembly, "ExampleFunction", "AWS::Lambda::Function")
        >>> env_vars = extract_lambda_environment_vars(func)
        >>> print(env_vars["BUCKET_NAME"])
        {'Ref': 'ExampleBucketDC717CF4'}
    """
    # Verify resource type
    if function.get("Type") != "AWS::Lambda::Function":
        raise ValueError("Resource must be of type AWS::Lambda::Function")
    return function.get("Properties", {}).get("Environment", {}).get("Variables", {})


def extract_ecs_task_definition_environment_vars(task_definition: Dict[str, Any]) -> Dict[str, Any]:
    """Extract environment variables from an ECS task definition.
    
    Args:
        task_definition: The CloudFormation resource definition for an ECS task
        
    Returns:
        Dictionary mapping environment variable names to their values
        
    Example:
        >>> task_def = find_resource(assembly, "ExampleTaskDef", "AWS::ECS::TaskDefinition")
        >>> env_vars = extract_environment_vars(task_def)
        >>> print(env_vars["BUCKET_NAME"])
        {'Ref': 'ExampleBucketDC717CF4'}
    """
    # Verify resource type
    if task_definition.get("Type") != "AWS::ECS::TaskDefinition":
        raise ValueError("Resource must be of type AWS::ECS::TaskDefinition")
    env_vars = {}
    
    # Get container definitions
    containers = task_definition.get("Properties", {}).get("ContainerDefinitions", [])
    
    # Extract environment variables from each container
    for container in containers:
        for env in container.get("Environment", []):
            name = env.get("Name")
            value = env.get("Value")
            if name and value:
                env_vars[name] = value
                
    return env_vars


def find_resource(
    assembly: cx_api.CloudAssembly, 
    logical_id: str,
    resource_type: str
) -> Optional[Dict[str, Any]]:
    """Find a CloudFormation resource by its CDK logical ID and type.
    
    Args:
        assembly: The CDK cloud assembly to search
        logical_id: The original CDK logical ID (e.g. 'ExampleFunction')
        resource_type: The CloudFormation resource type (e.g. 'AWS::Lambda::Function')
        
    Returns:
        The CloudFormation resource definition if found, None otherwise
        
    Example:
        >>> assembly = load_assembly(Path("cdk.out"))
        >>> function = find_resource(assembly, "ExampleFunction", "AWS::Lambda::Function")
        >>> print(function["Type"])
        'AWS::Lambda::Function'
    """
    def search_stack(template: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Search a stack template for the resource."""
        # Look through all resources
        for resource in template.get("Resources", {}).values():
            # Check resource type matches
            if resource.get("Type") != resource_type:
                continue
                
            # Check metadata for CDK path containing logical ID
            metadata = resource.get("Metadata", {}).get("aws:cdk:path", "")
            if f"/{logical_id}/" in metadata:
                return resource
            
            # Check if this is a nested stack
            if resource.get("Type") == "AWS::CloudFormation::Stack":
                # Get the nested template
                nested = resource.get("Properties", {}).get("TemplateURL", "")
                if nested and isinstance(nested, str):
                    # Load the nested template from the assembly
                    nested_name = nested.split("/")[-1].replace(".json", "")
                    for stack in assembly.stacks:
                        if stack.stack_name == nested_name:
                            result = search_stack(stack.template)
                            if result:
                                return result
        
        return None

    # Search all stacks in the assembly
    for stack in assembly.stacks:
        result = search_stack(stack.template)
        if result:
            return result
            
    return None


def test_resolve_ref(mocker):
    """Test resolving CloudFormation refs to physical IDs."""
    # Mock the CloudFormation client
    mock_cfn = mocker.patch('boto3.client')
    mock_cfn.return_value.describe_stack_resource.return_value = {
        'StackResourceDetail': {
            'PhysicalResourceId': 'my-stack-bucket-u4d24n1mpl0y'
        }
    }
    
    # Test with valid dict ref
    ref = {'Ref': 'MyBucket'}
    assert resolve_ref('my-stack', ref) == 'my-stack-bucket-u4d24n1mpl0y'
    
    # Test with valid string ref
    assert resolve_ref('my-stack', 'MyBucket') == 'my-stack-bucket-u4d24n1mpl0y'
    
    # Test invalid inputs
    with pytest.raises(ValueError, match="stack_name must be a non-empty string"):
        resolve_ref('', ref)
    
    with pytest.raises(ValueError, match="ref dict must contain 'Ref' key"):
        resolve_ref('my-stack', {})
    
    with pytest.raises(ValueError, match="ref\\['Ref'\\] must be a non-empty string"):
        resolve_ref('my-stack', {'Ref': ''})
    
    with pytest.raises(ValueError, match="ref string must be non-empty"):
        resolve_ref('my-stack', '')
    
    with pytest.raises(TypeError, match="ref must be either a dict with 'Ref' key or a string"):
        resolve_ref('my-stack', 123)
    
    # Verify correct API call
    mock_cfn.return_value.describe_stack_resource.assert_called_with(
        StackName='my-stack',
        LogicalResourceId='MyBucket'
    )


def resolve_ref(stack_name: str, ref: Union[Dict[str, str], str], region: Optional[str] = None) -> str:
    """Resolve a CloudFormation Ref to its physical resource ID.
    
    Args:
        stack_name: Name of the CloudFormation stack
        ref: Either a dict like {'Ref': 'LogicalId'} or a logical ID string
        region: Optional AWS region, defaults to current session region
        
    Returns:
        The physical resource ID (e.g. actual bucket name)
        
    Raises:
        ValueError: If stack_name is empty or ref is invalid
        TypeError: If ref is neither a dict with 'Ref' key nor a string
        
    Example:
        >>> resolve_ref("MyStack", {'Ref': 'MyBucket'})
        'my-stack-mybucket-u4d24n1mpl0y'
    """
    # Validate stack name
    if not stack_name or not isinstance(stack_name, str):
        raise ValueError("stack_name must be a non-empty string")

    # Validate and extract logical ID from ref
    if isinstance(ref, dict):
        if 'Ref' not in ref:
            raise ValueError("ref dict must contain 'Ref' key")
        if not isinstance(ref['Ref'], str) or not ref['Ref']:
            raise ValueError("ref['Ref'] must be a non-empty string")
        logical_id = ref['Ref']
    elif isinstance(ref, str):
        if not ref:
            raise ValueError("ref string must be non-empty")
        logical_id = ref
    else:
        raise TypeError("ref must be either a dict with 'Ref' key or a string")
    
    # Create CloudFormation client
    cfn = boto3.client('cloudformation', region_name=region)
    
    # Get physical resource ID
    response = cfn.describe_stack_resource(
        StackName=stack_name,
        LogicalResourceId=logical_id
    )
    
    return response['StackResourceDetail']['PhysicalResourceId']
