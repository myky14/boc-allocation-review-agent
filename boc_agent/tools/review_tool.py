from boc_agent.schemas.transaction import TransactionRecord
from boc_agent.schemas.review_result import ReviewResult
from typing import List, Dict, Any

def make_review_decision(
    tx: TransactionRecord,
    classification_metadata: Dict[str, Any],
    security_warnings: List[str],
    allocation_result: ReviewResult
) -> ReviewResult:
    """Combines classification metadata, security guardrail warning flags, and eligibility/allocation outcomes
    into the final ReviewResult object.
    
    If security warnings are found:
      - The review_status must be overridden to 'Needs Human Review'.
      - The prompt-injection flags from the guardrail check should be appended to the rationale field.
      - The confidence_score is reduced/set to 0.0.
    """
    # Start with a copy of the deterministic allocation result
    final_result = allocation_result.model_copy()
    
    # If there are security warnings, override review status and confidence, and append to rationale
    if security_warnings:
        final_result.review_status = "Needs Human Review"
        final_result.confidence_score = 0.0
        
        warning_str = " | ".join(security_warnings)
        if final_result.rationale:
            final_result.rationale = f"{final_result.rationale} | {warning_str}"
        else:
            final_result.rationale = warning_str
            
    return final_result

