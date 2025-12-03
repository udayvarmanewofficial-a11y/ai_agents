"""
Base Agent class that all specialized agents inherit from.
Provides common functionality and RAG access.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.core.logging import app_logger
from app.services.llm import LLMProviderFactory, LLMService
from app.services.rag import get_rag_service


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(
        self,
        llm_provider: str = "openai",
        model_name: Optional[str] = None,
        use_rag: bool = True,
    ):
        """
        Initialize base agent.
        
        Args:
            llm_provider: LLM provider name
            model_name: Specific model to use
            use_rag: Whether this agent should have RAG access
        """
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.use_rag = use_rag
        self.logger = app_logger
        
        # Initialize LLM service
        provider = LLMProviderFactory.create_provider(
            provider_name=llm_provider,
            model_name=model_name,
        )
        self.llm_service = LLMService(provider=provider)
        
        # Initialize RAG service if needed
        self.rag_service = get_rag_service() if use_rag else None
        
        self.logger.info(f"{self.__class__.__name__} initialized with {llm_provider}")
    
    @abstractmethod
    async def execute(
        self,
        task_input: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute the agent's main task.
        
        Args:
            task_input: Input data for the task
            context: Additional context (e.g., from previous agents)
            
        Returns:
            Agent's output
        """
        pass
    
    async def query_rag(
        self,
        query: str,
        user_id: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Query the RAG system for relevant information.
        
        Args:
            query: Search query
            user_id: User ID for filtering
            top_k: Number of results
            
        Returns:
            List of relevant documents
        """
        if not self.rag_service:
            self.logger.warning("RAG service not available for this agent")
            return []
        
        try:
            results = await self.rag_service.search(
                query=query,
                top_k=top_k,
                user_id=user_id,
            )
            return results
        except Exception as e:
            self.logger.error(f"Error querying RAG: {e}")
            return []
    
    def build_rag_context(
        self,
        results: List[Dict[str, Any]],
        max_length: int = 4000,
    ) -> str:
        """
        Build context string from RAG results.
        
        Args:
            results: RAG search results
            max_length: Maximum context length
            
        Returns:
            Formatted context string
        """
        if not self.rag_service:
            return ""
        
        return self.rag_service.build_context_from_results(results, max_length)
    
    async def generate_response(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        context: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response using the LLM.
        
        Args:
            prompt: User prompt
            system_message: System message
            context: Conversation history
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        try:
            response = await self.llm_service.generate_response(
                prompt=prompt,
                system_message=system_message,
                context=context,
                **kwargs
            )
            
            # Check if response was truncated due to token limits
            finish_reason = response.get("finish_reason", "stop")
            if finish_reason == "length":
                self.logger.warning("Response truncated due to token limit, attempting continuation")
                response = await self._continue_response(
                    initial_response=response,
                    prompt=prompt,
                    system_message=system_message,
                    context=context,
                    **kwargs
                )
            
            return response
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise
    
    async def _continue_response(
        self,
        initial_response: Dict[str, Any],
        prompt: str,
        system_message: Optional[str] = None,
        context: Optional[list] = None,
        max_continuations: int = 2,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Continue a truncated response by making follow-up requests.
        
        Args:
            initial_response: The initial truncated response
            prompt: Original prompt
            system_message: System message
            context: Conversation history
            max_continuations: Maximum number of continuation attempts
            **kwargs: Additional parameters
            
        Returns:
            Combined response with continued content
        """
        combined_content = initial_response.get("content", "")
        total_tokens = initial_response.get("tokens_used", 0)
        
        for attempt in range(max_continuations):
            # Create continuation prompt
            continuation_prompt = f"""Please continue from where you left off. Previous content:

{combined_content[-500:]}

Continue with the remaining sections to ensure completeness."""
            
            try:
                continuation = await self.llm_service.generate_response(
                    prompt=continuation_prompt,
                    system_message=system_message,
                    context=context,
                    **kwargs
                )
                
                continuation_content = continuation.get("content", "")
                combined_content += "\n\n" + continuation_content
                total_tokens += continuation.get("tokens_used", 0)
                
                # Check if this continuation was also truncated
                if continuation.get("finish_reason", "stop") != "length":
                    # Successfully completed
                    break
                    
            except Exception as e:
                self.logger.error(f"Error during continuation attempt {attempt + 1}: {e}")
                break
        
        # Update the response with combined content
        result = initial_response.copy()
        result["content"] = combined_content
        result["tokens_used"] = total_tokens
        result["was_continued"] = True
        result["finish_reason"] = "stop"
        
        return result
    
    def _format_output(
        self,
        content: str,
        agent_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Format agent output in a standard structure.
        
        Args:
            content: Agent's output content
            agent_type: Type of agent
            metadata: Additional metadata
            
        Returns:
            Formatted output dictionary
        """
        return {
            "agent_type": agent_type,
            "content": content,
            "metadata": metadata or {},
            "llm_provider": self.llm_provider,
            "model_name": self.model_name,
        }
