"""
Agent Orchestrator - Coordinates the execution of multiple agents.
Manages the workflow: Researcher -> Planner -> Reviewer.
"""

import asyncio
from typing import Any, Callable, Dict, Optional

from app.agents.planner_agent import PlannerAgent
from app.agents.researcher_agent import ResearcherAgent
from app.agents.reviewer_agent import ReviewerAgent
from app.core.logging import app_logger


class AgentOrchestrator:
    """Orchestrates the execution of multiple agents in sequence."""
    
    def __init__(
        self,
        llm_provider: str = "openai",
        model_name: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
        use_custom_rag: bool = False,
    ):
        """
        Initialize orchestrator with agents.
        
        Args:
            llm_provider: LLM provider to use
            model_name: Specific model name
            progress_callback: Optional callback for progress updates
            use_custom_rag: Force use of custom RAG data only
        """
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.progress_callback = progress_callback
        self.use_custom_rag = use_custom_rag
        self.logger = app_logger
        
        # Initialize agents
        self.researcher = ResearcherAgent(llm_provider, model_name, use_custom_rag)
        self.planner = PlannerAgent(llm_provider, model_name)
        self.reviewer = ReviewerAgent(llm_provider, model_name)
    
    async def execute_full_workflow(
        self,
        task_input: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute the complete agent workflow.
        
        Args:
            task_input: Task input containing title, description, etc.
            
        Returns:
            Dictionary containing outputs from all agents
        """
        try:
            self.logger.info("Starting full agent workflow")
            
            # Step 1: Research
            await self._send_progress("researcher", "started", 0)
            research_output = await self.researcher.execute(task_input)
            await self._send_progress("researcher", "completed", 33)
            
            # Step 2: Planning
            await self._send_progress("planner", "started", 33)
            context_with_research = {"research_output": research_output}
            plan_output = await self.planner.execute(task_input, context_with_research)
            await self._send_progress("planner", "completed", 66)
            
            # Step 3: Review
            await self._send_progress("reviewer", "started", 66)
            context_with_all = {
                "research_output": research_output,
                "plan_output": plan_output,
            }
            review_output = await self.reviewer.execute(task_input, context_with_all)
            await self._send_progress("reviewer", "completed", 100)
            
            # Compile final output
            final_output = {
                "research": research_output,
                "plan": plan_output,
                "review": review_output,
                "status": "completed",
            }
            
            self.logger.info("Full agent workflow completed successfully")
            return final_output
        
        except Exception as e:
            self.logger.error(f"Error in agent workflow: {e}")
            raise
    
    async def modify_plan(
        self,
        original_output: Dict[str, Any],
        modification_request: str,
        task_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Modify an existing plan based on user feedback.
        
        Args:
            original_output: Original workflow output
            modification_request: User's modification request
            task_context: Original task context
            
        Returns:
            Updated output with modified plan
        """
        try:
            self.logger.info("Modifying plan based on user feedback")
            
            await self._send_progress("reviewer", "started", 0)
            
            # Get the current plan
            plan_content = original_output.get("plan", {}).get("content", "")
            
            # Use reviewer to modify the plan
            modified_output = await self.reviewer.execute_modification(
                original_plan=plan_content,
                modification_request=modification_request,
                task_context=task_context,
            )
            
            await self._send_progress("reviewer", "completed", 100)
            
            # Update the output
            updated_output = original_output.copy()
            updated_output["plan"] = modified_output
            updated_output["modified"] = True
            updated_output["modification_request"] = modification_request
            
            self.logger.info("Plan modification completed")
            return updated_output
        
        except Exception as e:
            self.logger.error(f"Error modifying plan: {e}")
            raise
    
    async def _send_progress(
        self,
        agent_type: str,
        status: str,
        progress_percentage: float,
    ):
        """
        Send progress update via callback.
        
        Args:
            agent_type: Type of agent
            status: Current status
            progress_percentage: Progress percentage (0-100)
        """
        if self.progress_callback:
            try:
                await self.progress_callback({
                    "agent_type": agent_type,
                    "status": status,
                    "progress_percentage": progress_percentage,
                })
            except Exception as e:
                self.logger.error(f"Error sending progress update: {e}")
