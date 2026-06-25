import pandas as pd

def calculate_summary_metrics(df: pd.DataFrame) -> dict:
    """Calculates summary counts from a reviewed general ledger DataFrame."""
    metrics = {
        "total_rows": len(df),
        "approved": 0,
        "needs_human_review": 0,
        "eligible": 0,
        "needs_review": 0,
        "ineligible": 0,
        "out_of_canada": 0,
        "quebec_needs_review": 0,
        "quebec_non_qualified": 0
    }
    
    if df.empty:
        return metrics
        
    if "review_status" in df.columns:
        metrics["approved"] = int((df["review_status"] == "Approved").sum())
        metrics["needs_human_review"] = int((df["review_status"] == "Needs Human Review").sum())
        
    if "eligibility_status" in df.columns:
        metrics["eligible"] = int((df["eligibility_status"] == "Eligible").sum())
        metrics["needs_review"] = int((df["eligibility_status"] == "Needs Review").sum())
        metrics["ineligible"] = int((df["eligibility_status"] == "Ineligible").sum())
        
    if "suggested_allocation_column" in df.columns:
        metrics["out_of_canada"] = int((df["suggested_allocation_column"] == "Out of Canada costs").sum())
        metrics["quebec_needs_review"] = int((df["suggested_allocation_column"] == "Quebec needs review").sum())
        metrics["quebec_non_qualified"] = int((df["suggested_allocation_column"] == "Quebec non-qualified").sum())
        
    return metrics
