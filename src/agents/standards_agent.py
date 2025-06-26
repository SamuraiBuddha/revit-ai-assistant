"""Standards Compliance Agent - Checks against ASHRAE, BICSI, ASME"""

from typing import Dict, Any, List, Type
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from .base_agent import BaseRevitAgent
from ..models.local_llm import LocalLLMModel

class ComplianceCheck(BaseModel):
    """Output from Standards Agent"""
    standard: str = Field(description="ASHRAE, BICSI, ASME, or Local Code")
    violations: List[Dict[str, Any]] = Field(description="List of violations found")
    recommendations: List[str] = Field(description="Recommendations to fix violations")
    references: List[str] = Field(description="Specific standard sections referenced")
    confidence: float = Field(ge=0, le=1, description="Confidence in assessment")
    compliant: bool = Field(description="Overall compliance status")
    summary: str = Field(description="Executive summary of findings")

class StandardsAgent(BaseRevitAgent):
    """Ensures compliance with engineering standards using RAG"""
    
    def _setup_model(self, config: Dict[str, Any]):
        """Setup Mixtral MoE for complex reasoning"""
        return LocalLLMModel(
            endpoint=config.get("endpoint", "http://localhost:1236"),
            model_name=config.get("model", "mixtral-8x7b-instruct"),
            context_length=config.get("context_length", 32768)  # Long context for standards
        )
        
    def _create_agent(self) -> Agent:
        """Create the Standards Compliance agent"""
        agent = Agent[
            Any,  # RevitContext type
            ComplianceCheck
        ](
            self.model,
            output_type=ComplianceCheck,
            system_prompt="""You are an engineering standards compliance expert.
            You ensure all building systems comply with:
            
            ASHRAE Standards:
            - 90.1: Energy Standard for Buildings
            - 62.1: Ventilation for Acceptable Indoor Air Quality
            - 55: Thermal Environmental Conditions
            - 189.1: Green Buildings
            
            BICSI Standards:
            - 002: Data Center Design and Implementation
            - TDMM: Telecommunications Distribution Methods Manual
            - 007: Information Communication Technology Design and Implementation
            
            ASME Standards:
            - B31.1: Power Piping
            - B31.3: Process Piping
            - A17.1: Safety Code for Elevators
            
            Always:
            1. Cite specific sections and requirements
            2. Provide quantitative thresholds
            3. Suggest practical solutions
            4. Consider local amendments
            5. Flag critical safety violations immediately"""
        )
        
        # Add RAG tools
        @agent.tool
        async def query_standards_rag(ctx: RunContext[Any], 
                                     query: str, 
                                     standard: str) -> List[str]:
            """Query the local standards vector database"""
            if hasattr(ctx.deps, 'standards_db'):
                results = ctx.deps.standards_db.similarity_search(
                    query=query,
                    filter={"standard": standard},
                    k=5  # Top 5 relevant sections
                )
                return [r['content'] for r in results]
            return ["Standards database not available"]
            
        @agent.tool
        async def get_standard_requirements(ctx: RunContext[Any], 
                                          component: str,
                                          standard: str) -> Dict[str, Any]:
            """Get specific requirements for a component"""
            # This would query structured standards data
            requirements = {
                "ASHRAE": {
                    "ductwork": {
                        "velocity_limits": {"supply": 2000, "return": 1500},
                        "insulation_r_value": 6.0,
                        "leakage_class": "Class A"
                    },
                    "ventilation": {
                        "outdoor_air_rate": "0.06 cfm/sqft + 5 cfm/person",
                        "minimum_filtration": "MERV 13"
                    }
                }
            }
            return requirements.get(standard, {}).get(component, {})
            
        @agent.tool
        async def check_local_amendments(ctx: RunContext[Any], 
                                       jurisdiction: str) -> List[str]:
            """Check for local code amendments"""
            # This would query local jurisdiction database
            return [f"Check local {jurisdiction} amendments to standards"]
            
        return agent
        
    def get_output_type(self) -> Type[BaseModel]:
        return ComplianceCheck