import pytest
import pandas as pd
from boc_agent.chat.query_router import route_query
from boc_agent.chat.assistant import ReviewConversationAssistant

def test_intent_router_classification():
    # 1. Tax Ruling refusal intents
    assert route_query("is this officially eligible?") == "tax_ruling"
    assert route_query("guarantee this tax credit") == "tax_ruling"
    assert route_query("can we claim this officially?") == "tax_ruling"
    assert route_query("make a CAVCO determination") == "tax_ruling"
    assert route_query("optimize my tax credit") == "tax_ruling"
    
    # 2. Row explanation intents
    assert route_query("explain row 12") == "row_explanation"
    assert route_query("what does the agent recommend for trans ref 508841?") == "row_explanation"
    assert route_query("explain transaction 508841") == "row_explanation"
    assert route_query("Theo Desjardins") == "row_explanation" # Short vendor search
    
    # 3. Location filters
    assert route_query("Show me all Location 920 rows.") == "filter_location"
    assert route_query("outside canada costs") == "filter_location"
    
    # 4. Review queue summary
    assert route_query("Summarize the review queue.") == "review_queue_summary"
    assert route_query("flagged rows") == "review_queue_summary"
    
    # 5. Ineligible summary
    assert route_query("Which rows are ineligible?") == "ineligible_summary"
    
    # 6. Needs documentation
    assert route_query("Which rows need more documents?") == "needs_documentation"
    assert route_query("missing tax id") == "needs_documentation"
    
    # 7. Overall Summary
    assert route_query("overview of stats") == "summary"
    assert route_query("how many rows are there?") == "summary"
    
    # 8. Unknown fallback
    assert route_query("What is the weather today?") == "unknown"


def _get_snake_case_test_df():
    data = [
        {
            "trans_ref": "508841",
            "vendor_name": "Theo Desjardins",
            "amount": 100.0,
            "currency": "CAD",
            "application_province": "Quebec",
            "location": "920",
            "ep": "55",
            "suggested_allocation_column": "Quebec non-qualified",
            "eligibility_status": "Ineligible",
            "review_status": "Needs Human Review",
            "confidence_score": 0.70,
            "rationale": "Quebec non-qualified cost (Location 920)",
            "secondary_allocation_note": "None"
        },
        {
            "trans_ref": "123456",
            "vendor_name": "Greenslate Pay",
            "amount": 500.0,
            "currency": "CAD",
            "application_province": "Ontario",
            "location": "900",
            "ep": "41",
            "suggested_allocation_column": "Ontario Salary (41)",
            "eligibility_status": "Eligible",
            "review_status": "Approved",
            "confidence_score": 1.00,
            "rationale": "Ontario salary eligible",
            "secondary_allocation_note": "None"
        }
    ]
    return pd.DataFrame(data)


def _get_alias_test_df():
    # Uses original workbook headers for some columns
    data = [
        {
            "Trans Ref": "508841",
            "Vendor Name": "Theo Desjardins",
            "Amount": 100.0,
            "Currency": "CAD",
            "Application Province": "Quebec",
            "Location": "920",
            "Ep": "55",
            "suggested_allocation_column": "Quebec non-qualified",
            "eligibility_status": "Ineligible",
            "review_status": "Needs Human Review",
            "confidence_score": 0.70,
            "rationale": "Quebec non-qualified cost (Location 920)",
            "secondary_allocation_note": "None"
        },
        {
            "Trans Ref": "123456",
            "Vendor Name": "Greenslate Pay",
            "Amount": 500.0,
            "Currency": "CAD",
            "Application Province": "Ontario",
            "Location": "900",
            "Ep": "41",
            "suggested_allocation_column": "Ontario Salary (41)",
            "eligibility_status": "Eligible",
            "review_status": "Approved",
            "confidence_score": 1.00,
            "rationale": "Ontario salary eligible",
            "secondary_allocation_note": "None"
        }
    ]
    return pd.DataFrame(data)


def test_assistant_non_mutation():
    assistant = ReviewConversationAssistant()
    df = _get_snake_case_test_df()
    df_orig = df.copy()
    
    # Process queries
    assistant.answer("summary", df)
    assistant.answer("explain transaction 508841", df)
    assistant.answer("Location 920 rows", df)
    
    # Assert DataFrame was not altered/mutated
    pd.testing.assert_frame_equal(df, df_orig)


def test_assistant_summary_queries():
    assistant = ReviewConversationAssistant()
    
    # 1. Test snake_case DataFrame
    df_snake = _get_snake_case_test_df()
    res1 = assistant.answer("summary", df_snake)
    assert "Total Transactions" in res1
    assert "Approved (Auto)" in res1
    assert "Needs Human Review" in res1
    
    # 2. Test original workbook headers DataFrame
    df_alias = _get_alias_test_df()
    res2 = assistant.answer("summary", df_alias)
    assert "Total Transactions" in res2
    assert "Approved (Auto)" in res2
    assert "Needs Human Review" in res2


def test_assistant_row_explanations():
    assistant = ReviewConversationAssistant()
    df_alias = _get_alias_test_df()
    
    # 1. Find by Trans Ref (alias header)
    res = assistant.answer("explain transaction 508841", df_alias)
    assert "Theo Desjardins" in res
    assert "Quebec non-qualified" in res
    assert "Ineligible" in res
    
    # 2. Find by Vendor Name substring
    res_vendor = assistant.answer("tell me about Greenslate Pay", df_alias)
    assert "Greenslate Pay" in res_vendor
    assert "Ontario Salary (41)" in res_vendor
    
    # 3. Find by index fallback
    res_idx = assistant.answer("explain row 0", df_alias)
    assert "Theo Desjardins" in res_idx
    
    # 4. Safe not found response
    res_missing = assistant.answer("explain row 99", df_alias)
    assert "not found" in res_missing or "run review first" in res_missing or "ensure the review pipeline" in res_missing


