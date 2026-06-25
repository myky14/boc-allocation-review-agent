import re
import yaml
from typing import Tuple, Dict, Any

def parse_skill_markdown(content: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Splits SKILL.md content into raw YAML frontmatter and Markdown sections.
    
    Returns:
        A tuple of (frontmatter_dict, sections_dict)
    """
    frontmatter_dict = {}
    remaining_content = content
    
    # 1. Parse YAML Frontmatter
    if content.strip().startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1]
            frontmatter_dict = yaml.safe_load(frontmatter_text) or {}
            remaining_content = parts[2]
            
    # 2. Parse Markdown Sections (e.g. ## Header Name)
    sections = {}
    lines = remaining_content.splitlines()
    current_header = None
    current_lines = []
    
    # Find headers matching "## Header Title"
    header_pattern = re.compile(r'^##\s+(.+)$')
    
    for line in lines:
        match = header_pattern.match(line.strip())
        if match:
            if current_header:
                sections[current_header] = "\n".join(current_lines).strip()
            current_header = match.group(1).strip()
            current_lines = []
        else:
            if current_header is not None:
                current_lines.append(line)
                
    if current_header:
        sections[current_header] = "\n".join(current_lines).strip()
        
    # 3. Clean and parse section contents as YAML where applicable
    parsed_sections = {}
    for header, text in sections.items():
        try:
            # We can safe_load the YAML lists/dicts directly
            parsed_data = yaml.safe_load(text)
            parsed_sections[header] = parsed_data
        except Exception:
            # If safe_load fails (e.g. general text), store raw text
            parsed_sections[header] = text
            
    return frontmatter_dict, parsed_sections
