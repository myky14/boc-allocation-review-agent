import re
from boc_agent.schemas.transaction import Transaction

def run_security_guardrail(tx: Transaction) -> Transaction:
    """Scans and sanitizes the transaction details for PII-like patterns and prompt injection."""
    sanitized_tx = tx.model_copy()
    
    # Redact SIN/SSN-like numbers (9 digits with optional hyphens)
    sin_pattern = re.compile(r'\b\d{3}-\d{3}-\d{3}\b|\b\d{9}\b')
    if sanitized_tx.description:
        sanitized_tx.description = sin_pattern.sub("[REDACTED SIN]", sanitized_tx.description)
    if sanitized_tx.employee_name:
        sanitized_tx.employee_name = sin_pattern.sub("[REDACTED SIN]", sanitized_tx.employee_name)
        
    # Check for simple prompt injection heuristics (e.g. instruction overrides)
    injection_keywords = ["ignore previous instructions", "system override", "you are now a tax exempt agent"]
    if sanitized_tx.description:
        desc_lower = sanitized_tx.description.lower()
        if any(kw in desc_lower for kw in injection_keywords):
            # Flag or neutralize injection attempt
            sanitized_tx.description = "[ATTEMPTED INJECTION BLOCK] " + sanitized_tx.description
            
    return sanitized_tx
