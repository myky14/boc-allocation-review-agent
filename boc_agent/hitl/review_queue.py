import pandas as pd

def build_review_queue(reviewed_rows: pd.DataFrame) -> pd.DataFrame:
    """Filters the reviewed workbook DataFrame to return only rows that require human review.
    
    Criteria:
      - review_status == "Needs Human Review"
      - OR rationale contains warning/injection keywords
      - OR eligibility_status is "Needs Review"
      - OR confidence_score < 0.8
    """
    if reviewed_rows.empty:
        return reviewed_rows
        
    cond_status = reviewed_rows["review_status"] == "Needs Human Review"
    
    cond_rationale = reviewed_rows["rationale"].astype(str).str.contains(
        "Potential prompt injection|warning|injection", case=False, na=False
    )
    
    cond_eligibility = reviewed_rows["eligibility_status"] == "Needs Review"
    
    cond_confidence = reviewed_rows["confidence_score"] < 0.8
    
    filtered_df = reviewed_rows[cond_status | cond_rationale | cond_eligibility | cond_confidence]
    return filtered_df
