import pandas as pd
from dataclasses import dataclass
from typing import Callable, List, Optional, Dict
from boc_agent.runtime.context import RuntimeContext
from boc_agent.chat.helpers import (
    handle_summary,
    handle_row_explanation,
    handle_review_queue_summary,
    handle_location_filter,
    handle_status_filter,
    handle_needs_documentation,
    handle_documentation_rag,
    handle_tax_refusal,
    handle_unknown
)

@dataclass
class RuntimeTool:
    name: str
    purpose: str
    supported_intents: List[str]
    handler: Callable[[RuntimeContext], str]
    mutating: bool = False
    requires_dataframe: bool = True
    requires_grounding: bool = False

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, RuntimeTool] = {}
        self._intent_to_tool: Dict[str, RuntimeTool] = {}
        self._register_default_tools()

    def register(self, tool: RuntimeTool) -> None:
        self._tools[tool.name] = tool
        for intent in tool.supported_intents:
            self._intent_to_tool[intent] = tool

    def get_tool_for_intent(self, intent: str) -> Optional[RuntimeTool]:
        return self._intent_to_tool.get(intent)

    def get_tool(self, name: str) -> Optional[RuntimeTool]:
        return self._tools.get(name)

    def _register_default_tools(self) -> None:
        self.register(RuntimeTool(
            name="dataframe_summary",
            purpose="Provides high-level metrics of the reviewed GL workbook",
            supported_intents=["summary"],
            handler=lambda ctx: handle_summary(ctx.reviewed_df),
            mutating=False,
            requires_dataframe=True
        ))
        
        self.register(RuntimeTool(
            name="row_explanation",
            purpose="Explains eligibility and suggested allocations for a specific ledger row",
            supported_intents=["row_explanation"],
            handler=lambda ctx: handle_row_explanation(ctx.question, ctx.reviewed_df),
            mutating=False,
            requires_dataframe=True
        ))
        
        self.register(RuntimeTool(
            name="review_queue_summary",
            purpose="Summarizes the human review queue or document issues",
            supported_intents=["review_queue_summary", "needs_documentation"],
            handler=lambda ctx: (
                handle_needs_documentation(ctx.reviewed_df) 
                if ctx.intent == "needs_documentation" 
                else handle_review_queue_summary(ctx.reviewed_df)
            ),
            mutating=False,
            requires_dataframe=True
        ))

        self.register(RuntimeTool(
            name="location_filter",
            purpose="Filters and breaks down suggestions by Location code (900, 910, 920)",
            supported_intents=["filter_location"],
            handler=lambda ctx: handle_location_filter(ctx.question, ctx.reviewed_df),
            mutating=False,
            requires_dataframe=True
        ))

        self.register(RuntimeTool(
            name="status_filter",
            purpose="Filters ineligible transaction suggestions",
            supported_intents=["filter_status", "ineligible_summary"],
            handler=lambda ctx: handle_status_filter(ctx.question, ctx.reviewed_df),
            mutating=False,
            requires_dataframe=True
        ))

        self.register(RuntimeTool(
            name="documentation_rag",
            purpose="Retrieves grounded documentation snippets from the local vector index",
            supported_intents=["rag"],
            handler=lambda ctx: handle_documentation_rag(ctx.question),
            mutating=False,
            requires_dataframe=False,
            requires_grounding=True
        ))

        self.register(RuntimeTool(
            name="tax_refusal",
            purpose="Refuses tax, legal, and advisory determination queries with disclaimers",
            supported_intents=["tax_ruling"],
            handler=lambda ctx: handle_tax_refusal(ctx.question, ctx.skill),
            mutating=False,
            requires_dataframe=False
        ))

        self.register(RuntimeTool(
            name="unknown_fallback",
            purpose="Gracefully handles unclassified queries",
            supported_intents=["unknown"],
            handler=lambda ctx: handle_unknown(),
            mutating=False,
            requires_dataframe=False
        ))
