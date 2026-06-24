from boc_agent.schemas.transaction import Transaction
from typing import Tuple

def make_review_decision(
    tx: Transaction,
    payee_type: str,
    cost_category: str,
    eligibility_status: str,
    suggested_allocation: str,
    amount_percentage: float
) -> Tuple[float, str, str, str]:
    """Evaluates the audit state and determines confidence, review status, reasoning, and reference rule.
    
    Returns:
        Tuple[float, str, str, str]: (confidence_score, review_status, reasoning, reference_rule)
    """
    confidence = 1.0
    reasons = []
    rule = "RULE_STANDARD_MAPPING"
    
    # 1. Check for missing required fields (raises human review requirement, reduces confidence)
    missing_fields = []
    if not tx.application_province:
        missing_fields.append("application_province")
    if not tx.location:
        missing_fields.append("location")
    if not tx.ep:
        missing_fields.append("ep")
    if not tx.vendor_name:
        missing_fields.append("vendor_name")
    if not tx.tax_id:
        missing_fields.append("tax_id")
    if not tx.address:
        missing_fields.append("address")
        
    if missing_fields:
        confidence -= 0.15 * len(missing_fields)
        reasons.append(f"Missing required fields: {', '.join(missing_fields)}")
        rule = "RULE_MISSING_FIELDS_WARNING"
        
    # 2. Check special category flags
    if "VICE STUDIO CANADA" in (tx.vendor_name or "").upper():
        reasons.append("VICE Studio Canada labor audit match applied.")
        rule = "RULE_VICE_CANADA_SPECIAL"
        
    if "multi-share" in (tx.description or "").lower():
        reasons.append("Multi-share labor contract detected.")
        rule = "RULE_MULTI_SHARE_FEE_SPLIT"
        
    # Cap confidence
    confidence = max(0.1, min(1.0, confidence))
    
    # Review status decision
    if confidence < 0.85 or "missing" in "".join(reasons).lower():
        review_status = "Needs Human Review"
    else:
        review_status = "Approved"
        
    if not reasons:
        reasons.append("Normal transaction mapped successfully.")
        
    return confidence, review_status, " | ".join(reasons), rule
