import pandas as pd
from boc_agent.ui_helpers import calculate_summary_metrics

def test_calculate_summary_metrics_valid_data():
    df = pd.DataFrame([
        {
            "review_status": "Approved",
            "eligibility_status": "Eligible",
            "suggested_allocation_column": "Ontario Salary (41)"
        },
        {
            "review_status": "Needs Human Review",
            "eligibility_status": "Needs Review",
            "suggested_allocation_column": "Quebec needs review"
        },
        {
            "review_status": "Needs Human Review",
            "eligibility_status": "Ineligible",
            "suggested_allocation_column": "Out of Canada costs"
        }
    ])
    
    metrics = calculate_summary_metrics(df)
    assert metrics["total_rows"] == 3
    assert metrics["approved"] == 1
    assert metrics["needs_human_review"] == 2
    assert metrics["eligible"] == 1
    assert metrics["needs_review"] == 1
    assert metrics["ineligible"] == 1
    assert metrics["out_of_canada"] == 1
    assert metrics["quebec_needs_review"] == 1
    assert metrics["quebec_non_qualified"] == 0

def test_calculate_summary_metrics_empty_data():
    df = pd.DataFrame()
    metrics = calculate_summary_metrics(df)
    assert metrics["total_rows"] == 0
    assert metrics["approved"] == 0
    assert metrics["needs_human_review"] == 0
