import os
from typing import List, Dict

def load_documents(base_dir: str = ".") -> List[Dict[str, str]]:
    """Loads approved repository markdown/text documents relative to base_dir.
    
    Loads specific root files (README.md, PROJECT_CONTEXT.md, walkthrough.md) 
    and dynamically scans docs/*.md files. Skips missing/binary files gracefully.
    """
    documents = []
    
    # 1. Root files
    root_files = ["README.md", "PROJECT_CONTEXT.md", "walkthrough.md"]
    for rel_path in root_files:
        full_path = os.path.join(base_dir, rel_path)
        if os.path.isfile(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    text = f.read()
                documents.append({
                    "source_file": rel_path,
                    "text": text
                })
            except Exception:
                pass
                
    # 2. Dynamically scan docs/*.md
    docs_dir = os.path.join(base_dir, "docs")
    if os.path.isdir(docs_dir):
        try:
            for file_name in sorted(os.listdir(docs_dir)):
                if file_name.endswith(".md"):
                    rel_path = f"docs/{file_name}"
                    full_path = os.path.join(docs_dir, file_name)
                    if os.path.isfile(full_path):
                        with open(full_path, "r", encoding="utf-8") as f:
                            text = f.read()
                        documents.append({
                            "source_file": rel_path,
                            "text": text
                        })
        except Exception:
            pass
            
    return documents
