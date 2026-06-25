import pandas as pd
from typing import List, Tuple
from boc_agent.schemas.transaction import Transaction, TransactionRecord
from boc_agent.schemas.review_result import ReviewResult

def rename_and_reorder_df(df: pd.DataFrame, original_cols: List[str] = None) -> pd.DataFrame:
    """Formats a reviewed DataFrame to preserve original workbook headers and sequence.
    This function is a pure formatting/export helper and contains no business logic.
    """
    alias_map = {
        field_name: field_info.alias 
        for field_name, field_info in TransactionRecord.model_fields.items() 
        if field_info.alias
    }
    
    df_renamed = df.rename(columns=alias_map)
    
    if original_cols:
        existing_orig = [c for c in original_cols if c in df_renamed.columns]
        extra_cols = [c for c in df_renamed.columns if c not in existing_orig]
        df_renamed = df_renamed[existing_orig + extra_cols]
        
    return df_renamed

def export_reviewed_workbook(
    data: List[Tuple[Transaction, ReviewResult]], 
    output_path: str
) -> None:
    """Exports transaction data along with their review results to a CSV or Excel workbook."""
    rows = []
    
    # Find original columns order if populated in any transaction
    original_cols = []
    for tx, _ in data:
        if hasattr(tx, "_original_keys") and tx._original_keys:
            original_cols = tx._original_keys
            break
            
    for tx, review in data:
        row_dict = tx.model_dump()
        review_dict = review.model_dump()
        
        # Merge dictionaries
        combined = {**row_dict, **review_dict}
        rows.append(combined)
        
    df = pd.DataFrame(rows)
    df = rename_and_reorder_df(df, original_cols)
        
    if output_path.endswith('.csv'):
        df.to_csv(output_path, index=False)
    else:
        df.to_excel(output_path, index=False)
