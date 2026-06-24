from boc_agent.schemas.transaction import TransactionRecord
from boc_agent.tools.allocation_tool import (
    is_payroll_processor,
    is_partnership,
    is_vice_canada,
    is_labor_transaction,
    classify_payee_type,
    get_ep_suffix
)
from typing import Dict, Any

def classify_transaction(tx: TransactionRecord) -> Dict[str, Any]:
    """Extracts structured metadata classification around a transaction.
    
    Returns:
        Dict[str, Any]: Classification details including province, location class, cost family, and evidence.
    """
    app_prov = tx.application_province or "Unknown"
    
    loc = str(tx.location).strip() if tx.location else ""
    if loc == "900":
        loc_class = "in-province"
    elif loc == "910":
        loc_class = "in-Canada-outside-province"
    elif loc == "920":
        loc_class = "out-of-Canada"
    else:
        loc_class = "missing/unknown"
        
    desc_lower = (tx.description or "").lower()
    acc_name_lower = (tx.account_name or "").lower()
    is_meal = any(kw in desc_lower or kw in acc_name_lower for kw in ["catering", "craft", "per diem", "perdiem", "meal", "meals"])
    
    if is_meal:
        cost_family = "meal"
    elif is_vice_canada(tx.vendor_name) or is_vice_canada(tx.employee):
        cost_family = "VICE Canada labour" if is_labor_transaction(tx) else "spend/property"
    elif is_payroll_processor(tx.vendor_name):
        cost_family = "payroll processor"
    elif is_partnership(tx.vendor_name) or classify_payee_type(tx) == "Partnership":
        cost_family = "partnership"
    elif is_labor_transaction(tx):
        cost_family = "labour"
    else:
        ep_suffix = get_ep_suffix(tx.ep)
        if ep_suffix in {40, 50, 60}:
            cost_family = "spend/property"
        else:
            cost_family = "unknown"
            
    has_employee = bool(tx.employee and str(tx.employee).strip() != "" and str(tx.employee).lower() != "nan")
    has_corp = bool(tx.loan_out_corp and str(tx.loan_out_corp).strip() != "" and str(tx.loan_out_corp).lower() != "nan")
    has_tax_id = bool(tx.tax_id and str(tx.tax_id).strip() != "")
    has_province = bool(tx.province and str(tx.province).strip() != "")
    has_location = bool(tx.location and str(tx.location).strip() != "")
    has_ep = bool(tx.ep and str(tx.ep).strip() != "")
    
    return {
        "application_province": app_prov,
        "location_class": loc_class,
        "cost_family": cost_family,
        "evidence_flags": {
            "has_employee": has_employee,
            "has_loan_out_corp": has_corp,
            "has_tax_id": has_tax_id,
            "has_province": has_province,
            "has_location": has_location,
            "has_ep": has_ep
        }
    }