def test_assistant_location_filtering():
    assistant = ReviewConversationAssistant()
    df_alias = _get_alias_test_df()
    
    # Check Location 920 search
    res = assistant.answer("Show me all Location 920 rows", df_alias)
    assert "Location 920" in res
    assert "1 rows" in res
    assert "Quebec non-qualified" in res


def test_assistant_review_queue():
    assistant = ReviewConversationAssistant()
    df_alias = _get_alias_test_df()
    
    res = assistant.answer("Summarize the human review queue", df_alias)
    assert "review queue" in res.lower()
    assert "1 rows" in res


def test_assistant_tax_refusal():
    assistant = ReviewConversationAssistant()
    df_alias = _get_alias_test_df()
    
    res = assistant.answer("is this officially eligible?", df_alias)
    assert "Official Determination Disclaimer" in res
    assert "This assistant cannot make official tax-credit, legal, CRA, CAVCO" in res


def test_assistant_our_reference_matching():
    assistant = ReviewConversationAssistant()
    
    # DataFrame with Our Reference (original header)
    df_our_ref = pd.DataFrame([
        {
            "Trans Ref": "99999",
            "Our Reference": "88888",
            "Vendor Name": "Test Vendor",
            "Amount": 100.0,
            "Currency": "CAD",
            "Application Province": "Ontario",
            "Location": "900",
            "Ep": "41",
            "suggested_allocation_column": "Ontario Salary (41)",
            "eligibility_status": "Eligible",
            "review_status": "Approved",
            "confidence_score": 1.00,
            "rationale": "Eligible cost",
            "secondary_allocation_note": "None"
        }
    ])
    
    # DataFrame with our_reference (snake_case header)
    df_our_ref_snake = pd.DataFrame([
        {
            "trans_ref": "99999",
            "our_reference": "88888",
            "vendor_name": "Test Vendor",
            "amount": 100.0,
            "currency": "CAD",
            "application_province": "Ontario",
            "location": "900",
            "ep": "41",
            "suggested_allocation_column": "Ontario Salary (41)",
            "eligibility_status": "Eligible",
            "review_status": "Approved",
            "confidence_score": 1.00,
            "rationale": "Eligible cost",
            "secondary_allocation_note": "None"
        }
    ])
    
    res1 = assistant.answer("explain transaction 88888", df_our_ref)
    assert "Test Vendor" in res1
    
    res2 = assistant.answer("explain transaction 88888", df_our_ref_snake)
    assert "Test Vendor" in res2


def test_assistant_no_dataframe_response():
    assistant = ReviewConversationAssistant()
    
    # Test None DataFrame
    res_none = assistant.answer("summary", None)
    assert "not found / run review first" in res_none
    
    # Test empty DataFrame
    df_empty = pd.DataFrame()
    res_empty = assistant.answer("summary", df_empty)
    assert "not found / run review first" in res_empty


def test_assistant_needs_documentation_intent():
    assistant = ReviewConversationAssistant()
    
    # Small dataframe with fields that trigger needs_documentation
    df = pd.DataFrame([
        {
            "trans_ref": "11111",
            "vendor_name": "Doc Needed Vendor",
            "amount": 200.0,
            "currency": "CAD",
            "application_province": "Ontario",
            "location": "900",
            "ep": "41",
            "suggested_allocation_column": "Ontario Salary (41)",
            "eligibility_status": "Needs Review",
            "review_status": "Needs Human Review",
            "confidence_score": 0.5,
            "rationale": "Missing tax ID evidence",
            "secondary_allocation_note": "None"
        }
    ])
    
    res = assistant.answer("Which rows need more documents?", df)
    assert "Documentation & Follow-up Actions" in res
    assert "Doc Needed Vendor" in res
    assert "Missing tax ID evidence" in res


def test_assistant_nan_secondary_note():
    assistant = ReviewConversationAssistant()
    
    # Dataframe with NaN in secondary_allocation_note
    df = pd.DataFrame([
        {
            "trans_ref": "77777",
            "vendor_name": "NaN Vendor",
            "amount": 300.0,
            "currency": "CAD",
            "application_province": "Ontario",
            "location": "900",
            "ep": "41",
            "suggested_allocation_column": "Ontario Salary (41)",
            "eligibility_status": "Eligible",
            "review_status": "Approved",
            "confidence_score": 1.0,
            "rationale": "All good",
            "secondary_allocation_note": float('nan')
        }
    ])
    
    res = assistant.answer("explain transaction 77777", df)
    assert "Secondary Allocation Note**: None" in res


def test_assistant_refusal_wording():
    assistant = ReviewConversationAssistant()
    df = _get_alias_test_df()
    res = assistant.answer("is this officially eligible?", df)
    
    # Verify the disclaimer does not describe the deterministic engine as an official determination source
    assert "Official Determination Disclaimer" in res
    assert "This assistant cannot make official tax-credit, legal, CRA, CAVCO" in res
    assert "deterministic rules engine" not in res.lower()
    assert "deterministic engine" not in res.lower()
    assert "rules engine output" not in res.lower()
