from boc_agent.runtime.context import RuntimeContext
from boc_agent.chat.query_router import route_query

class Planner:
    def plan(self, context: RuntimeContext) -> None:
        """Classifies the user question into an intent and populates the context.intent field."""
        context.add_trace("Planner: Starting query routing and intent classification.")
        intent = route_query(context.question)
        context.intent = intent
        context.add_trace(f"Planner: Successfully resolved intent to '{intent}'.")
