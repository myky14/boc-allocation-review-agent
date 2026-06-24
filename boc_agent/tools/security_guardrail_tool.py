import re
from typing import List
from boc_agent.schemas.transaction import TransactionRecord

def scan_prompt_injection(tx: TransactionRecord) -> List[str]:
    """Scans the transaction description fields for prompt injection indicators.
    
    Returns:
        List[str]: List of warning flags or empty list if clean.
    """
    warnings = []
    override_keywords = [
        "ignore previous rules",
        "ignore the rules",
        "mark everything eligible",
        "mark as eligible",
        "override allocation",
        "override eligibility",
        "system override",
        "ignore rules",
        "make eligible"
    ]
    
    desc = (tx.description or "").lower()
    add_desc = (tx.additional_description or "").lower()
    
    for kw in override_keywords:
        if kw in desc or kw in add_desc:
            warnings.append(f"Potential prompt injection detected: '{kw}'")
            
    return warnings
