import re
import pandas as pd
from typing import Tuple, Optional, Any
from boc_agent.schemas.transaction import TransactionRecord
from boc_agent.schemas.review_result import ReviewResult

# Allowed Ep codes
ALLOWED_EP_CODES = {40, 41, 42, 44, 45, 50, 51, 52, 54, 55, 60, 61, 62, 64, 65}

# Allowed Location codes
ALLOWED_LOCATION_CODES = {900, 910, 920}

def is_payroll_processor(vendor_name: str) -> bool:
    """Helper to detect if a vendor is a payroll processor."""
    if not vendor_name:
        return False
    vn = str(vendor_name).strip().lower()
    words = re.findall(r'\b\w+\b', vn)
    if "payroll" in words or "greenslate" in words or "caps" in words:
        return True
    if any(x in vn for x in ["cast & crew", "cast and crew", "union street"]):
        return True
    return False

def is_partnership(vendor_name: str) -> bool:
    """Helper to detect partnership indicators in vendor name."""
    if not vendor_name:
        return False
    vn = str(vendor_name).strip().lower()
    words = re.findall(r'\b\w+\b', vn)
    return any(x in words for x in ["partnership", "partners", "llp", "lp"])

def is_vice_canada(vendor_name: str) -> bool:
    """Helper to detect normalized variants of VICE."""
    if not vendor_name:
        return False
    vn = str(vendor_name).strip().lower()
    if vn in ["vice", "vice studio", "vice studio canada", "vice canada"]:
        return True
    words = re.findall(r'\b\w+\b', vn)
    return "vice" in words

def get_ep_suffix(ep: Any) -> Optional[int]:
    """Extracts the last two digits of the Ep code."""
    if pd.isna(ep) or ep is None or str(ep).strip() == "":
        return None
    try:
        val = int(float(ep))
        return val % 100
    except (ValueError, TypeError):
        return None

def is_labor_transaction(tx: TransactionRecord) -> bool:
    """Helper to determine if a transaction is labor-related based on available fields."""
    has_employee = tx.employee and str(tx.employee).strip() != "" and str(tx.employee).lower() != "nan"
    has_corp = tx.loan_out_corp and str(tx.loan_out_corp).strip() != "" and str(tx.loan_out_corp).lower() != "nan"
    
    if has_employee or has_corp:
        return True
        
    ep_suffix = get_ep_suffix(tx.ep)
    if ep_suffix in {41, 51, 61, 42, 52, 62, 44, 54, 64, 45, 55, 65}:
        return True
        
    desc_lower = (tx.description or "").lower()
    acc_name_lower = (tx.account_name or "").lower()
    
    # We exclude spend-like terms explicitly first unless employee/corp or labor Ep is present
    exclude_terms = ["software", "platform", "collaboration", "equipment", "rental", "facility", "rooms", "room"]
    
    # Standard labor keywords (whole words only)
    labor_keywords = {
        "salary", "crew", "labor", "assistant", "operator", "gaffer", 
        "payroll", "services", "director", "producer", "dop", "fringe", "consultant",
        "wages", "performer", "actor", "contractor"
    }
    
    desc_words = set(re.findall(r'\b\w+\b', desc_lower))
    acc_words = set(re.findall(r'\b\w+\b', acc_name_lower))
    
    if desc_words.intersection(labor_keywords) or acc_words.intersection(labor_keywords):
        if any(term in desc_words or term in acc_words for term in exclude_terms):
            return False
        return True
        
    return False

