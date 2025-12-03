"""
OpenAI LLM provider implementation.
"""

from typing import Any, Dict, List, Optional

import openai
from app.services.llm.base_provider import BaseLLMProvider
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider implementation."""
    
    def __init__(self, api_key: str, model_name: str, temperature: float = 0.7, max_tokens: int = 2000):
        """Initialize OpenAI provider."""
        super().__init__(api_key, model_name, temperature, max_tokens)
        self.client = AsyncOpenAI(api_key=api_key)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response using OpenAI API.
        
        Args:
            prompt: User prompt
            system_message: System message
            context: Conversation history
            **kwargs: Additional OpenAI parameters
            
        Returns:
            Generated response with metadata
        """
        try:
            messages = self._format_messages(prompt, system_message, context)
            
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty", 0.0),
                presence_penalty=kwargs.get("presence_penalty", 0.0),
            )
            
            return {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
            }
        
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise
    
    async def generate_stream(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ):
        """
        Generate a streaming response using OpenAI API.
        
        Args:
            prompt: User prompt
            system_message: System message
            context: Conversation history
            **kwargs: Additional OpenAI parameters
            
        Yields:
            Chunks of generated text
        """
        try:
            messages = self._format_messages(prompt, system_message, context)
            
            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                stream=True,
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            self.logger.error(f"OpenAI streaming error: {e}")
            raise
