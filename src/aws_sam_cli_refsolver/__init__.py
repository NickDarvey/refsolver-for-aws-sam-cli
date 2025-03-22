"""AWS SAM CLI Reference Resolver package."""
from pathlib import Path
from typing import Optional, Dict, Any, Union

import boto3
from aws_cdk import cx_api

__version__ = "0.1.0"


CFNLogicalId = str
CFNDefinition = Dict[str, Any]
CFNStack = cx_api.CloudFormationStackArtifact
CDKAssembly = cx_api.CloudAssembly


def load_assembly(cdk_out_dir: Path) -> CDKAssembly:
    """Load CDK cloud assembly from the given output directory.
    
    Args:
        cdk_out_dir: Path to the CDK output directory containing assembly.json
        
    Returns:
        The loaded CloudAssembly object
    """
    return CDKAssembly(str(cdk_out_dir))


def extract_lambda_function_environment_vars(resource_tuple: tuple[CFNDefinition, CFNStack, CFNLogicalId]) -> Dict[str, Any]:
    """Extract environment variables from a Lambda function definition.
    
    Args:
        resource_tuple: Tuple of (resource_def, stack, logical_id) from find_resource()
        
    Returns:
        Dictionary mapping environment variable names to their values
        
    Example:
        >>> resource = find_resource(assembly, "ExampleFunction", "AWS::Lambda::Function")
        >>> env_vars = extract_lambda_environment_vars(resource)
        >>> print(env_vars["BUCKET_NAME"])
        {'Ref': 'ExampleBucketDC717CF4'}
    """
    # Unpack the tuple
    function, _, _ = resource_tuple
    
    # Verify resource type
    if function.get("Type") != "AWS::Lambda::Function":
        raise ValueError("Resource must be of type AWS::Lambda::Function")
    return function.get("Properties", {}).get("Environment", {}).get("Variables", {})


def extract_ecs_task_definition_environment_vars(resource_tuple: tuple[CFNDefinition, CFNStack, CFNLogicalId]) -> Dict[str, Any]:
    """Extract environment variables from an ECS task definition.
    
    Args:
        resource_tuple: Tuple of (resource_def, stack, logical_id) from find_resource()
        
    Returns:
        Dictionary mapping environment variable names to their values
        
    Example:
        >>> resource = find_resource(assembly, "ExampleTaskDef", "AWS::ECS::TaskDefinition")
        >>> env_vars = extract_environment_vars(resource)
        >>> print(env_vars["BUCKET_NAME"])
        {'Ref': 'ExampleBucketDC717CF4'}
    """
    # Unpack the tuple
    task_definition, _, _ = resource_tuple
    
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
    assembly: CDKAssembly, 
    logical_id: str,
    resource_type: str
) -> Optional[tuple[CFNDefinition, CFNStack, CFNLogicalId]]:
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
    def search_stack(template: Dict[str, Any], current_stack: CFNStack) -> Optional[tuple[CFNLogicalId, CFNDefinition, CFNStack]]:
        """Search a stack template for the resource."""
        # Look through all resources
        for CFN_logical_id, resource in template.get("Resources", {}).items():
            # Check resource type matches
            if resource.get("Type") != resource_type:
                continue
                
            # Check metadata for CDK path containing logical ID
            metadata = resource.get("Metadata", {}).get("aws:cdk:path", "")
            if f"/{logical_id}/" in metadata:
                return resource, current_stack, CFN_logical_id
            
            # Check if this is a nested stack
            if resource.get("Type") == "AWS::CloudFormation::Stack":
                # Get the nested template
                nested = resource.get("Properties", {}).get("TemplateURL", "")
                if nested and isinstance(nested, str):
                    # Load the nested template from the assembly
                    nested_name = nested.split("/")[-1].replace(".json", "")
                    for stack in assembly.stacks:
                        if stack.stack_name == nested_name:
                            result = search_stack(stack.template, stack)
                            if result:
                                return result
        
        return None

    # Search all stacks in the assembly
    for stack in assembly.stacks:
        result = search_stack(stack.template, stack)
        if result:
            return result
            
    return None




def resolve_ref(stack: cx_api.CloudFormationStackArtifact, session: boto3.Session, ref: Dict[str, str]) -> str:
    """Resolve a CloudFormation Ref to its physical resource ID.
    
    Args:
        stack: The CloudFormation stack artifact from CDK
        session: The boto3 Session to use for AWS API calls
        ref: A dict like {'Ref': 'LogicalId'}
        
    Returns:
        The physical resource ID (e.g. actual bucket name)
        
    Raises:
        TypeError: If parameters are of wrong type
        ValueError: If ref is invalid
        
    Example:
        >>> resource, stack = find_resource(assembly, "MyBucket", "AWS::S3::Bucket")
        >>> resolve_ref(stack, {'Ref': 'MyBucket'})
        'my-stack-mybucket-u4d24n1mpl0y'
    """
    # Validate parameter types
    if not isinstance(stack, cx_api.CloudFormationStackArtifact):
        raise TypeError("stack must be a CloudFormationStackArtifact")
    
    if not isinstance(session, boto3.Session):
        raise TypeError("session must be a boto3.Session")
    
    if not isinstance(ref, dict):
        raise TypeError("ref must be a dict")

    # Validate ref has 'Ref' key with non-empty string value
    if 'Ref' not in ref:
        raise ValueError("ref dict must contain 'Ref' key")
    if not isinstance(ref['Ref'], str) or not ref['Ref']:
        raise ValueError("ref['Ref'] must be a non-empty string")

    logical_id = ref['Ref']
    
    # Create CloudFormation client
    CFN = session.client('cloudformation')
    
    # Get physical resource ID
    response = CFN.describe_stack_resource(
        StackName=stack.stack_name,
        LogicalResourceId=logical_id
    )
    
    return response['StackResourceDetail']['PhysicalResourceId']
