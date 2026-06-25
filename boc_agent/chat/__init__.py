from boc_agent.chat.query_router import route_query

def __getattr__(name: str):
    if name == "ReviewConversationAssistant":
        from boc_agent.chat.assistant import ReviewConversationAssistant
        return ReviewConversationAssistant
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["route_query", "ReviewConversationAssistant"]
