import pandas as pd
from typing import List, Tuple
from boc_agent.schemas.transaction import Transaction
from boc_agent.schemas.review_result import ReviewResult

def export_reviewed_workbook(
    data: List[Tuple[Transaction, ReviewResult]], 
    output_path: str
) -> None:
    """Exports transaction data along with their review results to a CSV or Excel workbook."""
    rows = []
    for tx, review in data:
        row_dict = tx.model_dump()
        review_dict = review.model_dump()
        # Merge dictionaries
        combined = {**row_dict, **review_dict}
        rows.append(combined)
        
    df = pd.DataFrame(rows)
    if output_path.endswith('.csv'):
        df.to_csv(output_path, index=False)
    else:
        df.to_excel(output_path, index=False)
