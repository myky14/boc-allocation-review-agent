from boc_agent.schemas.transaction import TransactionRecord
from boc_agent.schemas.review_result import ReviewResult
from boc_agent.tools.allocation_tool import review_transaction

def suggest_allocation(tx: TransactionRecord) -> ReviewResult:
    """Delegates directly to the deterministic rule engine to suggest allocations.
    
    Guarantees suggested_allocation_column, amount_percentage, reference_rule, and rationale
    are preserved exactly from the deterministic rule engine.
    """
    return review_transaction(tx)
