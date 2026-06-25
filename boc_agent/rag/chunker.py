from typing import List, Dict

def chunk_documents(documents: List[Dict[str, str]], chunk_size: int = 500, overlap: int = 100) -> List[Dict[str, str]]:
    """Chunks documents into sections of chunk_size characters with overlap, 
    associating each chunk with its closest markdown header.
    """
    chunks = []
    step = max(1, chunk_size - overlap)
    
    for doc in documents:
        source_file = doc["source_file"]
        text = doc["text"]
        
        # Split into lines to identify headings
        lines = text.splitlines()
        sections = []
        current_header = "Introduction"
        current_section_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                # Save previous section if it has content
                section_content = "\n".join(current_section_lines).strip()
                if section_content:
                    sections.append((current_header, section_content))
                current_section_lines = []
                # Parse new header name
                current_header = stripped.lstrip("#").strip()
            else:
                current_section_lines.append(line)
                
        # Append last section
        section_content = "\n".join(current_section_lines).strip()
        if section_content:
            sections.append((current_header, section_content))
            
        # Fallback if no sections were parsed but document has text
        if not sections and text.strip():
            sections.append(("Introduction", text.strip()))
            
        for header, section_text in sections:
            section_text = section_text.strip()
            if not section_text:
                continue
                
            text_len = len(section_text)
            
            # If the entire section is smaller than chunk_size, output it as one chunk
            if text_len <= chunk_size:
                chunks.append({
                    "source_file": source_file,
                    "header": header,
                    "excerpt": section_text
                })
                continue
                
            start = 0
            while start < text_len:
                end = start + chunk_size
                excerpt = section_text[start:end].strip()
                if excerpt:
                    chunks.append({
                        "source_file": source_file,
                        "header": header,
                        "excerpt": excerpt
                    })
                start += step
                
    return chunks
