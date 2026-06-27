import re
import pandas as pd
from typing import Optional, Tuple
from boc_agent.skill.loader import SkillLoader
from boc_agent.runtime.context import RuntimeContext
from boc_agent.runtime.planner import Planner
from boc_agent.runtime.tool_registry import ToolRegistry
from boc_agent.runtime.executor import Executor
from boc_agent.runtime.response import ResponseBuilder
from boc_agent.runtime.trace.trace_models import RuntimeTrace

class BOCReviewAgent:
    last_trace: Optional[RuntimeTrace] = None

    def __init__(self):
        self.registry = ToolRegistry()
        self.planner = Planner()
        self.executor = Executor(self.registry)
        self.response_builder = ResponseBuilder()
        self.last_trace = None

    def run(self, question: str, reviewed_df: Optional[pd.DataFrame] = None) -> str:
        """Loads skill contract, runs planning, executes resolved tool, formats the output, and returns response string."""
        from boc_agent.runtime.trace.trace_builder import TraceBuilder
        builder = TraceBuilder()
        builder.start_stage("run")
        builder.set_user_query(question)

        skill = None
        skill_load_error = None
        try:
            skill = SkillLoader().get_skill()
        except Exception as e:
            skill_load_error = e

        # Create RuntimeContext for the turn containing our TraceBuilder
        context = RuntimeContext(
            question=question,
            reviewed_df=reviewed_df,
            skill=skill,
            trace_builder=builder
        )
        context.add_trace("Agent: Initialized RuntimeContext for the current execution turn.")

        if skill_load_error is not None or skill is None:
            err_msg = "Skill configuration is unavailable or invalid. Runtime execution has been blocked for safety."
            context.errors.append(str(skill_load_error or "Skill is None"))
            context.add_trace(f"Agent: Blocked execution due to missing or invalid skill configuration: {skill_load_error}")

            builder.add_reasoning_step(
                stage="Agent Startup",
                action="Load Skill Configuration",
                note=f"Failed loading skill config file: {skill_load_error or 'Skill is None'}"
            )
            builder.add_confidence_snapshot(
                stage="Agent Startup",
                confidence=0.00,
                note="Fails closed due to missing skill file"
            )
            builder.end_stage("run")

            trace = builder.build(
                response=err_msg,
                response_type="error",
                grounding_source="None",
                citations_used=[],
                skill_version="unknown",
                runtime_version="1.0.0",
                errors=context.errors
            )
            self.last_trace = trace
            BOCReviewAgent.last_trace = trace
            return err_msg

        # Add reasoning step for run initialization
        builder.add_reasoning_step(
            stage="Agent Runtime",
            action="Start Run",
            note="Beginning execution sequence"
        )

        try:
            # 1. Plan intent
            self.planner.plan(context)

            # 2. Execute tool
            raw_result = self.executor.execute(context)

            # 3. Build response
            final_response = self.response_builder.build_response(context, raw_result)

            # Determine response type and grounding source
            response_type = "markdown"
            grounding_source = "None"
            citations = []
            if context.intent == "rag":
                response_type = "rag_response"
                grounding_source = "repository_documentation"
                citations = list(set(re.findall(r'\b(?:docs/[\w.-]+\.md|README\.md|PROJECT_CONTEXT\.md|walkthrough\.md)\b', final_response)))
            elif context.intent == "tax_ruling":
                response_type = "refusal"
            elif context.intent == "unknown":
                response_type = "fallback"

            builder.end_stage("run")

            skill_ver = skill.metadata.version if skill else "unknown"
            trace = builder.build(
                response=final_response,
                response_type=response_type,
                grounding_source=grounding_source,
                citations_used=citations,
                skill_version=skill_ver,
                runtime_version="1.0.0",
                errors=context.errors
            )
            self.last_trace = trace
            BOCReviewAgent.last_trace = trace
            return final_response

        except Exception as e:
            err_msg = "An unexpected error occurred during agent runtime execution."
            context.errors.append(str(e))
            context.add_trace(f"Agent: Encountered runtime crash: {str(e)}")

            builder.add_reasoning_step(
                stage="Agent Runtime",
                action="Encountered Exception",
                note=f"Crash: {str(e)}"
            )
            builder.add_confidence_snapshot(
                stage="Formatter",
                confidence=0.00,
                note="Agent runtime failed on exception"
            )
            builder.end_stage("run")

            skill_ver = skill.metadata.version if skill else "unknown"
            trace = builder.build(
                response=err_msg,
                response_type="error",
                grounding_source="None",
                citations_used=[],
                skill_version=skill_ver,
                runtime_version="1.0.0",
                errors=context.errors
            )
            self.last_trace = trace
            BOCReviewAgent.last_trace = trace
            return err_msg
