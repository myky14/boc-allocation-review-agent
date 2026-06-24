import sys
import os
import pandas as pd

def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/evaluate_outputs.py <path_to_reviewed_workbook>")
        sys.exit(1)
        
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"Error: File not found at {path}")
        sys.exit(1)
        
    try:
        # Excel can have multiple sheets; export_reviewed_workbook uses openpyxl to write
        df = pd.read_excel(path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        sys.exit(1)
        
    total_rows = len(df)
    print("==================================================")
    print("          BOC Agent Evaluation Summary            ")
    print("==================================================")
    print(f"Total Reviewed Transactions: {total_rows}")
    print()
    
    # 1. Count by review_status
    print("--- Review Status Breakdown ---")
    if "review_status" in df.columns:
        status_counts = df["review_status"].value_counts(dropna=False)
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
    else:
        print("  Error: 'review_status' column not found.")
    print()
    
    # 2. Count by eligibility_status
    print("--- Eligibility Status Breakdown ---")
    if "eligibility_status" in df.columns:
        elig_counts = df["eligibility_status"].value_counts(dropna=False)
        for status, count in elig_counts.items():
            print(f"  {status}: {count}")
    else:
        print("  Error: 'eligibility_status' column not found.")
    print()
    
    # 3. Top Allocation Columns
    print("--- Suggested Allocation Column Distribution ---")
    if "suggested_allocation_column" in df.columns:
        alloc_counts = df["suggested_allocation_column"].value_counts(dropna=False)
        for col, count in alloc_counts.items():
            print(f"  {col}: {count}")
    else:
        print("  Error: 'suggested_allocation_column' column not found.")
    print()
    
    # 4. Highlighted Categories
    print("--- Audit Highlights ---")
    if "review_status" in df.columns:
        needs_human = df[df["review_status"] == "Needs Human Review"]
        print(f"  Total Needs Human Review Rows: {len(needs_human)}")
    
    if "suggested_allocation_column" in df.columns:
        out_of_ca = df[df["suggested_allocation_column"] == "Out of Canada costs"]
        print(f"  Total Out of Canada Rows: {len(out_of_ca)}")
        
        qc_needs_review = df[df["suggested_allocation_column"] == "Quebec needs review"]
        print(f"  Total Quebec Needs Review Rows: {len(qc_needs_review)}")
        
        qc_non_qual = df[df["suggested_allocation_column"] == "Quebec non-qualified"]
        print(f"  Total Quebec Non-Qualified Rows: {len(qc_non_qual)}")
    print("==================================================")

if __name__ == "__main__":
    main()
