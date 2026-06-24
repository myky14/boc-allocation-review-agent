from boc_agent.schemas.transaction import TransactionRecord
from boc_agent.schemas.review_result import ReviewResult
from typing import Dict, Any, Optional

def evaluate_eligibility(tx: TransactionRecord, deterministic_result: Optional[ReviewResult] = None) -> Dict[str, Any]:
    """Exposes structured eligibility information from the deterministic review result.
    
    Ensures it does not contradict the rule engine output.
    """
    if deterministic_result is None:
        from boc_agent.tools.allocation_tool import review_transaction
        deterministic_result = review_transaction(tx)
        
    return {
        "eligibility_status": deterministic_result.eligibility_status,
        "is_eligible": deterministic_result.eligibility_status == "Eligible",
        "is_ineligible": deterministic_result.eligibility_status == "Ineligible",
        "needs_review": deterministic_result.eligibility_status == "Needs Review",
        "confidence_score": deterministic_result.confidence_score
    }
