import sys
import os
import pandas as pd
from boc_agent.hitl.review_queue import build_review_queue
from boc_agent.hitl.review_exporter import export_human_review_log

def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "outputs/reviewed_boc_gl_dataset.xlsx"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "outputs/human_review_queue.xlsx"
    
    if not os.path.exists(input_path):
        print(f"Error: Input reviewed file not found at {input_path}")
        sys.exit(1)
        
    try:
        df = pd.read_excel(input_path)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        sys.exit(1)
        
    total_rows = len(df)
    queue_df = build_review_queue(df)
    needs_review_count = len(queue_df)
    
    # Save the queue workbook
    export_human_review_log(queue_df, output_path)
    
    print("==================================================")
    print("        HITL Review Queue Builder Completed       ")
    print("==================================================")
    print(f"Total Reviewed Rows in Input: {total_rows}")
    print(f"Number of Rows Requiring Human Review: {needs_review_count}")
    print(f"Output Queue Exported to: {output_path}")
    print("==================================================")

if __name__ == "__main__":
    main()
