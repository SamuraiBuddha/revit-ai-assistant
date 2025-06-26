"""Example: Multi-agent coordination for MEP task"""

import asyncio
from src.utils import AgentRegistry
from src.schemas import RevitContext

async def main():
    # Initialize agent registry
    registry = AgentRegistry()
    await registry.initialize_agents()
    
    # Get the orchestrator
    orchestrator = registry.get_agent('orchestrator')
    if not orchestrator:
        print("Orchestrator not available")
        return
        
    # Create context with project info
    context = RevitContext(
        project_path="/path/to/hospital_project.rvt",
        project_name="City Hospital Expansion",
        active_view_id="mep_coordination_3d",
        active_phase_id="phase_2",
        selected_element_ids=["duct_123", "duct_456", "pipe_789"],
        user_preferences={"units": "metric"},
        standards_db=None,  # Would be real DB
        api_docs_index=None,
        revit_api=None
    )
    
    # Complex multi-agent request
    request = """We need to prepare Level 3 for MEP coordination meeting tomorrow.
    Check that all HVAC ducts meet ASHRAE requirements, ensure proper phasing,
    and prepare coordination views for export to NWC format."""
    
    print("Request:", request)
    print("\nOrchestrator is planning...\n")
    
    try:
        # Get the plan from orchestrator
        plan = await orchestrator.process(request, context)
        
        print(f"Task Type: {plan.task_type}")
        print(f"Expected Outcome: {plan.expected_outcome}")
        print(f"Estimated Time: {plan.estimated_time}")
        print(f"\nCoordination Plan:\n{plan.coordination_plan}")
        
        print("\nAgent Tasks:")
        for i, task in enumerate(plan.tasks, 1):
            print(f"\n{i}. {task.agent_name.upper()}")
            print(f"   Task: {task.task_description}")
            print(f"   Priority: {task.priority}")
            if task.dependencies:
                print(f"   Dependencies: {', '.join(task.dependencies)}")
                
        # Execute the plan (if agents were fully implemented)
        print("\n" + "="*60)
        print("Executing plan...")
        print("="*60)
        
        if hasattr(orchestrator, 'execute_plan'):
            results = await orchestrator.execute_plan(plan, context)
            
            print("\nExecution Results:")
            for agent_name, result in results.items():
                print(f"\n{agent_name}: {type(result).__name__}")
                if hasattr(result, 'summary'):
                    print(f"  Summary: {result.summary}")
        else:
            print("\n(Plan execution would happen here with all agents)")
            
    except Exception as e:
        print(f"Error: {e}")
        
    # Cleanup
    await registry.shutdown()

if __name__ == "__main__":
    asyncio.run(main())