def classify_payee_type(tx: TransactionRecord) -> str:
    """Classifies the payee type based on the presence of Employee, Loan out corp, and description."""
    effective_vendor = tx.vendor_name
    has_employee = tx.employee and str(tx.employee).strip() != "" and str(tx.employee).lower() != "nan"
    has_corp = tx.loan_out_corp and str(tx.loan_out_corp).strip() != "" and str(tx.loan_out_corp).lower() != "nan"
    
    # If payroll processor, use Employee as effective payee info
    if is_payroll_processor(effective_vendor) and has_employee:
        effective_vendor = tx.employee
        
    if is_partnership(effective_vendor):
        return "Partnership"
        
    if has_corp:
        return "Loan-out"
        
    if has_employee:
        return "Employee"
        
    desc_lower = (tx.description or "").lower()
    payee_lower = (effective_vendor or "").lower()
    
    if "partnership" in desc_lower or "partnership" in payee_lower or "llp" in payee_lower or " lp " in f" {payee_lower} ":
        return "Partnership"
        
    if is_labor_transaction(tx):
        return "Individual"
        
    return "Vendor"

def review_transaction(tx: TransactionRecord) -> ReviewResult:
    """Reviews a single TransactionRecord using the deterministic accounting rules engine.
    
    Args:
        tx: TransactionRecord data row.
        
    Returns:
        ReviewResult detailing the suggested allocation, amount percentage, and review flags.
    """
    reasons = []
    needs_review = False
    province_conflict = False
    
    # Pre-checks for required variables
    has_employee = tx.employee and str(tx.employee).strip() != "" and str(tx.employee).lower() != "nan"
    has_corp = tx.loan_out_corp and str(tx.loan_out_corp).strip() != "" and str(tx.loan_out_corp).lower() != "nan"
    is_labor = is_labor_transaction(tx)
    payee_type = classify_payee_type(tx)
    ep_suffix = get_ep_suffix(tx.ep)
    
    # A. Province missing checks
    if not tx.application_province or pd.isna(tx.application_province) or str(tx.application_province).strip() == "":
        needs_review = True
        reasons.append("Application Province missing")
        
    if not tx.province or pd.isna(tx.province) or str(tx.province).strip() == "":
        needs_review = True
        reasons.append("Payee Province missing")
        
    # B. Location missing/invalid check
    loc_val = None
    if not tx.location or pd.isna(tx.location) or str(tx.location).strip() == "":
        needs_review = True
        reasons.append("Location code missing")
    else:
        try:
            loc_val = int(float(tx.location))
            if loc_val not in ALLOWED_LOCATION_CODES:
                needs_review = True
                reasons.append(f"Invalid Location code: {tx.location}")
        except (ValueError, TypeError):
            needs_review = True
            reasons.append(f"Invalid Location code format: {tx.location}")
        
    # C. Ep missing/invalid check
    if ep_suffix is None:
        needs_review = True
        reasons.append("Ep code missing")
    elif ep_suffix not in ALLOWED_EP_CODES:
        needs_review = True
        reasons.append(f"Invalid Ep code suffix: {tx.ep}")
        
    # D. Labor missing Tax ID check
    if is_labor and (not tx.tax_id or pd.isna(tx.tax_id) or str(tx.tax_id).strip() == ""):
        needs_review = True
        reasons.append("Labor transaction missing Tax ID")
        
    # E. Payroll processor validation
    if is_payroll_processor(tx.vendor_name):
        if not has_employee:
            needs_review = True
            reasons.append("Payroll processor vendor without Employee detail")
        else:
            reasons.append(f"Payroll processor detected; Employee '{tx.employee}' used as effective payee")
        
    # Country clean-up
    country_clean = str(tx.country).strip().lower() if tx.country else ""
    is_country_canada = country_clean in ["canada", "can", "ca"]
    is_country_empty = country_clean == ""
    is_country_foreign = not is_country_canada and not is_country_empty

    # Country / Location conflict
    if is_country_foreign and loc_val in [900, 910]:
        needs_review = True
        reasons.append(f"Vendor country '{tx.country}' and cost location '{tx.location}' conflict")

    # F. Conflicting province evidence check (App Province vs Payee Province)
    if tx.application_province and tx.province and pd.notna(tx.application_province) and pd.notna(tx.province):
        app_prov = str(tx.application_province).strip().lower()
        payee_prov = str(tx.province).strip().lower()
        
        prov_map = {
            "on": "ontario", "ontario": "ontario",
            "qc": "quebec", "quebec": "quebec", "qb": "quebec",
            "bc": "british columbia", "british columbia": "british columbia",
            "ab": "alberta", "alberta": "alberta",
            "ns": "nova scotia", "nova scotia": "nova scotia",
            "mb": "manitoba", "manitoba": "manitoba",
            "sk": "saskatchewan", "saskatchewan": "saskatchewan",
            "nb": "new brunswick", "new brunswick": "new brunswick",
            "nl": "newfoundland", "newfoundland": "newfoundland",
            "pe": "prince edward island", "prince edward island": "prince edward island",
        }
        
        std_app = prov_map.get(app_prov, app_prov)
        std_payee = prov_map.get(payee_prov, payee_prov)
        
        if std_app != std_payee:
            needs_review = True
            province_conflict = True
            reasons.append(
                "Payee province differs from application province; provincial eligibility requires review. "
                "Federal treatment may still apply depending on available evidence."
            )

    # G. Ep Code Conflict Checks
    if ep_suffix is not None:
        # Spend codes vs Employee/Corp presence
        if ep_suffix in {40, 50, 60} and (has_employee or has_corp):
            needs_review = True
            reasons.append(f"Ep code indicates Spend ({ep_suffix}) but Employee/Corp is populated")
            
        # Salary codes vs Corp presence
        if ep_suffix in {41, 51, 61} and has_corp:
            needs_review = True
            reasons.append(f"Ep code indicates Salary ({ep_suffix}) but Loan out corp is populated")
            
        # Loan-out codes vs no Corp presence
        if ep_suffix in {42, 52, 62} and not has_corp and has_employee:
            needs_review = True
            reasons.append(f"Ep code indicates Loan-out ({ep_suffix}) but no Loan out corp is populated")
            
        # Multi-share/fringe codes vs non-labor
        if ep_suffix in {44, 54, 64} and not is_labor:
            needs_review = True
            reasons.append(f"Ep code indicates Multi-share ({ep_suffix}) but transaction is not labor-related")

        # Ep Individual/Partnership (45, 55, 65) but classification is Loan-out
        if ep_suffix in {45, 55, 65} and payee_type == "Loan-out":
            needs_review = True
            reasons.append(f"Ep code indicates Individual/Partnership ({ep_suffix}) but payee classified as Loan-out")

        # Ep Salary (41, 51, 61) but classification is Partnership or Loan-out
        if ep_suffix in {41, 51, 61} and payee_type in ["Partnership", "Loan-out"]:
            needs_review = True
            reasons.append(f"Ep code indicates Salary ({ep_suffix}) but payee classified as {payee_type}")

        # Ep Loan-out (42, 52, 62) but classification is Employee or Partnership
        if ep_suffix in {42, 52, 62} and payee_type in ["Employee", "Partnership"]:
            needs_review = True
            reasons.append(f"Ep code indicates Loan-out ({ep_suffix}) but payee classified as {payee_type}")

        # Spend Ep with labor transaction
        if ep_suffix in {40, 50, 60} and is_labor:
            needs_review = True
            reasons.append(f"Ep code indicates Spend ({ep_suffix}) but transaction is labor-related")

    # H. Partnership Tax ID check
    if payee_type == "Partnership" and (not tx.tax_id or pd.isna(tx.tax_id) or str(tx.tax_id).strip() == ""):
        needs_review = True
        reasons.append("Partnership transaction missing Tax ID")

    # 3. Core Rule Matching & Allocation Mapping
    desc_lower = (tx.description or "").lower()
    acc_name_lower = (tx.account_name or "").lower()
    
    suggested_allocation = "Fed non eligible"
    amount_percentage = 100.0
    eligibility_status = "Eligible"
    reference_rule = "RULE_DEFAULT"
    secondary_note = None
    
    is_quebec = (tx.application_province == "Quebec")

    # ------------------ QUEBEC ALLOCATION LOGIC ------------------
    if is_quebec:
        # Location 920 takes absolute priority over needs_review override
        if loc_val == 920:
            suggested_allocation = "Quebec non-qualified"
            amount_percentage = 100.0
            eligibility_status = "Ineligible"
            reference_rule = "RULE_QUEBEC_NON_QUALIFIED"
            reasons.append("Quebec non-qualified cost (Location 920)")

        elif needs_review:
            suggested_allocation = "Quebec needs review"
            amount_percentage = 100.0
            eligibility_status = "Needs Review"
            reference_rule = "RULE_QUEBEC_NEEDS_REVIEW"
            reasons.append("Quebec row flagged for human review")
        
        elif is_country_foreign or ("out of canada" in desc_lower or "us spend" in desc_lower or "foreign supplier" in desc_lower):
            suggested_allocation = "Quebec non-qualified"
            amount_percentage = 100.0
            eligibility_status = "Ineligible"
            reference_rule = "RULE_QUEBEC_NON_QUALIFIED"
            reasons.append("Quebec non-qualified cost (foreign vendor or non-qualified evidence)")
            
        elif loc_val == 910 and is_country_canada and is_labor:
            # Suggest appropriate Federal labor category
            if payee_type == "Loan-out":
                suggested_allocation = "Fed loan-out"
                reference_rule = "RULE_FED_LOAN_OUT_FALLBACK"
            elif payee_type == "Individual":
                suggested_allocation = "Fed individual"
                reference_rule = "RULE_FED_INDIVIDUAL_FALLBACK"
            elif payee_type == "Partnership":
                suggested_allocation = "Fed partnership"
                reference_rule = "RULE_FED_PARTNERSHIP_FALLBACK"
            else:
                suggested_allocation = "Fed salary"
                reference_rule = "RULE_FED_SALARY_FALLBACK"
            
            # Check multi-share split
            if ep_suffix in {44, 54, 64} or "multi-share" in desc_lower or "fringe" in desc_lower:
                suggested_allocation = "Fed multi-share"
                amount_percentage = 65.0
                secondary_note = "remaining 35% should be reviewed as spend/non-labor treatment for MVP purposes"
                reasons.append("This is an internal BOC allocation convention based on the synthetic workbook Ep code.")
                reference_rule = "RULE_FED_MULTI_SHARE_FALLBACK"
            else:
                amount_percentage = 100.0
                
            eligibility_status = "Eligible"
            reasons.append("Canadian payee outside application province; suggested federal treatment.")
            
        elif loc_val == 910 and is_country_canada and not is_labor:
            suggested_allocation = "Quebec non-qualified"
            amount_percentage = 100.0
            eligibility_status = "Ineligible"
            reference_rule = "RULE_QUEBEC_NON_QUALIFIED"
            reasons.append("Canadian spend outside application province (Quebec non-qualified)")
            
        elif loc_val == 900 and is_country_canada and is_labor:
            suggested_allocation = "Quebec qualified labour"
            reference_rule = "RULE_QUEBEC_QUALIFIED_LABOUR"
            reasons.append("Quebec production accounting context and internal Ep mapping applied")
            
            # Check for VICE labor
            if is_vice_canada(tx.vendor_name) or is_vice_canada(tx.employee):
                secondary_note = "Payee appears to be VICE Canada labor; Quebec-specific dedicated VICE bucket is not implemented in this MVP."
                
            # Check for multi-share
            if ep_suffix in {44, 54, 64} or "multi-share" in desc_lower or "fringe" in desc_lower:
                amount_percentage = 65.0
                secondary_note = "remaining 35% should be reviewed as spend/non-labor treatment for MVP purposes"
                reasons.append("This is an internal BOC allocation convention based on the synthetic workbook Ep code.")
            else:
                amount_percentage = 100.0
                
            eligibility_status = "Eligible"
            
        elif loc_val == 900 and is_country_canada and not is_labor:
            # Check for meals/catering
            if any(kw in desc_lower for kw in ["catering", "craft", "craft service", "per diem", "perdiem", "meal", "meals"]) or any(kw in acc_name_lower for kw in ["catering", "craft", "craft service", "per diem", "perdiem", "meal", "meals"]):
                suggested_allocation = "Meal (catering, craft, per diem)"
                amount_percentage = 100.0
                eligibility_status = "Eligible"
                reference_rule = "RULE_MEAL_CATERING"
                reasons.append("Meal/catering review bucket, not a final tax credit determination.")
            else:
                suggested_allocation = "Quebec qualified properties / spend"
                amount_percentage = 100.0
                eligibility_status = "Eligible"
                reference_rule = "RULE_QUEBEC_SPEND"
                reasons.append("Quebec qualified spend / properties matched")
                
        else:
            suggested_allocation = "Quebec non-qualified"
            amount_percentage = 100.0
            eligibility_status = "Ineligible"
            reference_rule = "RULE_QUEBEC_NON_QUALIFIED"

    # ------------------ ONTARIO / FEDERAL ALLOCATION LOGIC ------------------
    else:
        # Priority 1: Out of Canada (Location 920 or foreign payee takes priority)
        if loc_val == 920 or is_country_foreign or ("out of canada" in desc_lower or "us spend" in desc_lower or "foreign supplier" in desc_lower):
            suggested_allocation = "Out of Canada costs"
            amount_percentage = 100.0
            eligibility_status = "Ineligible"
            reference_rule = "RULE_OUT_OF_CANADA"
            reasons.append("Out of Canada cost or foreign payee identified")

        # Priority 2: Meal / Catering / Craft / Per Diem rule
        elif any(kw in desc_lower for kw in ["catering", "craft", "craft service", "per diem", "perdiem", "meal", "meals"]) or any(kw in acc_name_lower for kw in ["catering", "craft", "craft service", "per diem", "perdiem", "meal", "meals"]):
            suggested_allocation = "Meal (catering, craft, per diem)"
            amount_percentage = 100.0
            if loc_val not in [900, 910] or not tx.location:
                eligibility_status = "Needs Review"
            else:
                eligibility_status = "Eligible"
            reference_rule = "RULE_MEAL_CATERING"
            reasons.append("Meal/catering review bucket, not a final tax credit determination.")

        # Priority 3: VICE Studio Canada labor rule
        elif is_vice_canada(tx.vendor_name) or is_vice_canada(tx.employee):
            if is_labor:
                if tx.application_province == "Ontario" and loc_val == 900 and not province_conflict:
                    suggested_allocation = "ONT labor paid to VICE Canada"
                else:
                    suggested_allocation = "Fed labor paid to VICE Canada"
                amount_percentage = 100.0
                eligibility_status = "Eligible"
                reference_rule = "RULE_VICE_CANADA_LABOR"
                reasons.append("VICE Canada labor transaction matched")
            else:
                suggested_allocation = "Fed non eligible"
                amount_percentage = 100.0
                eligibility_status = "Ineligible"
                reference_rule = "RULE_VICE_CANADA_NON_LABOR"
                reasons.append("VICE Canada spend (non-labor)")

        # Priority 4: Multi-share / Fringe splits
        elif ep_suffix in {44, 54, 64} or "multi-share" in desc_lower or "fringe" in desc_lower or "multi-share" in acc_name_lower:
            if tx.application_province == "Ontario" and loc_val == 900 and not province_conflict:
                suggested_allocation = "ONT labor multi-share (44)"
            else:
                suggested_allocation = "Fed multi-share"
            amount_percentage = 65.0
            secondary_note = "remaining 35% should be reviewed as spend/non-labor treatment for MVP purposes"
            reasons.append("This is an internal BOC allocation convention based on the synthetic workbook Ep code.")
            eligibility_status = "Eligible"
            reference_rule = "RULE_MULTI_SHARE"

        # Priority 5: Partnership
        elif payee_type == "Partnership" or (ep_suffix in {45, 55, 65} and is_partnership(tx.vendor_name)):
            suggested_allocation = "Fed partnership"
            amount_percentage = 100.0
            eligibility_status = "Eligible"
            reference_rule = "RULE_PARTNERSHIP"
            reasons.append("Partnership supplier cost suggested")

        # Priority 6: Labor Categories
        elif is_labor:
            if payee_type == "Loan-out":
                if tx.application_province == "Ontario" and loc_val == 900 and not province_conflict:
                    suggested_allocation = "ONT loan-out corporation (42)"
                else:
                    suggested_allocation = "Fed loan-out"
                amount_percentage = 100.0
                eligibility_status = "Eligible"
                reference_rule = "RULE_LOAN_OUT"
                reasons.append("Loan-out corporation labor suggested")
                
            elif payee_type == "Individual":
                if tx.application_province == "Ontario" and loc_val == 900 and not province_conflict:
                    suggested_allocation = "ONT individual (45)"
                else:
                    suggested_allocation = "Fed individual"
                amount_percentage = 100.0
                eligibility_status = "Eligible"
                reference_rule = "RULE_INDIVIDUAL"
                reasons.append("Individual contractor labor suggested")
                
            else:
                if tx.application_province == "Ontario" and loc_val == 900 and not province_conflict:
                    suggested_allocation = "Ontario Salary (41)"
                else:
                    suggested_allocation = "Fed salary"
                amount_percentage = 100.0
                eligibility_status = "Eligible"
                reference_rule = "RULE_SALARY"
                reasons.append("Direct salary employee labor suggested")

        # Priority 7: Spend / Corporate Suppliers
        else:
            if tx.application_province == "Ontario" and loc_val == 900 and not province_conflict:
                suggested_allocation = "Ontario Spend (40)"
                amount_percentage = 100.0
                eligibility_status = "Eligible"
                reference_rule = "RULE_SPEND"
                reasons.append("Ontario Creates eligible spend suggested")
            else:
                if loc_val == 910:
                    reasons.append("Spend Location is 910 (Canadian outside application province)")
                suggested_allocation = "Fed non eligible"
                amount_percentage = 100.0
                eligibility_status = "Ineligible"
                reference_rule = "RULE_NON_ONTARIO_SPEND"
                reasons.append("Non-Ontario spend treatment suggested")

        # Post-rule override for province conflicts in Ontario/Fed
        if province_conflict and suggested_allocation != "Out of Canada costs":
            eligibility_status = "Needs Review"
            if suggested_allocation.startswith("ONT ") or suggested_allocation.startswith("Ontario "):
                fed_map = {
                    "Ontario Salary (41)": "Fed salary",
                    "ONT loan-out corporation (42)": "Fed loan-out",
                    "ONT individual (45)": "Fed individual",
                    "ONT labor multi-share (44)": "Fed multi-share",
                    "ONT labor paid to VICE Canada": "Fed labor paid to VICE Canada",
                    "Ontario Spend (40)": "Fed non eligible"
                }
                suggested_allocation = fed_map.get(suggested_allocation, "Fed non eligible")

        # Override eligibility for missing required fields on normal mappings
        if needs_review and suggested_allocation != "Out of Canada costs":
            eligibility_status = "Needs Review"

    review_status = "Needs Human Review" if needs_review else "Approved"
    confidence_score = 0.70 if needs_review else 1.00
    rationale_str = " | ".join(reasons)
    
    return ReviewResult(
        suggested_allocation_column=suggested_allocation,
        amount_percentage=amount_percentage,
        eligibility_status=eligibility_status,
        confidence_score=confidence_score,
        review_status=review_status,
        rationale=rationale_str,
        reference_rule=reference_rule,
        secondary_allocation_note=secondary_note
    )
