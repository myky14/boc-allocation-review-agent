import pandas as pd
from typing import Optional

class ReviewConversationAssistant:
    """Conversational assistant for explaining and querying the reviewed GL workbook.

    This is a local-first, deterministic Q&A helper. Phase 8.1 implements
    dataframe Q&A for workbook transaction inquiries, and Phase 8.2 adds
    local deterministic documentation RAG for general policy and setup queries.
    It contains no LLMs and no mutating database operations.

    In Phase 9.1, it has been refactored into a thin compatibility wrapper
    delegating to the ADK-inspired BOCReviewAgent.
    """
    last_trace = None

    def __init__(self):
        self.last_trace = None

    def answer(self, question: str, reviewed_df: Optional[pd.DataFrame] = None) -> str:
        """Processes the question and returns a grounded answer by delegating to BOCReviewAgent."""
        from boc_agent.runtime.agent import BOCReviewAgent
        agent = BOCReviewAgent()
        response = agent.run(question, reviewed_df)
        self.last_trace = agent.last_trace
        ReviewConversationAssistant.last_trace = agent.last_trace
        return response
