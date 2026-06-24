import re
import pandas as pd

REQUIRED_COLUMNS = [
    "Account", "Account Name", "Trans Date", "Src", "Trans Ref",
    "Vendor ID", "Vendor Name", "Description", "Additional Description",
    "Loan out corp", "Employee", "Tax ID", "Address", "City",
    "Province", "Country", "Zip Code", "Our Reference", "Currency",
    "USD", "Application Province", "Location", "Ep", "Amount"
]

ALLOWED_EPS = {40, 41, 42, 44, 45, 50, 51, 52, 54, 55, 60, 61, 62, 64, 65}
ALLOWED_LOCATIONS = {900, 910, 920}

def validate_dataframe_schema(df: pd.DataFrame) -> None:
    """Validates that all required columns are present and adhere to domain rules.
    
    Raises:
        ValueError: If any validation fails.
    """
    # 1. Verify required columns
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in workbook: {missing_columns}")

    # 2. Verify domain rules row-by-row
    account_pattern = re.compile(r"^T\d{2}-\d{4}$")
    
    for idx, row in df.iterrows():
        # Check Account matching regex TXX-XXXX
        acc = row.get("Account")
        if pd.isna(acc) or not re.match(account_pattern, str(acc)):
            raise ValueError(f"Row {idx}: Account '{acc}' does not match format TXX-XXXX (e.g. T22-1000)")
            
        # Check Src must be PL or CB
        src = row.get("Src")
        if pd.isna(src) or str(src) not in ["PL", "CB"]:
            raise ValueError(f"Row {idx}: Src '{src}' must be 'PL' or 'CB'")
            
        # Check Location must be 900, 910, 920 or blank
        loc = row.get("Location")
        if pd.notna(loc):
            try:
                loc_val = int(float(loc))
                if loc_val not in ALLOWED_LOCATIONS:
                    raise ValueError(f"Row {idx}: Location '{loc}' must be 900, 910, 920 or blank")
            except (ValueError, TypeError):
                raise ValueError(f"Row {idx}: Location '{loc}' is not a valid Location code")
                
        # Check Ep must be allowed codes or blank
        ep = row.get("Ep")
        if pd.notna(ep):
            try:
                ep_val = int(float(ep))
                if ep_val not in ALLOWED_EPS:
                    raise ValueError(f"Row {idx}: Ep '{ep}' must be one of {sorted(list(ALLOWED_EPS))} or blank")
            except (ValueError, TypeError):
                raise ValueError(f"Row {idx}: Ep '{ep}' is not a valid Ep code")
                
        # Check Application Province must be Ontario or Quebec
        prov = row.get("Application Province")
        if pd.isna(prov) or str(prov) not in ["Ontario", "Quebec"]:
            raise ValueError(f"Row {idx}: Application Province '{prov}' must be 'Ontario' or 'Quebec'")

def load_workbook(file_path: str) -> pd.DataFrame:
    """Loads a general ledger workbook (CSV or Excel) and validates its schema.
    
    Returns:
        pd.DataFrame: The loaded DataFrame with column order preserved.
    """
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
        
    validate_dataframe_schema(df)
    return df
