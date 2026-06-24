import os
import pytest
import pandas as pd
from boc_agent.io.workbook_loader import load_workbook, validate_dataframe_schema, REQUIRED_COLUMNS
from boc_agent.schemas.transaction import TransactionRecord

DATASET_PATH = "data/synthetic/synthetic_boc_gl_dataset.xlsx"

def test_dataset_exists():
    """Verifies that the synthetic dataset workbook exists in the designated directory."""
    assert os.path.exists(DATASET_PATH), f"Dataset file not found at: {DATASET_PATH}"

def test_workbook_loads_and_validates():
    """Verifies that the workbook loads as a pandas DataFrame with valid required columns and row count."""
    df = load_workbook(DATASET_PATH)
    assert isinstance(df, pd.DataFrame)
    
    # Assert row count is greater than 150
    assert len(df) > 150, f"Expected more than 150 transactions, found: {len(df)}"
    
    # Assert required columns exist in the loaded dataframe
    for col in REQUIRED_COLUMNS:
        assert col in df.columns, f"Expected column {col} was not found in loaded workbook"

def test_transaction_record_instantiation():
    """Verifies that a TransactionRecord can be successfully instantiated from the first row of the workbook."""
    df = load_workbook(DATASET_PATH)
    first_row_dict = df.iloc[0].to_dict()
    
    # Instantiation should succeed
    record = TransactionRecord.from_row_dict(first_row_dict)
    assert isinstance(record, TransactionRecord)
    assert record.amount == float(first_row_dict["Amount"])
    assert record.account == str(first_row_dict["Account"])

def test_missing_column_raises_error():
    """Verifies that validate_dataframe_schema raises a clear ValueError when a required column is missing."""
    dummy_data = {col: [1] for col in REQUIRED_COLUMNS if col != "Amount"}
    df_missing = pd.DataFrame(dummy_data)
    
    with pytest.raises(ValueError) as excinfo:
        validate_dataframe_schema(df_missing)
        
    assert "Missing required columns in workbook" in str(excinfo.value)

def _get_valid_dummy_row():
    return {
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

def test_invalid_account_raises_error():
    """Verifies that an invalid Account pattern raises a ValueError."""
    row = _get_valid_dummy_row()
    row["Account"] = "53200"  # Invalid format
    df = pd.DataFrame([row])
    with pytest.raises(ValueError) as excinfo:
        validate_dataframe_schema(df)
    assert "does not match format TXX-XXXX" in str(excinfo.value)

def test_invalid_src_raises_error():
    """Verifies that an invalid Src code raises a ValueError."""
    row = _get_valid_dummy_row()
    row["Src"] = "AP"  # Invalid format
    df = pd.DataFrame([row])
    with pytest.raises(ValueError) as excinfo:
        validate_dataframe_schema(df)
    assert "Src 'AP' must be 'PL' or 'CB'" in str(excinfo.value)

def test_invalid_location_raises_error():
    """Verifies that an invalid Location code raises a ValueError."""
    row = _get_valid_dummy_row()
    row["Location"] = "Studio A"  # Invalid format
    df = pd.DataFrame([row])
    with pytest.raises(ValueError) as excinfo:
        validate_dataframe_schema(df)
    assert "must be 900, 910, 920 or blank" in str(excinfo.value) or "is not a valid Location code" in str(excinfo.value)

def test_invalid_ep_raises_error():
    """Verifies that an invalid Ep code raises a ValueError."""
    row = _get_valid_dummy_row()
    row["Ep"] = "101"  # Invalid format
    df = pd.DataFrame([row])
    with pytest.raises(ValueError) as excinfo:
        validate_dataframe_schema(df)
    assert "must be one of" in str(excinfo.value) or "is not a valid Ep code" in str(excinfo.value)

def test_invalid_province_raises_error():
    """Verifies that an invalid Application Province raises a ValueError."""
    row = _get_valid_dummy_row()
    row["Application Province"] = "Alberta"  # Invalid format
    df = pd.DataFrame([row])
    with pytest.raises(ValueError) as excinfo:
        validate_dataframe_schema(df)
    assert "must be 'Ontario' or 'Quebec'" in str(excinfo.value)
