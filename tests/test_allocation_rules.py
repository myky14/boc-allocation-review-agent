import pytest
from boc_agent.schemas.transaction import TransactionRecord
from boc_agent.tools.allocation_tool import review_transaction

def _get_base_tx_dict():
    return {
        "Account": "T22-1000",
        "Account Name": "Camera Operator",
        "Trans Date": "01/05/2026",
        "Src": "PL",
        "Trans Ref": "508841",
        "Vendor ID": "THE135",
        "Vendor Name": "Theo Desjardins",
        "Description": "Freelance camera services",
        "Additional Description": "Main Unit",
        "Loan out corp": None,
        "Employee": "Theo Desjardins",
        "Tax ID": "980-583-570",
        "Address": "850 Rue Lumen",
        "City": "Montreal",
        "Province": "Ontario",
        "Country": "Canada",
        "Zip Code": "M5V 2T6",
        "Our Reference": "11508",
        "Currency": "CAD",
        "USD": None,
        "Application Province": "Ontario",
        "Location": "900",
        "Ep": "41",
        "Amount": 1000.0
    }

# Test 1: Location 920 + Country Canada + Ontario application → Out of Canada costs, Ineligible
def test_loc_920_canada_ontario():
    tx_dict = _get_base_tx_dict()
    tx_dict["Location"] = "920"
    tx_dict["Country"] = "Canada"
    tx_dict["Application Province"] = "Ontario"
    tx_dict["Province"] = "Ontario"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Out of Canada costs"
    assert res.eligibility_status == "Ineligible"
    assert res.amount_percentage == 100.0
    assert res.review_status == "Approved"

# Test 2: Location 920 + Country Canada + Quebec application → Quebec non-qualified, Ineligible
def test_loc_920_canada_quebec():
    tx_dict = _get_base_tx_dict()
    tx_dict["Location"] = "920"
    tx_dict["Country"] = "Canada"
    tx_dict["Application Province"] = "Quebec"
    tx_dict["Province"] = "Quebec"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Quebec non-qualified"
    assert res.eligibility_status == "Ineligible"
    assert res.amount_percentage == 100.0
    assert res.review_status == "Approved"

# Test 3: Country United States + Location 900 → Needs Human Review due country/location conflict
def test_us_country_loc_900_conflict():
    tx_dict = _get_base_tx_dict()
    tx_dict["Location"] = "900"
    tx_dict["Country"] = "United States"
    tx_dict["Application Province"] = "Ontario"
    tx_dict["Province"] = "Georgia"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.review_status == "Needs Human Review"
    assert "conflict" in res.rationale

# Test 4: Quebec salary labour + Location 900 → Quebec qualified labour
def test_quebec_salary_labor():
    tx_dict = _get_base_tx_dict()
    tx_dict["Application Province"] = "Quebec"
    tx_dict["Province"] = "Quebec"
    tx_dict["Location"] = "900"
    tx_dict["Country"] = "Canada"
    tx_dict["Employee"] = "Jean Dupuis"
    tx_dict["Ep"] = "51"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Quebec qualified labour"
    assert res.eligibility_status == "Eligible"
    assert res.review_status == "Approved"

# Test 5: Quebec loan-out labour + Location 900 → Quebec qualified labour
def test_quebec_loan_out_labor():
    tx_dict = _get_base_tx_dict()
    tx_dict["Application Province"] = "Quebec"
    tx_dict["Province"] = "Quebec"
    tx_dict["Location"] = "900"
    tx_dict["Country"] = "Canada"
    tx_dict["Loan out corp"] = "Dupuis Productions Inc"
    tx_dict["Ep"] = "52"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Quebec qualified labour"
    assert res.eligibility_status == "Eligible"
    assert res.review_status == "Approved"

# Test 6: Quebec individual labour + Location 900 → Quebec qualified labour
def test_quebec_individual_labor():
    tx_dict = _get_base_tx_dict()
    tx_dict["Application Province"] = "Quebec"
    tx_dict["Province"] = "Quebec"
    tx_dict["Location"] = "900"
    tx_dict["Country"] = "Canada"
    tx_dict["Employee"] = None
    tx_dict["Loan out corp"] = None
    tx_dict["Vendor Name"] = "Jean Contractor"
    tx_dict["Ep"] = "55"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Quebec qualified labour"
    assert res.eligibility_status == "Eligible"
    assert res.review_status == "Approved"

