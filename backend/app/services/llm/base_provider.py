"""
Base LLM provider interface.
Defines the contract that all LLM providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.core.logging import app_logger


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, api_key: str, model_name: str, temperature: float = 0.7, max_tokens: int = 2000):
        """
        Initialize LLM provider.
        
        Args:
            api_key: API key for the provider
            model_name: Name of the model to use
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.logger = app_logger
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User prompt
            system_message: System message to set context
            context: Conversation history
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dictionary containing:
                - content: Generated text
                - tokens_used: Number of tokens consumed
                - model: Model name used
                - finish_reason: Why generation stopped
        """
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ):
        """
        Generate a streaming response from the LLM.
        
        Args:
            prompt: User prompt
            system_message: System message to set context
            context: Conversation history
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Chunks of generated text
        """
        pass
    
    def _format_messages(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """
        Format messages for the API call.
        
        Args:
            prompt: User prompt
            system_message: System message
            context: Conversation history
            
        Returns:
            Formatted messages list
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        if context:
            messages.extend(context)
        
        messages.append({"role": "user", "content": prompt})
        
        return messages
