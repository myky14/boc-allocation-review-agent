from boc_agent.schemas.transaction import TransactionRecord
from boc_agent.schemas.review_result import ReviewResult
from boc_agent.tools.allocation_tool import review_transaction

class Orchestrator:
    """Orchestrates the local-first execution flow for GL transaction review.
    
    Currently wraps the deterministic rule engine.
    """
    
    def process_transaction(self, tx: TransactionRecord) -> ReviewResult:
        """Processes a single transaction through the deterministic allocation rule engine."""
        return review_transaction(tx)