# Test 7: Quebec multi-share + Location 900 → Quebec qualified labour, 65.0 percentage, secondary note
def test_quebec_multi_share_labor():
    tx_dict = _get_base_tx_dict()
    tx_dict["Application Province"] = "Quebec"
    tx_dict["Province"] = "Quebec"
    tx_dict["Location"] = "900"
    tx_dict["Country"] = "Canada"
    tx_dict["Ep"] = "54"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Quebec qualified labour"
    assert res.amount_percentage == 65.0
    assert "remaining 35% should be reviewed" in res.secondary_allocation_note

# Test 8: Quebec spend + Location 900 → Quebec qualified properties / spend
def test_quebec_spend_properties():
    tx_dict = _get_base_tx_dict()
    tx_dict["Application Province"] = "Quebec"
    tx_dict["Province"] = "Quebec"
    tx_dict["Location"] = "900"
    tx_dict["Country"] = "Canada"
    tx_dict["Employee"] = None
    tx_dict["Loan out corp"] = None
    tx_dict["Vendor Name"] = "Rentals Inc"
    tx_dict["Account Name"] = "EQUIPMENT RENTAL"
    tx_dict["Description"] = "Camera gear rental"
    tx_dict["Ep"] = "50"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Quebec qualified properties / spend"
    assert res.eligibility_status == "Eligible"
    assert res.amount_percentage == 100.0

# Test 9: Quebec missing Ep → Quebec needs review
def test_quebec_missing_ep():
    tx_dict = _get_base_tx_dict()
    tx_dict["Application Province"] = "Quebec"
    tx_dict["Province"] = "Quebec"
    tx_dict["Location"] = "900"
    tx_dict["Country"] = "Canada"
    tx_dict["Ep"] = None
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Quebec needs review"
    assert res.review_status == "Needs Human Review"
    assert res.eligibility_status == "Needs Review"

# Test 10: Quebec missing Location → Quebec needs review
def test_quebec_missing_location():
    tx_dict = _get_base_tx_dict()
    tx_dict["Application Province"] = "Quebec"
    tx_dict["Province"] = "Quebec"
    tx_dict["Location"] = None
    tx_dict["Country"] = "Canada"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Quebec needs review"
    assert res.review_status == "Needs Human Review"
    assert res.eligibility_status == "Needs Review"

# Test 11: Quebec partnership missing Tax ID → Quebec needs review
def test_quebec_partnership_missing_tax_id():
    tx_dict = _get_base_tx_dict()
    tx_dict["Application Province"] = "Quebec"
    tx_dict["Province"] = "Quebec"
    tx_dict["Location"] = "900"
    tx_dict["Country"] = "Canada"
    tx_dict["Vendor Name"] = "Consulting Partners LLP"
    tx_dict["Ep"] = "55"
    tx_dict["Tax ID"] = None
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Quebec needs review"
    assert res.review_status == "Needs Human Review"
    assert res.eligibility_status == "Needs Review"

# Test 12: VICE Canada Quebec labor → Quebec qualified labour with secondary note
def test_vice_canada_quebec_labor():
    tx_dict = _get_base_tx_dict()
    tx_dict["Application Province"] = "Quebec"
    tx_dict["Province"] = "Quebec"
    tx_dict["Location"] = "900"
    tx_dict["Country"] = "Canada"
    tx_dict["Vendor Name"] = "VICE STUDIO CANADA"
    tx_dict["Employee"] = "Vice Crew"
    tx_dict["Ep"] = "51"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Quebec qualified labour"
    assert "VICE Canada labor; Quebec-specific dedicated VICE bucket is not implemented" in res.secondary_allocation_note

