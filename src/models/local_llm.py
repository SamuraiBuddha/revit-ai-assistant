"""Local LLM model wrapper for LM Studio, Ollama, etc."""

import httpx
import asyncio
from typing import Dict, Any, List, Optional
import json
import logging

class LocalLLMModel:
    """Wrapper for local LLM endpoints (OpenAI-compatible)"""
    
    def __init__(self, endpoint: str, model_name: str, context_length: int = 8192):
        self.endpoint = endpoint.rstrip('/')
        self.model_name = model_name
        self.context_length = context_length
        self.client = httpx.AsyncClient(
            base_url=endpoint,
            timeout=120.0  # Longer timeout for local models
        )
        self.logger = logging.getLogger(f"model.{model_name}")
        
    async def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Complete a prompt using the local model"""
        try:
            # OpenAI-compatible endpoint
            response = await self.client.post(
                "/v1/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": kwargs.get("max_tokens", 2048),
                    "temperature": kwargs.get("temperature", 0.7),
                    "stream": False,
                    **kwargs
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Completion error: {e}")
            raise
            
    async def stream_complete(self, prompt: str, **kwargs):
        """Stream completions from the local model"""
        try:
            async with self.client.stream(
                "POST",
                "/v1/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": kwargs.get("max_tokens", 2048),
                    "temperature": kwargs.get("temperature", 0.7),
                    "stream": True,
                    **kwargs
                }
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            self.logger.error(f"Stream error: {e}")
            raise
            
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        try:
            response = await self.client.get("/v1/models")
            response.raise_for_status()
            return response.json()
        except:
            return {"model": self.model_name, "context_length": self.context_length}
            
    async def health_check(self) -> bool:
        """Check if the model endpoint is responsive"""
        try:
            response = await self.client.get("/health")
            return response.status_code == 200
        except:
            return False
            
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
        
    # PydanticAI compatibility methods
    async def request(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """PydanticAI compatible request method"""
        response = await self.complete(
            prompt=messages[-1]["content"],  # Use last message
            **kwargs
        )
        return response["choices"][0]["message"]["content"]
        
    @property
    def name(self) -> str:
        """Model name for PydanticAI"""
        return f"local:{self.model_name}"