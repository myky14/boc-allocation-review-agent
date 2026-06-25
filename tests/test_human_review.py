import os
import tempfile
import pytest
import pandas as pd
from boc_agent.hitl.review_decision import HumanReviewDecision, apply_human_decision
from boc_agent.hitl.review_queue import build_review_queue
from boc_agent.hitl.review_exporter import export_human_review_log

def test_hitl_review_queue_filtering():
    # Construct a dummy reviewed dataframe
    data = [
        # Case 1: Approved high confidence -> should be excluded
        {
            "trans_ref": "TX001",
            "review_status": "Approved",
            "rationale": "Standard transaction.",
            "eligibility_status": "Eligible",
            "confidence_score": 1.0,
            "suggested_allocation_column": "Ontario Salary (41)"
        },
        # Case 2: Needs Human Review -> should be included
        {
            "trans_ref": "TX002",
            "review_status": "Needs Human Review",
            "rationale": "Missing required fields.",
            "eligibility_status": "Needs Review",
            "confidence_score": 0.7,
            "suggested_allocation_column": "Ontario Salary (41)"
        },
        # Case 3: Security-flagged in rationale -> should be included
        {
            "trans_ref": "TX003",
            "review_status": "Approved", # Or Needs Human Review
            "rationale": "Potential prompt injection detected.",
            "eligibility_status": "Eligible",
            "confidence_score": 0.0,
            "suggested_allocation_column": "Ontario Salary (41)"
        },
        # Case 4: Low confidence (< 0.8) -> should be included
        {
            "trans_ref": "TX004",
            "review_status": "Approved",
            "rationale": "Ambiguous payee.",
            "eligibility_status": "Eligible",
            "confidence_score": 0.75,
            "suggested_allocation_column": "Ontario Salary (41)"
        }
    ]
    df = pd.DataFrame(data)
    queue = build_review_queue(df)
    
    refs = queue["trans_ref"].tolist()
    assert "TX001" not in refs
    assert "TX002" in refs
    assert "TX003" in refs
    assert "TX004" in refs
    assert len(queue) == 3

def test_hitl_apply_decision_preserves_agent_suggestion():
    row = {
        "trans_ref": "TX002",
        "suggested_allocation_column": "Ontario Salary (41)",
        "amount_percentage": 100.0,
        "eligibility_status": "Needs Review"
    }
    
    decision = HumanReviewDecision(
        transaction_ref="TX002",
        reviewer_decision="Override Allocation",
        reviewer_comment="Reclassified to spend per invoice review.",
        reviewer_name="Audit Lead",
        reviewed_at="2026-06-25T12:00:00Z",
        override_allocation="Ontario Spend (40)",
        override_reason="Accountant override"
    )
    
    updated = apply_human_decision(row, decision)
    
    # Original agent suggestion remains intact
    assert updated["suggested_allocation_column"] == "Ontario Salary (41)"
    assert updated["amount_percentage"] == 100.0
    
    # Human override details are added separately
    assert updated["human_review_decision"] == "Override Allocation"
    assert updated["human_review_comment"] == "Reclassified to spend per invoice review."
    assert updated["human_reviewer"] == "Audit Lead"
    assert updated["human_reviewed_at"] == "2026-06-25T12:00:00Z"
    assert updated["human_override_allocation"] == "Ontario Spend (40)"
    assert updated["human_override_reason"] == "Accountant override"

def test_hitl_export_to_csv():
    decisions = [
        {
            "trans_ref": "TX002",
            "suggested_allocation_column": "Ontario Salary (41)",
            "human_review_decision": "Override Allocation",
            "human_reviewer": "Auditor"
        }
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "human_review_log.csv")
        export_human_review_log(decisions, output_file)
        
        assert os.path.exists(output_file)
        df = pd.read_csv(output_file)
        assert len(df) == 1
        assert df.iloc[0]["trans_ref"] == "TX002"
        assert df.iloc[0]["human_reviewer"] == "Auditor"

