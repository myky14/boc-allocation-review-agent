import pandas as pd

def format_summary_response(total: int, approved: int, needs_review: int, eligible: int, needs_elig_review: int, ineligible: int) -> str:
    return f"""### 📊 Workbook Summary Metrics
- **Total Transactions**: {total}
- **Review Status**:
  - ✅ **Approved (Auto)**: {approved}
  - 🔍 **Needs Human Review**: {needs_review}
- **Eligibility Status**:
  - 🟢 **Eligible**: {eligible}
  - 🟡 **Needs Review**: {needs_elig_review}
  - 🔴 **Ineligible**: {ineligible}

*This assistant explains the reviewed workbook. It does not provide official tax-credit determinations.*"""

def format_row_explanation(row_data: dict) -> str:
    ref = row_data.get("Trans Ref") or row_data.get("trans_ref") or "N/A"
    vendor = row_data.get("Vendor Name") or row_data.get("vendor_name") or "N/A"
    amount = row_data.get("Amount") or row_data.get("amount") or 0.0
    currency = row_data.get("Currency") or row_data.get("currency") or "CAD"
    app_prov = row_data.get("Application Province") or row_data.get("application_province") or "N/A"
    location = row_data.get("Location") or row_data.get("location") or "N/A"
    ep = row_data.get("Ep") or row_data.get("ep") or "N/A"
    suggested = row_data.get("suggested_allocation_column") or "N/A"
    eligibility = row_data.get("eligibility_status") or "N/A"
    review = row_data.get("review_status") or "N/A"
    confidence = row_data.get("confidence_score") or 0.0
    rationale = row_data.get("rationale") or "N/A"
    
    sec_note = row_data.get("secondary_allocation_note")
    if sec_note is None or (isinstance(sec_note, float) and pd.isna(sec_note)) or str(sec_note).strip().lower() in ("nan", "", "none", "<na>"):
        sec_note = "None"
    
    return f"""### 🔍 Transaction Details: Reference {ref}
* **Vendor Name**: {vendor}
* **Amount**: {amount} {currency}
* **Application Province**: {app_prov}
* **Location Code / Ep Code**: {location} / {ep}
* **Agent Suggested Allocation**: `{suggested}`
* **Eligibility Status**: `{eligibility}`
* **Review Status**: `{review}`
* **Confidence Score**: `{confidence}`
* **Rationale**: {rationale}
* **Secondary Allocation Note**: {sec_note}

*This assistant explains the reviewed workbook. It does not provide official tax-credit determinations.*"""

def format_tax_ruling_refusal() -> str:
    return """⚠️ **Official Determination Disclaimer**
This assistant cannot make official tax-credit, legal, CRA, CAVCO, Ontario Creates, or SODEC determinations. Official determinations must come from the relevant authorities. Qualified tax/accounting professionals and this reviewed workbook can support internal review and follow-up.

If you need to analyze a transaction, please ensure the review pipeline has run, and consult the deterministic allocations in the workbook."""
