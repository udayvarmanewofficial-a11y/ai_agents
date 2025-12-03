"""
Reviewer Agent - Reviews and refines plans created by the Planner Agent.
Provides feedback, identifies issues, and suggests improvements.
"""

from typing import Any, Dict, Optional

from app.agents.base_agent import BaseAgent


class ReviewerAgent(BaseAgent):
    """Agent responsible for reviewing and refining plans."""
    
    def __init__(self, llm_provider: str = "openai", model_name: Optional[str] = None):
        """Initialize reviewer agent."""
        super().__init__(llm_provider=llm_provider, model_name=model_name, use_rag=False)
    
    async def execute(
        self,
        task_input: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Review the plan and provide feedback or refinements.
        
        Args:
            task_input: Contains original task description
            context: Should contain research_output and plan_output
            
        Returns:
            Review feedback and refined plan
        """
        try:
            self.logger.info("Reviewer Agent starting execution")
            
            task_title = task_input.get("title", "")
            task_description = task_input.get("description", "")
            
            # Get research and plan from context
            research_output = context.get("research_output", {}) if context else {}
            plan_output = context.get("plan_output", {}) if context else {}
            
            research_content = research_output.get("content", "No research available")
            plan_content = plan_output.get("content", "No plan available")
            
            # Build review prompt
            review_prompt = self._build_review_prompt(
                task_title,
                task_description,
                research_content,
                plan_content,
            )
            
            system_message = self._get_system_message()
            
            response = await self.generate_response(
                prompt=review_prompt,
                system_message=system_message,
            )
            
            # Extract review content
            review_content = response.get("content", "")
            
            output = self._format_output(
                content=review_content,
                agent_type="reviewer",
                metadata={
                    "tokens_used": response.get("tokens_used", 0),
                    "reviewed_plan": bool(plan_content and plan_content != "No plan available"),
                },
            )
            
            self.logger.info("Reviewer Agent completed execution")
            return output
        
        except Exception as e:
            self.logger.error(f"Reviewer Agent error: {e}")
            raise
    
    async def execute_modification(
        self,
        original_plan: str,
        modification_request: str,
        task_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Modify an existing plan based on user feedback.
        
        Args:
            original_plan: The original plan content
            modification_request: User's requested changes
            task_context: Original task context
            
        Returns:
            Modified plan
        """
        try:
            self.logger.info("Reviewer Agent modifying plan")
            
            modification_prompt = self._build_modification_prompt(
                original_plan,
                modification_request,
                task_context,
            )
            
            system_message = self._get_system_message()
            
            response = await self.generate_response(
                prompt=modification_prompt,
                system_message=system_message,
            )
            
            modified_content = response.get("content", "")
            
            output = self._format_output(
                content=modified_content,
                agent_type="reviewer",
                metadata={
                    "tokens_used": response.get("tokens_used", 0),
                    "modification_applied": True,
                },
            )
            
            self.logger.info("Plan modification completed")
            return output
        
        except Exception as e:
            self.logger.error(f"Error modifying plan: {e}")
            raise
    
    def _get_system_message(self) -> str:
        """Get system message for the reviewer agent."""
        return """You are an expert Plan Optimization Specialist. Your role is to take a draft plan and transform it into a polished, user-ready final deliverable.

**Your Task:**
Review the draft plan internally, identify improvements, and output ONLY the final, refined plan - clean and ready to use.

**What to Output:**
- A complete, well-structured plan that the user can follow immediately
- Clear sections with actionable steps, timelines, and milestones
- Specific, practical guidance without meta-commentary
- Professional formatting with headings, bullet points, and clear organization

**What NOT to Output:**
- DO NOT include your review process, assessment, or critique
- DO NOT write "Here's what I found..." or "Strengths include..."
- DO NOT include sections like "Overall Assessment", "Areas for Improvement", "Feedback"
- DO NOT add commentary about the plan - just present the refined plan itself

**Critical Guidelines:**
- Present information in a direct, instructional tone (e.g., "Start with...", "Focus on...", "Complete by...")
- Ensure the plan is complete - never truncate or end abruptly
- Enhance weak areas from the draft but present them as if they were always part of the plan
- Make timelines realistic, steps clear, and success criteria measurable
- Use clear structure: Overview → Phases/Steps → Execution Tips → Key Success Factors
- Keep the user's context (time, skill level, constraints) in mind

**Example of Good Output:**
"# Your 6-Month Study Plan

## Overview
This plan will help you systematically prepare for your exams through three focused phases...

## Phase 1: Foundation Building (Months 1-2)
**Goal:** Complete first pass of all subjects...
- Week 1-2: Focus on Mathematics chapters 1-5...
- Daily Schedule: 2 hours morning, 1.5 hours evening...

## Execution Strategy
- Start each day by reviewing yesterday's notes...
- Take one full day off each week..."

Remember: Output only the final plan. No meta-discussion, no review commentary - just the polished deliverable."""
    
    def _build_review_prompt(
        self,
        task_title: str,
        task_description: str,
        research_content: str,
        plan_content: str,
    ) -> str:
        """Build the review prompt."""
        prompt = f"""You have a draft plan that needs to be finalized. Review it internally and output ONLY the polished, final plan.

**Task Details:**
Title: {task_title}
Description: {task_description}

**Background Research:**
{research_content}

**Draft Plan to Refine:**
{plan_content}

**Your Instructions:**
1. Internally review the draft plan for completeness, feasibility, and clarity
2. Identify any gaps, unrealistic timelines, or vague instructions
3. Incorporate improvements from the research findings
4. Output ONLY the final, polished plan - no meta-commentary

**Output Format:**
- Start directly with the plan title/heading
- Use clear sections: Overview, Phases/Timeline, Daily/Weekly Structure, Key Strategies, Success Tips
- Make every instruction specific and actionable
- Include concrete examples where helpful
- End with practical execution advice

**Remember:** Output the final plan ONLY. Do not include:
- "Here's my assessment..."
- "Strengths of this plan..."
- "Areas for improvement..."
- "I recommend changing..."

Just present the clean, ready-to-use plan as if you created it perfectly from the start."""
        
        return prompt
    
    def _build_modification_prompt(
        self,
        original_plan: str,
        modification_request: str,
        task_context: Dict[str, Any],
    ) -> str:
        """Build the modification prompt."""
        task_title = task_context.get("title", "")
        task_description = task_context.get("description", "")
        
        prompt = f"""You need to update an existing plan based on user feedback. Output ONLY the modified plan - no commentary.

**Original Task:**
Title: {task_title}
Description: {task_description}

**Current Plan:**
{original_plan}

**User's Requested Changes:**
{modification_request}

**Your Instructions:**
1. Apply the user's requested changes to the plan
2. Ensure the modified sections integrate smoothly with the rest of the plan
3. Maintain the overall structure and quality
4. Output ONLY the complete updated plan

**Remember:** 
- Do NOT include "Summary of Changes" or "Here's what I modified"
- Do NOT add meta-commentary about the modifications
- Just output the clean, updated plan directly
- Start with the plan title and proceed with the content

Present the final modified plan as if it was created this way from the beginning."""
        
        return prompt