def test_exporter_header_preservation():
    from boc_agent.io.workbook_exporter import export_reviewed_workbook
    from boc_agent.schemas.transaction import TransactionRecord
    from boc_agent.schemas.review_result import ReviewResult
    import tempfile
    import os
    import pandas as pd
    
    tx_dict = {
        "Account": "T22-1000",
        "Account Name": "Camera",
        "Trans Date": "01/05/2026",
        "Src": "PL",
        "Trans Ref": "508841",
        "Vendor ID": "THE135",
        "Vendor Name": "Theo Desjardins",
        "Description": "Freelance",
        "Additional Description": None,
        "Loan out corp": None,
        "Employee": "Theo Desjardins",
        "Tax ID": "123456789",
        "Address": "123 Main St",
        "City": "Montreal",
        "Province": "Quebec",
        "Country": "Canada",
        "Zip Code": "H2X 1Y4",
        "Our Reference": "11508",
        "Currency": "CAD",
        "USD": None,
        "Application Province": "Quebec",
        "Location": "900",
        "Ep": "55",
        "Amount": 100.0
    }
    tx = TransactionRecord.from_row_dict(tx_dict)
    
    review = ReviewResult(
        suggested_allocation_column="Quebec qualified labour",
        amount_percentage=100.0,
        eligibility_status="Eligible",
        confidence_score=1.0,
        review_status="Approved",
        rationale="Valid",
        reference_rule="RULE_DEFAULT"
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "exported.xlsx")
        export_reviewed_workbook([(tx, review)], output_path)
        
        df = pd.read_excel(output_path)
        # Original headers must be preserved
        assert "Vendor Name" in df.columns
        assert "Application Province" in df.columns
        assert "Trans Ref" in df.columns
        # Internal snake_case fields should NOT be there
        assert "vendor_name" not in df.columns
        assert "application_province" not in df.columns
        assert "trans_ref" not in df.columns


def test_hitl_decision_validation():
    from pydantic import ValidationError
    
    base_args = {
        "transaction_ref": "TX001",
        "reviewer_comment": "Valid comment",
        "reviewer_name": "Auditor",
        "reviewed_at": "2026-06-25T12:00:00Z"
    }
    
    # Valid decisions should pass
    valid_decisions = [
        "Accept Agent Suggestion",
        "Override Allocation",
        "Mark Ineligible",
        "Request More Documentation",
        "Defer"
    ]
    for decision in valid_decisions:
        model = HumanReviewDecision(reviewer_decision=decision, **base_args)
        assert model.reviewer_decision == decision
        
    # Invalid decisions should raise ValidationError
    invalid_decisions = ["banana", "random", "approved", ""]
    for decision in invalid_decisions:
        with pytest.raises(ValidationError):
            HumanReviewDecision(reviewer_decision=decision, **base_args)


def test_exporter_preserves_custom_column_and_order():
    from boc_agent.io.workbook_exporter import export_reviewed_workbook
    from boc_agent.schemas.transaction import TransactionRecord
    from boc_agent.schemas.review_result import ReviewResult
    import tempfile
    import os
    import pandas as pd
    
    # Construct row with a custom column and in non-standard order
    # Note: dict keys insertion order is preserved in Python
    row_dict = {
        "My Custom Column": "CustomValue",
        "Vendor Name": "Alice Smith",
        "Account": "T22-1000",
        "Account Name": "Catering",
        "Trans Date": "2026-06-25",
        "Amount": 250.0
    }
    
    # 1. Test using TransactionRecord.from_row_dict (preserves original keys order)
    tx = TransactionRecord.from_row_dict(row_dict)
    assert tx.amount == 250.0
    # Custom fields are stored due to extra="allow"
    assert getattr(tx, "My Custom Column") == "CustomValue"
    
    review = ReviewResult(
        suggested_allocation_column="Meal (catering, craft, per diem)",
        amount_percentage=100.0,
        eligibility_status="Eligible",
        confidence_score=1.0,
        review_status="Approved",
        rationale="Good",
        reference_rule="RULE_DEFAULT"
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "custom_order.xlsx")
        export_reviewed_workbook([(tx, review)], output_path)
        
        df = pd.read_excel(output_path)
        
        # Verify custom column and headers are preserved
        assert "My Custom Column" in df.columns
        assert "Vendor Name" in df.columns
        assert "Account" in df.columns
        assert "suggested_allocation_column" in df.columns
        
        # Verify the columns order
        # Original columns must be first, in the original order, followed by other columns and review columns
        cols = list(df.columns)
        assert cols[0] == "My Custom Column"
        assert cols[1] == "Vendor Name"
        assert cols[2] == "Account"
        assert cols[3] == "Account Name"
        assert cols[4] == "Trans Date"
        assert cols[5] == "Amount"
        
        # Review columns must be at the very end
        assert cols[-8] == "suggested_allocation_column"
        assert cols[-7] == "amount_percentage"
        assert cols[-6] == "eligibility_status"
        assert cols[-5] == "confidence_score"
        assert cols[-4] == "review_status"
        assert cols[-3] == "rationale"
        assert cols[-2] == "reference_rule"
        assert cols[-1] == "secondary_allocation_note"
        
    # 2. Test when TransactionRecord is created directly (without _original_keys)
    # It should still export successfully without raising any exceptions
    direct_tx = TransactionRecord(
        account="T22-1000",
        account_name="Catering",
        trans_date="2026-06-25",
        amount=250.0,
        vendor_name="Alice Smith"
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "direct.xlsx")
        # Should not raise exception
        export_reviewed_workbook([(direct_tx, review)], output_path)
        df_direct = pd.read_excel(output_path)
        assert "Account" in df_direct.columns
        assert "Vendor Name" in df_direct.columns
        assert "suggested_allocation_column" in df_direct.columns



