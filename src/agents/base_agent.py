"""Base agent class for all Revit agents"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel
from pydantic_ai import Agent
import logging

class BaseRevitAgent(ABC):
    """Base class for all Revit AI agents"""
    
    def __init__(self, model_config: Dict[str, Any], name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
        self.model = self._setup_model(model_config)
        self.agent = self._create_agent()
        self.logger.info(f"Initialized {name} agent")
        
    @abstractmethod
    def _setup_model(self, config: Dict[str, Any]):
        """Setup the LLM model (local or cloud)"""
        pass
        
    @abstractmethod
    def _create_agent(self) -> Agent:
        """Create the PydanticAI agent with tools and prompts"""
        pass
        
    @abstractmethod
    def get_output_type(self) -> Type[BaseModel]:
        """Return the Pydantic model for agent output"""
        pass
        
    async def process(self, query: str, context: Any) -> BaseModel:
        """Process a query with context"""
        self.logger.info(f"Processing query: {query[:100]}...")
        try:
            result = await self.agent.run(query, deps=context)
            self.logger.info(f"Successfully processed query")
            return result.data
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            raise
            
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities for discovery"""
        return {
            "name": self.name,
            "output_type": self.get_output_type().__name__,
            "description": self.__class__.__doc__
        }