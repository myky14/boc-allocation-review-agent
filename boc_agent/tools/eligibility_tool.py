from boc_agent.schemas.transaction import Transaction

def evaluate_eligibility(tx: Transaction, payee_type: str, cost_category: str) -> str:
    """Suggests the eligibility status for the transaction based on workbook details."""
    # Placeholder eligibility evaluation
    desc = (tx.description or "").lower()
    address = (tx.address or "").lower()
    
    # If explicitly out of Canada, it's ineligible for provincial/federal regional credits 
    # (though it maps to "Out of Canada costs" allocation bucket)
    if "out of canada" in desc or "us spend" in desc or "usa" in address:
        return "Ineligible"
        
    # Check if required province matches application province
    if tx.application_province == "Ontario" and "ontario" not in address and "on" not in address:
        # Might be Federal or ineligible for Ontario
        pass
        
    return "Eligible"
