from boc_agent.runtime.context import RuntimeContext
from boc_agent.chat.query_router import route_query

class Planner:
    def plan(self, context: RuntimeContext) -> None:
        """Classifies the user question into an intent and populates the context.intent and trace fields."""
        context.trace_builder.start_stage("planner")
        context.add_trace("Planner: Starting query routing and intent classification.")

        # Add reasoning step for routing entry
        context.trace_builder.add_reasoning_step(
            stage="Planner",
            action="Route Intent",
            note=f"Classifying user query: '{context.question}'"
        )

        intent = route_query(context.question)
        context.intent = intent

        # Mapping intent to capability and target tool
        intent_map = {
            "summary": ("aggregate_stats", "dataframe_summary", "Query matches summary/metrics keywords"),
            "row_explanation": ("dataframe_lookup", "row_explanation", "Query requests specific row details or vendor explanation"),
            "filter_location": ("dataframe_lookup", "location_filter", "Query requests location-based breakdown"),
            "ineligible_summary": ("dataframe_lookup", "status_filter", "Query matches ineligible status keywords"),
            "filter_status": ("dataframe_lookup", "status_filter", "Query matches status keywords"),
            "needs_documentation": ("dataframe_lookup", "review_queue_summary", "Query matches missing documentation keywords"),
            "review_queue_summary": ("aggregate_stats", "review_queue_summary", "Query requests human review queue details"),
            "rag": ("documentation_rag", "documentation_rag", "Query asks about setup, policy, or system walkthrough"),
            "tax_ruling": ("tax_determinations", "tax_refusal", "Query matched tax credit ruling/disclaimer triggers"),
            "unknown": ("unknown", "unknown_fallback", "Query did not match any routing rules")
        }

        capability, tool_name, reason = intent_map.get(
            intent,
            ("unknown", "unknown_fallback", "Unmapped intent fallback")
        )

        # Set planner trace values
        context.trace_builder.set_planner(
            original_query=context.question,
            intent=intent,
            reason=reason,
            capability=capability,
            tool_selected=tool_name
        )

        # Add confidence checkpoint
        confidence_map = {
            "tax_ruling": 1.00,
            "row_explanation": 0.99,
            "summary": 0.98,
            "rag": 0.95,
            "filter_location": 0.94,
            "review_queue_summary": 0.93,
            "ineligible_summary": 0.92,
            "needs_documentation": 0.91,
            "unknown": 0.50
        }
        confidence = confidence_map.get(intent, 0.90)
        context.trace_builder.add_confidence_snapshot(
            stage="Planner",
            confidence=confidence,
            note=f"Planner classified intent as '{intent}'"
        )

        context.add_trace(f"Planner: Successfully resolved intent to '{intent}'.")
        context.trace_builder.end_stage("planner")
