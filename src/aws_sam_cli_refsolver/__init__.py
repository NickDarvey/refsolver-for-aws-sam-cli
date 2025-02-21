"""AWS SAM CLI Reference Resolver package."""
from pathlib import Path
from typing import Optional, Dict, Any

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


def extract_environment_vars(task_definition: Dict[str, Any]) -> Dict[str, Any]:
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
