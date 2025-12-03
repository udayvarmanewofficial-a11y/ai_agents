"""
Google Gemini LLM provider implementation.
"""

from typing import Any, Dict, List, Optional

import google.generativeai as genai
from app.services.llm.base_provider import BaseLLMProvider
from tenacity import retry, stop_after_attempt, wait_exponential


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider implementation."""
    
    def __init__(self, api_key: str, model_name: str, temperature: float = 0.7, max_tokens: int = 2000):
        """Initialize Gemini provider."""
        super().__init__(api_key, model_name, temperature, max_tokens)
        genai.configure(api_key=api_key)
        
        # Configure generation parameters
        self.generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "top_p": 0.95,
            "top_k": 40,
        }
        
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=self.generation_config,
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response using Gemini API.
        
        Args:
            prompt: User prompt
            system_message: System message (included in prompt for Gemini)
            context: Conversation history
            **kwargs: Additional Gemini parameters
            
        Returns:
            Generated response with metadata
        """
        try:
            # Format prompt with system message and context
            full_prompt = self._format_prompt_for_gemini(prompt, system_message, context)
            
            # Update generation config if custom parameters provided
            generation_config = self.generation_config.copy()
            if "temperature" in kwargs:
                generation_config["temperature"] = kwargs["temperature"]
            if "max_tokens" in kwargs:
                generation_config["max_output_tokens"] = kwargs["max_tokens"]
            
            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=generation_config,
            )
            
            # Extract token count (Gemini provides this differently)
            tokens_used = getattr(response.usage_metadata, 'total_token_count', 0) if hasattr(response, 'usage_metadata') else 0
            prompt_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0
            completion_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0
            
            return {
                "content": response.text,
                "tokens_used": tokens_used,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "model": self.model_name,
                "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "STOP",
            }
        
        except Exception as e:
            self.logger.error(f"Gemini API error: {e}")
            raise
    
    async def generate_stream(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ):
        """
        Generate a streaming response using Gemini API.
        
        Args:
            prompt: User prompt
            system_message: System message
            context: Conversation history
            **kwargs: Additional Gemini parameters
            
        Yields:
            Chunks of generated text
        """
        try:
            full_prompt = self._format_prompt_for_gemini(prompt, system_message, context)
            
            generation_config = self.generation_config.copy()
            if "temperature" in kwargs:
                generation_config["temperature"] = kwargs["temperature"]
            if "max_tokens" in kwargs:
                generation_config["max_output_tokens"] = kwargs["max_tokens"]
            
            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=generation_config,
                stream=True,
            )
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            self.logger.error(f"Gemini streaming error: {e}")
            raise
    
    def _format_prompt_for_gemini(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Format prompt for Gemini (which doesn't have a separate system message).
        
        Args:
            prompt: User prompt
            system_message: System message
            context: Conversation history
            
        Returns:
            Formatted prompt string
        """
        parts = []
        
        if system_message:
            parts.append(f"System Instructions: {system_message}\n")
        
        if context:
            parts.append("Previous conversation:\n")
            for msg in context:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                parts.append(f"{role.capitalize()}: {content}\n")
        
        parts.append(f"User: {prompt}")
        
        return "\n".join(parts)
