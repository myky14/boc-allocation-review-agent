import pandas as pd
from typing import List, Union

def export_human_review_log(decisions: Union[List[dict], pd.DataFrame], output_path: str) -> None:
    """Exports human review queue/log to a CSV or Excel workbook."""
    if isinstance(decisions, list):
        df = pd.DataFrame(decisions)
    else:
        df = decisions
        
    if output_path.endswith('.csv'):
        df.to_csv(output_path, index=False)
    else:
        df.to_excel(output_path, index=False)