# Test 13: Ontario VICE labor remains ONT labor paid to VICE Canada
def test_ontario_vice_labor():
    tx_dict = _get_base_tx_dict()
    tx_dict["Application Province"] = "Ontario"
    tx_dict["Province"] = "Ontario"
    tx_dict["Location"] = "900"
    tx_dict["Country"] = "Canada"
    tx_dict["Vendor Name"] = "VICE STUDIO CANADA"
    tx_dict["Employee"] = "Vice Crew"
    tx_dict["Ep"] = "41"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "ONT labor paid to VICE Canada"

# Test 14: Federal/non-Ontario VICE labor remains Fed labor paid to VICE Canada
def test_federal_vice_labor():
    tx_dict = _get_base_tx_dict()
    tx_dict["Application Province"] = "Ontario"
    tx_dict["Province"] = "Ontario"
    tx_dict["Location"] = "910"
    tx_dict["Country"] = "Canada"
    tx_dict["Vendor Name"] = "VICE STUDIO CANADA"
    tx_dict["Employee"] = "Vice Crew"
    tx_dict["Ep"] = "41"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Fed labor paid to VICE Canada"

# Test 15: Meal with Location 920 → Out of Canada costs or Quebec non-qualified depending application province
def test_meal_location_920_ontario():
    tx_dict = _get_base_tx_dict()
    tx_dict["Application Province"] = "Ontario"
    tx_dict["Province"] = "Ontario"
    tx_dict["Location"] = "920"
    tx_dict["Country"] = "Canada"
    tx_dict["Description"] = "Catering services for production"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Out of Canada costs"
    assert res.eligibility_status == "Ineligible"

def test_meal_location_920_quebec():
    tx_dict = _get_base_tx_dict()
    tx_dict["Application Province"] = "Quebec"
    tx_dict["Province"] = "Quebec"
    tx_dict["Location"] = "920"
    tx_dict["Country"] = "Canada"
    tx_dict["Description"] = "Catering services for production"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Quebec non-qualified"
    assert res.eligibility_status == "Ineligible"

# Regression Test: Quebec + Location 920 + Country United States -> Quebec non-qualified, Ineligible
def test_loc_920_us_quebec():
    tx_dict = _get_base_tx_dict()
    tx_dict["Application Province"] = "Quebec"
    tx_dict["Province"] = "Georgia"
    tx_dict["Location"] = "920"
    tx_dict["Country"] = "United States"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Quebec non-qualified"
    assert res.eligibility_status == "Ineligible"
    assert res.amount_percentage == 100.0

# Regression Test: Quebec + Location 920 + Country Canada -> Quebec non-qualified, Ineligible
def test_loc_920_canada_quebec_direct():
    tx_dict = _get_base_tx_dict()
    tx_dict["Application Province"] = "Quebec"
    tx_dict["Province"] = "Quebec"
    tx_dict["Location"] = "920"
    tx_dict["Country"] = "Canada"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    assert res.suggested_allocation_column == "Quebec non-qualified"
    assert res.eligibility_status == "Ineligible"
    assert res.amount_percentage == 100.0

# Regression Test: Editing rooms + Ep 60 + no employee + no loan-out should NOT trigger labor conflict
def test_editing_rooms_no_labor_conflict():
    tx_dict = _get_base_tx_dict()
    tx_dict["Account Name"] = "EDITING ROOMS"
    tx_dict["Ep"] = "60"
    tx_dict["Description"] = "Remote collaboration platform"
    tx_dict["Employee"] = None
    tx_dict["Loan out corp"] = None
    tx_dict["Vendor Name"] = "EditGrid Systems"
    
    tx = TransactionRecord.from_row_dict(tx_dict)
    res = review_transaction(tx)
    
    # It should not trigger labor-related conflict, meaning review_status could be Approved if other fields are valid
    # Wait, in the base dictionary, application province is Ontario but payee province is Ontario (wait, base has province=Ontario). Let's see:
    # Ep = 60 (Spend), no employee/corp. This maps to Ontario Spend (40) or Fed non eligible.
    # Since Location = 900, Application Province = Ontario, Country = Canada, it maps to Ontario Spend (40).
    # And since there is no conflict, it should be Approved!
    assert res.suggested_allocation_column == "Ontario Spend (40)"
    assert res.review_status == "Approved"

