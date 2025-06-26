"""Example: Using the API Expert agent"""

import asyncio
from src.utils import AgentRegistry
from src.schemas import RevitContext

async def main():
    # Initialize agent registry
    registry = AgentRegistry()
    await registry.initialize_agents()
    
    # Get the API Expert agent
    api_expert = registry.get_agent('api_expert')
    if not api_expert:
        print("API Expert agent not available")
        return
        
    # Create a mock Revit context
    context = RevitContext(
        project_path="/path/to/project.rvt",
        project_name="Sample Project",
        active_view_id="123456",
        active_phase_id=None,
        selected_element_ids=[],
        user_preferences={},
        standards_db=None,
        api_docs_index=None,
        revit_api=None
    )
    
    # Example queries
    queries = [
        "How do I get all walls on the active level?",
        "Show me how to create a new drafting view",
        "How can I change the phase of selected elements?",
        "Generate code to export the current view to DWG"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        try:
            result = await api_expert.process(query, context)
            print(f"\nOperation Type: {result.operation_type}")
            print(f"Transaction Required: {result.transaction_required}")
            print(f"\nCode Snippet:\n{result.code_snippet}")
            print(f"\nExplanation: {result.explanation}")
            
        except Exception as e:
            print(f"Error: {e}")
            
    # Cleanup
    await registry.shutdown()

if __name__ == "__main__":
    asyncio.run(main())