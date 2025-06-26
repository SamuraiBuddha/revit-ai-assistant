"""Agent registry and management"""

import yaml
from typing import Dict, Any, List  # Added List import
import logging
from pathlib import Path

from ..agents import (
    BaseRevitAgent,
    OrchestratorAgent,
    APIExpertAgent,
    DynamoAgent,
    StandardsAgent
)

class AgentRegistry:
    """Manages all agents and their lifecycle"""
    
    def __init__(self, config_path: str = "config/default_config.yaml"):
        self.logger = logging.getLogger("AgentRegistry")
        self.config = self._load_config(config_path)
        self.agents: Dict[str, BaseRevitAgent] = {}
        self._initialized = False
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML"""
        path = Path(config_path)
        if not path.exists():
            self.logger.warning(f"Config file not found: {config_path}")
            return {}
            
        with open(path, 'r') as f:
            return yaml.safe_load(f)
            
    async def initialize_agents(self):
        """Initialize all configured agents"""
        if self._initialized:
            return
            
        model_configs = self.config.get('models', {})
        
        # Initialize specialized agents first
        agent_classes = {
            'api_expert': APIExpertAgent,
            'dynamo_agent': DynamoAgent,
            'standards_agent': StandardsAgent,
            # Add other agents as implemented
        }
        
        for agent_name, agent_class in agent_classes.items():
            if agent_name in model_configs:
                try:
                    self.agents[agent_name] = agent_class(
                        model_configs[agent_name],
                        agent_name
                    )
                    self.logger.info(f"Initialized {agent_name}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize {agent_name}: {e}")
                    
        # Initialize orchestrator last (needs other agents)
        if 'orchestrator' in model_configs:
            try:
                self.agents['orchestrator'] = OrchestratorAgent(
                    model_configs['orchestrator'],
                    self.agents  # Pass all other agents
                )
                self.logger.info("Initialized orchestrator")
            except Exception as e:
                self.logger.error(f"Failed to initialize orchestrator: {e}")
                
        self._initialized = True
        self.logger.info(f"Initialized {len(self.agents)} agents")
        
    def get_agent(self, name: str) -> BaseRevitAgent:
        """Get a specific agent by name"""
        return self.agents.get(name)
        
    def list_agents(self) -> List[str]:
        """List all available agent names"""
        return list(self.agents.keys())
        
    async def shutdown(self):
        """Cleanup all agents"""
        # Any cleanup needed
        self.logger.info("Shutting down agents")
        self.agents.clear()
        self._initialized = False
