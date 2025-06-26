"""API Expert Agent - Generates Revit API code"""

from typing import Dict, Any, List, Type
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from .base_agent import BaseRevitAgent
from ..models.local_llm import LocalLLMModel

class APIOperation(BaseModel):
    """Output from API Expert agent"""
    operation_type: str = Field(description="query, create, modify, delete")
    api_calls: List[str] = Field(description="Actual C# or Python code lines")
    error_handling: str = Field(description="Error handling approach")
    transaction_required: bool = Field(description="Whether transaction is needed")
    code_snippet: str = Field(description="Complete code snippet")
    explanation: str = Field(description="Explanation of the code")
    references: List[str] = Field(description="API documentation references")

class APIExpertAgent(BaseRevitAgent):
    """Expert in Revit API code generation and best practices"""
    
    def _setup_model(self, config: Dict[str, Any]):
        """Setup local CodeLlama model"""
        return LocalLLMModel(
            endpoint=config.get("endpoint", "http://localhost:1234"),
            model_name=config.get("model", "codellama-13b-instruct"),
            context_length=config.get("context_length", 16384)
        )
        
    def _create_agent(self) -> Agent:
        """Create the API Expert agent"""
        agent = Agent[
            Any,  # RevitContext type
            APIOperation
        ](
            self.model,
            output_type=APIOperation,
            system_prompt="""You are a Revit API expert with deep knowledge of:
            - RevitAPI and RevitAPIUI namespaces
            - Transaction handling and document modification
            - Element filtering and LINQ queries  
            - Parameter manipulation and shared parameters
            - View creation and graphics overrides
            - Custom IUpdater implementations
            - Performance optimization techniques
            - WorkSharing and Central model operations
            
            Always include:
            1. Transaction wrapping with proper error handling
            2. Null checks and defensive programming
            3. Proper disposal of transactions
            4. Try-catch blocks for API calls
            5. Comments explaining complex operations
            
            Generate working C# or Python code for Revit API operations.
            Prefer C# unless Python is specifically requested."""
        )
        
        # Add tools
        @agent.tool
        async def search_api_docs(ctx: RunContext[Any], query: str) -> str:
            """Search local Revit API documentation"""
            # This would connect to indexed API docs
            if hasattr(ctx.deps, 'api_docs_index'):
                return ctx.deps.api_docs_index.search(query)
            return "API docs not available"
            
        @agent.tool
        async def get_element_methods(ctx: RunContext[Any], element_class: str) -> List[str]:
            """Get available methods for a Revit element class"""
            # This would use reflection or pre-indexed data
            common_methods = {
                "Wall": ["get_Parameter", "Flip", "get_Location", "get_BoundingBox"],
                "Door": ["get_FromRoom", "get_ToRoom", "Flip", "get_Host"],
                "View": ["SetCategoryHidden", "SetCategoryOverrides", "Duplicate"]
            }
            return common_methods.get(element_class, [])
            
        @agent.tool
        async def get_common_patterns(ctx: RunContext[Any], pattern_type: str) -> str:
            """Get common Revit API code patterns"""
            patterns = {
                "element_filter": """FilteredElementCollector collector = new FilteredElementCollector(doc)
                    .OfClass(typeof(Wall))
                    .WhereElementIsNotElementType();""",
                "transaction": """using (Transaction trans = new Transaction(doc, "Description"))
                {
                    trans.Start();
                    try
                    {
                        // Your code here
                        trans.Commit();
                    }
                    catch (Exception ex)
                    {
                        trans.RollBack();
                        TaskDialog.Show("Error", ex.Message);
                    }
                }"""
            }
            return patterns.get(pattern_type, "Pattern not found")
            
        return agent
        
    def get_output_type(self) -> Type[BaseModel]:
        return APIOperation