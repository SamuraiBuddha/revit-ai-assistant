"""Orchestrator Agent - Coordinates all other agents using Claude"""

from typing import Dict, Any, List, Type
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from .base_agent import BaseRevitAgent
import asyncio

class AgentTask(BaseModel):
    """Single task for an agent"""
    agent_name: str = Field(description="Which agent to use")
    task_description: str = Field(description="What the agent should do")
    dependencies: List[str] = Field(default_factory=list, description="Tasks that must complete first")
    priority: int = Field(default=1, ge=1, le=5, description="Task priority")
    
class RevitTask(BaseModel):
    """Output from Orchestrator agent"""
    task_type: str = Field(description="Type of overall task")
    tasks: List[AgentTask] = Field(description="Individual agent tasks")
    coordination_plan: str = Field(description="How tasks will be coordinated")
    expected_outcome: str = Field(description="What success looks like")
    estimated_time: str = Field(description="Estimated completion time")
    privacy_note: str = Field(default="All processing done locally except orchestration")
    
class OrchestratorAgent(BaseRevitAgent):
    """Orchestrates complex multi-agent workflows"""
    
    def __init__(self, model_config: Dict[str, Any], agent_registry: Dict[str, BaseRevitAgent]):
        """Initialize with access to all other agents"""
        self.agent_registry = agent_registry
        super().__init__(model_config, "orchestrator")
        
    def _setup_model(self, config: Dict[str, Any]):
        """Setup Claude 3 Opus (only cloud model)"""
        # This would use the anthropic SDK or API
        from pydantic_ai.models.anthropic import AnthropicModel
        return AnthropicModel(
            model_name="claude-3-opus-20240229",
            api_key=config.get("api_key")
        )
        
    def _create_agent(self) -> Agent:
        """Create the Orchestrator agent"""
        agent = Agent[
            Any,  # RevitContext type
            RevitTask
        ](
            self.model,
            output_type=RevitTask,
            system_prompt="""You are the master orchestrator for a Revit AI assistant system.
            You coordinate specialized agents to complete complex architectural tasks.
            
            Available agents and their capabilities:
            - api_expert: Generates Revit API code (C#/Python)
            - dynamo: Creates visual programming scripts
            - temporal_chief: Manages project phasing
            - visibility: Troubleshoots graphics and view issues
            - export_manager: Handles file exports (DWG, IFC, NWC)
            - import_manager: Manages imports and links
            - family_builder: Creates system families
            - component_modeler: Designs .RFA components
            - coordinate_manager: Handles survey/project coordinates
            - standards: Checks ASHRAE/BICSI/ASME compliance
            
            Your role:
            1. Understand the user's request
            2. Break it into agent-specific tasks
            3. Determine task dependencies
            4. Create an execution plan
            5. Monitor progress (conceptually)
            
            Important:
            - You only plan and coordinate
            - All actual work is done by local agents
            - Project data never leaves the user's machine
            - Prioritize safety and standards compliance
            - Consider performance and user experience"""
        )
        
        # Add orchestration tools
        @agent.tool
        async def get_agent_capabilities(ctx: RunContext[Any], agent_name: str) -> Dict[str, Any]:
            """Get capabilities of a specific agent"""
            if agent_name in self.agent_registry:
                return self.agent_registry[agent_name].get_capabilities()
            return {"error": f"Unknown agent: {agent_name}"}
            
        @agent.tool
        async def estimate_task_complexity(ctx: RunContext[Any], task: str) -> Dict[str, Any]:
            """Estimate complexity and time for a task"""
            # Simple heuristic based on keywords
            complex_keywords = ["entire", "all", "coordinate", "multi", "phase"]
            simple_keywords = ["single", "one", "specific", "quick"]
            
            complexity = "medium"
            if any(kw in task.lower() for kw in complex_keywords):
                complexity = "high"
            elif any(kw in task.lower() for kw in simple_keywords):
                complexity = "low"
                
            time_estimates = {
                "low": "1-5 minutes",
                "medium": "5-15 minutes",
                "high": "15-60 minutes"
            }
            
            return {
                "complexity": complexity,
                "estimated_time": time_estimates[complexity],
                "agent_count": 1 if complexity == "low" else 2 if complexity == "medium" else 3
            }
            
        @agent.tool
        async def check_prerequisites(ctx: RunContext[Any], task_type: str) -> List[str]:
            """Check what needs to be in place for a task"""
            prerequisites = {
                "mep_coordination": ["Current phase must be defined", "Systems must be modeled"],
                "standards_check": ["Standards database must be loaded", "Elements to check must be selected"],
                "export": ["Views must be set up", "Export settings defined"]
            }
            return prerequisites.get(task_type, [])
            
        return agent
        
    def get_output_type(self) -> Type[BaseModel]:
        return RevitTask
        
    async def execute_plan(self, plan: RevitTask, context: Any) -> Dict[str, Any]:
        """Execute the orchestrated plan using local agents"""
        results = {}
        completed_tasks = set()
        
        # Simple dependency resolution
        while len(completed_tasks) < len(plan.tasks):
            for task in plan.tasks:
                if task.agent_name in completed_tasks:
                    continue
                    
                # Check dependencies
                if all(dep in completed_tasks for dep in task.dependencies):
                    agent = self.agent_registry.get(task.agent_name)
                    if agent:
                        self.logger.info(f"Executing task: {task.agent_name} - {task.task_description}")
                        try:
                            result = await agent.process(task.task_description, context)
                            results[task.agent_name] = result
                            completed_tasks.add(task.agent_name)
                        except Exception as e:
                            self.logger.error(f"Task failed: {task.agent_name} - {e}")
                            results[task.agent_name] = {"error": str(e)}
                            completed_tasks.add(task.agent_name)
                            
            # Avoid infinite loop
            await asyncio.sleep(0.1)
            
        return results