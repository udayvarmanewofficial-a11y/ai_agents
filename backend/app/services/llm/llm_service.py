"""
LLM provider factory and management.
Provides unified interface for different LLM providers.
"""

from typing import Optional

from app.core.config import settings
from app.core.logging import app_logger
from app.services.llm.base_provider import BaseLLMProvider
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.openai_provider import OpenAIProvider


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""
    
    @staticmethod
    def create_provider(
        provider_name: str,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> BaseLLMProvider:
        """
        Create an LLM provider instance.
        
        Args:
            provider_name: Name of the provider ("openai" or "gemini")
            model_name: Model name (optional, uses default from settings)
            temperature: Sampling temperature (optional, uses default from settings)
            max_tokens: Max tokens (optional, uses default from settings)
            
        Returns:
            LLM provider instance
            
        Raises:
            ValueError: If provider is not supported or API key is missing
        """
        provider_name = provider_name.lower()
        
        if provider_name == "openai":
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            
            return OpenAIProvider(
                api_key=settings.openai_api_key,
                model_name=model_name or settings.openai_model,
                temperature=temperature or settings.openai_temperature,
                max_tokens=max_tokens or settings.openai_max_tokens,
            )
        
        elif provider_name == "gemini":
            if not settings.google_api_key:
                raise ValueError("Google API key not configured")
            
            return GeminiProvider(
                api_key=settings.google_api_key,
                model_name=model_name or settings.gemini_model,
                temperature=temperature or settings.gemini_temperature,
                max_tokens=max_tokens or settings.gemini_max_tokens,
            )
        
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")
    
    @staticmethod
    def get_default_provider() -> BaseLLMProvider:
        """
        Get the default LLM provider configured in settings.
        
        Returns:
            Default LLM provider instance
        """
        return LLMProviderFactory.create_provider(settings.default_llm_provider)


class LLMService:
    """High-level service for LLM operations."""
    
    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        """
        Initialize LLM service.
        
        Args:
            provider: LLM provider instance (optional, uses default if not provided)
        """
        self.provider = provider or LLMProviderFactory.get_default_provider()
        self.logger = app_logger
    
    async def generate_response(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        context: Optional[list] = None,
        **kwargs
    ) -> dict:
        """
        Generate a response using the configured provider.
        
        Args:
            prompt: User prompt
            system_message: System message
            context: Conversation history
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        try:
            self.logger.info(f"Generating response using {self.provider.__class__.__name__}")
            response = await self.provider.generate(
                prompt=prompt,
                system_message=system_message,
                context=context,
                **kwargs
            )
            self.logger.info(f"Response generated successfully. Tokens used: {response.get('tokens_used', 0)}")
            return response
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise
    
    async def generate_stream(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        context: Optional[list] = None,
        **kwargs
    ):
        """
        Generate a streaming response.
        
        Args:
            prompt: User prompt
            system_message: System message
            context: Conversation history
            **kwargs: Additional parameters
            
        Yields:
            Response chunks
        """
        try:
            self.logger.info(f"Generating streaming response using {self.provider.__class__.__name__}")
            async for chunk in self.provider.generate_stream(
                prompt=prompt,
                system_message=system_message,
                context=context,
                **kwargs
            ):
                yield chunk
        except Exception as e:
            self.logger.error(f"Error generating streaming response: {e}")
            raise
