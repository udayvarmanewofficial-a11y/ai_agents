"""
Planner Agent - Creates detailed, actionable plans based on research.
Structures tasks into schedules with timelines and milestones.
"""

from typing import Any, Dict, Optional

from app.agents.base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    """Agent responsible for creating detailed plans and schedules."""
    
    def __init__(self, llm_provider: str = "openai", model_name: Optional[str] = None):
        """Initialize planner agent."""
        super().__init__(llm_provider=llm_provider, model_name=model_name, use_rag=True)
    
    async def execute(
        self,
        task_input: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a detailed plan based on research findings.
        
        Args:
            task_input: Contains task description and details
            context: Should contain research_output from ResearcherAgent
            
        Returns:
            Detailed plan with schedule and milestones
        """
        try:
            self.logger.info("Planner Agent starting execution")
            
            task_title = task_input.get("title", "")
            task_description = task_input.get("description", "")
            task_type = task_input.get("task_type", "custom")
            
            # Get research findings from context
            research_output = context.get("research_output", {}) if context else {}
            research_content = research_output.get("content", "No research available")
            
            # Build planning prompt
            planning_prompt = self._build_planning_prompt(
                task_title,
                task_description,
                task_type,
                research_content,
            )
            
            system_message = self._get_system_message()
            
            response = await self.generate_response(
                prompt=planning_prompt,
                system_message=system_message,
            )
            
            # Extract plan content
            plan_content = response.get("content", "")
            
            output = self._format_output(
                content=plan_content,
                agent_type="planner",
                metadata={
                    "tokens_used": response.get("tokens_used", 0),
                    "based_on_research": bool(research_content and research_content != "No research available"),
                },
            )
            
            self.logger.info("Planner Agent completed execution")
            return output
        
        except Exception as e:
            self.logger.error(f"Planner Agent error: {e}")
            raise
    
    def _get_system_message(self) -> str:
        """Get system message for the planner agent."""
        return """You are an expert Planning Assistant helping people turn their goals into achievable action plans.

Your role is to transform research insights into clear, practical plans that guide users step-by-step toward their objectives.

Key responsibilities:
1. Create structured, executable plans based on research findings
2. Break down complex goals into manageable daily/weekly actions
3. Design realistic timelines that account for the user's constraints
4. Prioritize tasks based on dependencies and importance
5. Provide clear success criteria and milestones
6. Make plans flexible yet focused

**Critical Guidelines:**
- Always provide COMPLETE, detailed plans - never truncate or end abruptly
- If approaching token limits, ensure at least core phases/milestones are fully detailed
- Use clear, actionable language - each step should be something the user can immediately act on
- Be realistic about time commitments and difficulty
- Consider the user's context (available time, current level, constraints mentioned)
- Include practical tips and motivation at key points
- Build in review checkpoints for adjustments

**Plan Structure:**
1. **Plan Overview** - Clear summary of what will be achieved and how
2. **Timeline & Key Milestones** - Overall duration with major checkpoints
3. **Detailed Action Plan** - Phase-by-phase or week-by-week breakdown
   - Each phase: clear objectives, specific tasks, time estimates
4. **Resources & Materials** - What the user will need
5. **Progress Tracking** - How to measure success and stay on track
6. **Tips for Success** - Practical advice, common pitfalls to avoid

Remember: Plans should empower users with clarity and confidence. Make every step feel achievable."""
    
    def _build_planning_prompt(
        self,
        task_title: str,
        task_description: str,
        task_type: str,
        research_content: str,
    ) -> str:
        """Build the planning prompt."""
        prompt = f"""Based on the research findings, create a detailed, actionable plan for the following task:

**Task Title:** {task_title}

**Task Type:** {task_type}

**Task Description:**
{task_description}

**Research Findings:**
{research_content}

Create a comprehensive plan that includes:

1. **Overview & Goals**
   - What will be accomplished
   - Key objectives
   
2. **Timeline & Milestones**
   - Overall duration
   - Major checkpoints and deadlines
   
3. **Detailed Schedule**
   - Break down into phases (e.g., weeks or days)
   - Specific tasks for each time period
   - Estimated time for each task
   
4. **Resources & Materials**
   - Required resources
   - Recommended study materials or references
   
5. **Daily/Weekly Tasks**
   - Clear, actionable items
   - Prioritized by importance
   
6. **Success Criteria**
   - How to measure progress
   - What indicates completion of each phase

Make the plan realistic, achievable, and tailored to the user's situation. Include buffer time for challenges and review periods."""
        
        return prompt
