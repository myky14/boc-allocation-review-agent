import pandas as pd
from typing import Optional
from boc_agent.skill.loader import SkillLoader
from boc_agent.runtime.context import RuntimeContext
from boc_agent.runtime.planner import Planner
from boc_agent.runtime.tool_registry import ToolRegistry
from boc_agent.runtime.executor import Executor
from boc_agent.runtime.response import ResponseBuilder

class BOCReviewAgent:
    def __init__(self):
        self.registry = ToolRegistry()
        self.planner = Planner()
        self.executor = Executor(self.registry)
        self.response_builder = ResponseBuilder()

    def run(self, question: str, reviewed_df: Optional[pd.DataFrame] = None) -> str:
        """Loads skill contract, runs planning, executes resolved tool, and formats the output."""
        skill = None
        skill_load_error = None
        try:
            skill = SkillLoader().get_skill()
        except Exception as e:
            skill_load_error = e

        # Create RuntimeContext for the turn
        context = RuntimeContext(
            question=question,
            reviewed_df=reviewed_df,
            skill=skill
        )
        context.add_trace("Agent: Initialized RuntimeContext for the current execution turn.")

        if skill_load_error is not None or skill is None:
            err_msg = "Skill configuration is unavailable or invalid. Runtime execution has been blocked for safety."
            context.errors.append(str(skill_load_error or "Skill is None"))
            context.add_trace(f"Agent: Blocked execution due to missing or invalid skill configuration: {skill_load_error}")
            return err_msg

        try:
            # 1. Plan intent
            self.planner.plan(context)
            
            # 2. Execute tool
            raw_result = self.executor.execute(context)
            
            # 3. Build response
            final_response = self.response_builder.build_response(context, raw_result)
            return final_response
        except Exception as e:
            # Prevent showing raw stack trace or crashing
            context.errors.append(str(e))
            context.add_trace(f"Agent: Encountered runtime crash: {str(e)}")
            return "An unexpected error occurred during agent runtime execution."
