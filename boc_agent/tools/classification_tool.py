from boc_agent.schemas.transaction import Transaction
from boc_agent.tools.allocation_tool import classify_payee_type
from typing import Tuple

def classify_transaction(tx: Transaction) -> Tuple[str, str]:
    """Suggests the payee structure and cost category for a transaction.
    
    Returns:
        Tuple[str, str]: (payee_type, cost_category)
    """
    payee_type = classify_payee_type(tx)
    
    desc = (tx.description or "").lower()
    payee = (tx.vendor_name or "").lower()
    
    if "meal" in desc or "catering" in desc or "craft" in desc or "per diem" in desc:
        cost_category = "Meals"
    elif "travel" in desc or "flight" in desc or "hotel" in desc:
        cost_category = "Travel"
    elif payee_type in ["Employee", "Loan-out", "Individual"] or "payroll" in desc:
        cost_category = "Labor"
    else:
        cost_category = "Spend"
        
    return payee_type, cost_category
