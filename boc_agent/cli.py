import argparse
import sys
from boc_agent.io.workbook_loader import load_workbook
from boc_agent.io.workbook_exporter import export_reviewed_workbook
from boc_agent.schemas.transaction import TransactionRecord
from boc_agent.agents.orchestrator import Orchestrator

def main():
    """CLI entrypoint for processing General Ledger workbooks."""
    parser = argparse.ArgumentParser(description="BOC Allocation Review Agent CLI")
    parser.add_argument(
        "--input", 
        required=True, 
        help="Path to synthetic input GL workbook (CSV or Excel)"
    )
    parser.add_argument(
        "--output", 
        required=True, 
        help="Path to save reviewed workbook (CSV or Excel)"
    )
    
    args = parser.parse_args()
    
    try:
        print(f"Loading workbook: {args.input}")
        df = load_workbook(args.input)
        print(f"Loaded {len(df)} transactions.")
        
        orchestrator = Orchestrator()
        reviewed_data = []
        
        print("Processing transactions through agent workflow...")
        for _, row in df.iterrows():
            tx = TransactionRecord.from_row_dict(row.to_dict())
            result = orchestrator.process_transaction(tx)
            reviewed_data.append((tx, result))
            
        print(f"Exporting results to: {args.output}")
        export_reviewed_workbook(reviewed_data, args.output)
        print("Processing completed successfully.")
        
    except Exception as e:
        print(f"Error during processing: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
