"""
Researcher Agent - Conducts research using RAG and external knowledge.
Gathers all necessary information before planning.
"""

from typing import Any, Dict, List, Optional

from app.agents.base_agent import BaseAgent


class ResearcherAgent(BaseAgent):
    """Agent responsible for researching and gathering information."""
    
    def __init__(self, llm_provider: str = "openai", model_name: Optional[str] = None, use_custom_rag: bool = False):
        """
        Initialize researcher agent.
        
        Args:
            llm_provider: LLM provider to use
            model_name: Specific model name
            use_custom_rag: Force use of custom RAG data only
        """
        super().__init__(llm_provider=llm_provider, model_name=model_name, use_rag=True)
        self.use_custom_rag = use_custom_rag
    
    async def execute(
        self,
        task_input: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Research the task and gather relevant information.
        
        Args:
            task_input: Contains task description, title, type, etc.
            context: Additional context
            
        Returns:
            Research findings and recommendations
        """
        try:
            self.logger.info("Researcher Agent starting execution")
            
            task_title = task_input.get("title", "")
            task_description = task_input.get("description", "")
            task_type = task_input.get("task_type", "custom")
            user_id = task_input.get("user_id", "")
            
            # Step 1: Query RAG system for relevant information
            self.logger.info("Querying RAG system for relevant information")
            rag_results = await self.query_rag(
                query=f"{task_title}: {task_description}",
                user_id=user_id,
                top_k=10,
            )
            
            rag_context = self.build_rag_context(rag_results, max_length=6000)
            
            # If use_custom_rag is True but no RAG data found, warn the user
            if self.use_custom_rag and not rag_results:
                self.logger.warning("use_custom_rag is enabled but no RAG data found")
                rag_context = "⚠️ Custom knowledge base is enabled but no relevant documents were found. Please upload documents to your knowledge base or disable 'Use Custom Knowledge Base' option."
            
            # Step 2: Analyze task requirements
            self.logger.info("Analyzing task requirements")
            analysis_prompt = self._build_research_prompt(
                task_title,
                task_description,
                task_type,
                rag_context,
                use_custom_rag=self.use_custom_rag,
            )
            
            system_message = self._get_system_message()
            
            response = await self.generate_response(
                prompt=analysis_prompt,
                system_message=system_message,
            )
            
            # Extract research findings
            research_content = response.get("content", "")
            
            output = self._format_output(
                content=research_content,
                agent_type="researcher",
                metadata={
                    "rag_sources_count": len(rag_results),
                    "tokens_used": response.get("tokens_used", 0),
                    "has_rag_context": len(rag_results) > 0,
                },
            )
            
            self.logger.info("Researcher Agent completed execution")
            return output
        
        except Exception as e:
            self.logger.error(f"Researcher Agent error: {e}")
            raise
    
    def _get_system_message(self) -> str:
        """Get system message for the researcher agent."""
        return """You are an expert Research Assistant helping people achieve their goals through thorough analysis and planning.

Your role is to deeply understand what the user wants to accomplish and gather all necessary information to create an effective plan.

Key responsibilities:
1. Thoroughly analyze the user's goal and current situation
2. Identify all necessary topics, skills, and resources required
3. Extract relevant information from available knowledge sources
4. Highlight critical prerequisites and dependencies
5. Flag potential challenges or roadblocks early
6. Provide actionable, well-organized insights

**Critical Guidelines:**
- Always provide COMPLETE, detailed analysis - never truncate or end abruptly
- If you're approaching token limits, prioritize the most critical information first
- Organize findings clearly with headers and bullet points
- Be conversational yet professional - avoid overly technical jargon unless necessary
- Consider the user's context (time available, current level, constraints)
- If information is unclear, note what clarifications would be helpful

**Output Structure:**
1. **Goal Understanding** - What the user wants to achieve
2. **Current State Assessment** - Where they are now (if mentioned)
3. **Key Requirements** - Topics, skills, or resources needed
4. **Knowledge Base Insights** - Relevant information from available sources
5. **Important Considerations** - Prerequisites, dependencies, challenges
6. **Recommendations for Planning** - What to prioritize, suggested approach

Remember: Be thorough but also practical. Focus on helping the user succeed."""
    
    def _build_research_prompt(
        self,
        task_title: str,
        task_description: str,
        task_type: str,
        rag_context: str,
        use_custom_rag: bool = False,
    ) -> str:
        """Build the research prompt."""
        
        # Add instruction about custom knowledge base restriction if enabled
        custom_rag_instruction = ""
        if use_custom_rag:
            custom_rag_instruction = """
⚠️ **IMPORTANT: Custom Knowledge Base Mode is ENABLED**
- You MUST use ONLY the information from the knowledge base provided below
- DO NOT use any external knowledge or general information you may have
- If the knowledge base doesn't contain sufficient information, clearly state what's missing
- Base all your research findings strictly on the provided documents
"""
        
        prompt = f"""I need to research and gather information for the following task:

**Task Title:** {task_title}

**Task Type:** {task_type}

**Task Description:**
{task_description}

{custom_rag_instruction}

**Available Knowledge Base Information:**
{rag_context if rag_context else "No specific documents found in the knowledge base."}

Please conduct comprehensive research on this task. Analyze the requirements, identify key topics and concepts, and provide detailed findings that will help in creating an effective plan.

Focus on:
1. Understanding what needs to be accomplished
2. Identifying key topics, concepts, or skills required
3. Extracting relevant information from the knowledge base
4. Providing actionable recommendations for planning
5. Highlighting prerequisites and potential challenges

Provide your research findings in a well-structured format."""
        
        return prompt
