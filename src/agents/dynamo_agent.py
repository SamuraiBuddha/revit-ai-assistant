"""Dynamo Agent - Generates visual programming scripts"""

from typing import Dict, Any, List, Type
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from .base_agent import BaseRevitAgent
from ..models.local_llm import LocalLLMModel
import json

class DynamoNode(BaseModel):
    """Represents a single Dynamo node"""
    id: str = Field(description="Unique node identifier")
    type: str = Field(description="Node type (e.g., 'Categories', 'Python Script')")
    inputs: Dict[str, str] = Field(default_factory=dict, description="Input connections")
    outputs: List[str] = Field(default_factory=list, description="Output names")
    position: Dict[str, float] = Field(default_factory=dict, description="X,Y position")
    package: str = Field(default="Core", description="Package name if custom")
    code: str = Field(default="", description="Python code if Python node")

class DynamoScript(BaseModel):
    """Output from Dynamo agent"""
    script_name: str = Field(description="Name of the Dynamo script")
    description: str = Field(description="What the script does")
    nodes: List[DynamoNode] = Field(description="All nodes in the script")
    connections: List[Dict[str, str]] = Field(description="Node connections")
    inputs: List[str] = Field(description="User inputs required")
    outputs: List[str] = Field(description="Expected outputs")
    packages_required: List[str] = Field(description="Required Dynamo packages")
    python_code: str = Field(default="", description="Standalone Python if applicable")

class DynamoAgent(BaseRevitAgent):
    """Creates Dynamo visual programming scripts"""
    
    def _setup_model(self, config: Dict[str, Any]):
        """Setup StarCoder for code generation"""
        return LocalLLMModel(
            endpoint=config.get("endpoint", "http://localhost:1235"),
            model_name=config.get("model", "starcoder2-15b"),
            context_length=config.get("context_length", 8192)
        )
        
    def _create_agent(self) -> Agent:
        """Create the Dynamo agent"""
        agent = Agent[
            Any,  # RevitContext type
            DynamoScript
        ](
            self.model,
            output_type=DynamoScript,
            system_prompt="""You are a Dynamo visual programming expert.
            You create Dynamo scripts for:
            - Complex geometry generation
            - Data manipulation and Excel integration
            - Automated documentation
            - Parametric design workflows
            - MEP system routing
            - Batch processing operations
            
            You understand:
            - Node connections and data flow
            - List management (Flatten, Transpose, Lacing)
            - DesignScript syntax
            - Python nodes for complex operations
            - Popular packages: Clockwork, Springs, Data-Shapes, Bakery
            - Geometry nodes and vector math
            - Excel and database integration
            
            Always create scripts that:
            1. Have clear node organization
            2. Include error handling in Python nodes
            3. Use appropriate list levels
            4. Are well-documented
            5. Can be reused with different inputs"""
        )
        
        # Add Dynamo-specific tools
        @agent.tool
        async def get_node_info(ctx: RunContext[Any], node_name: str) -> Dict[str, Any]:
            """Get information about a specific Dynamo node"""
            node_db = {
                "Categories": {
                    "outputs": ["Categories"],
                    "inputs": [],
                    "description": "Gets all Revit categories"
                },
                "All Elements of Category": {
                    "outputs": ["Elements"],
                    "inputs": ["category"],
                    "description": "Gets all elements of a category"
                },
                "Python Script": {
                    "outputs": ["OUT"],
                    "inputs": ["IN[0]", "IN[1]", "IN[2]"],
                    "description": "Executes Python code"
                }
            }
            return node_db.get(node_name, {})
            
        @agent.tool
        async def get_package_nodes(ctx: RunContext[Any], package: str) -> List[str]:
            """Get available nodes from a Dynamo package"""
            packages = {
                "Clockwork": ["Element.Name+", "FamilyInstance.Room", "View.ConvertToIndependent"],
                "Springs": ["Collector.ElementsInView", "FamilyInstance.ByHostAndPoint"],
                "Data-Shapes": ["UI.MultipleInputForm++", "UI.Listview Data"]
            }
            return packages.get(package, [])
            
        @agent.tool
        async def generate_python_node(ctx: RunContext[Any], task: str) -> str:
            """Generate Python code for a Dynamo Python node"""
            templates = {
                "list_processing": '''# Load the Python Standard and DesignScript Libraries
import sys
import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# Inputs
items = IN[0]

# Process list
output = []
for item in items:
    # Your processing here
    output.append(item)

# Assign output
OUT = output'''
            }
            return templates.get("list_processing", "# Custom Python code here")
            
        return agent
        
    def get_output_type(self) -> Type[BaseModel]:
        return DynamoScript