import os
import re
from boc_agent.rag.retriever import DocRetriever

def sanitize_absolute_paths(text: str) -> str:
    """Sanitizes absolute file URLs and Windows absolute paths to relative ones or removes them."""
    if not text:
        return text
    try:
        ws_abs = os.path.abspath(".").replace("\\", "/").rstrip("/") + "/"
        ws_abs_back = os.path.abspath(".").replace("/", "\\").rstrip("\\") + "\\"
    except Exception:
        ws_abs = ""
        ws_abs_back = ""

    if ws_abs:
        # Match case-insensitive file:/// URI prefix up to the workspace root
        pattern = re.compile(re.escape("file:///") + re.escape(ws_abs), re.IGNORECASE)
        text = pattern.sub("", text)
        
        # Match case-insensitive workspace root path itself (no file:/// prefix)
        pattern_raw = re.compile(re.escape(ws_abs), re.IGNORECASE)
        text = pattern_raw.sub("", text)

    if ws_abs_back:
        # Match backslash version of workspace root
        pattern_back = re.compile(re.escape(ws_abs_back), re.IGNORECASE)
        text = pattern_back.sub("", text)

    # Clean other generic file:/// URIs
    text = re.sub(r'file:///([a-zA-Z]:/[^)\s]*)', r'[local path removed]', text)
    # Clean generic Windows absolute paths (e.g. C:/Users/... or C:\Users\...)
    text = re.sub(r'\b[a-zA-Z]:/[^)\s\n\r]*', r'[local path removed]', text)
    text = re.sub(r'\b[a-zA-Z]:\\[^)\s\n\r]*', r'[local path removed]', text)
    return text

class RAGAnswerer:
    """Answers documentation and policy questions by retrieving matched chunks from repo files."""
    def __init__(self, base_dir: str = "."):
        self.retriever = DocRetriever(base_dir)

    def answer(self, question: str, top_k: int = 3) -> str:
        """Retrieves matching chunks and builds a grounded markdown response."""
        chunks = self.retriever.retrieve(question, top_k=top_k)
        
        if not chunks:
            return "No relevant repository documentation was found for this question. Please rephrase or check the walkthrough."
            
        intro = "### 📚 Documentation Reference\n\nBased on the repository documentation, here are the most relevant sections:\n\n"
        
        excerpts_list = []
        for idx, chunk in enumerate(chunks, 1):
            src = chunk.get("source_file", "N/A")
            header = chunk.get("header", "N/A")
            excerpt_text = chunk.get("excerpt", "").strip()
            
            excerpts_list.append(
                f"> **[Reference {idx}]**\n"
                f"> *Source file: [{src}]({src}) (Section: {header})*\n"
                f">\n"
                f"> {excerpt_text}"
            )
            
        body = "\n\n".join(excerpts_list)
        
        disclaimer_text = "⚠️ **Disclaimer**: This response is grounded in repository documentation and does not provide official tax, legal, CRA, CAVCO, Ontario Creates, or SODEC determinations."
        omit_protocols = []
        try:
            from boc_agent.skill.loader import get_active_skill
            skill = get_active_skill()
            if skill.grounding_policy.required_disclaimer:
                disclaimer_text = skill.grounding_policy.required_disclaimer
            omit_protocols = skill.grounding_policy.omit_protocols
        except Exception:
            pass

        disclaimer = f"\n\n---\n{disclaimer_text}"
        full_response = intro + body + disclaimer

        # Enforce grounding policy: omit protocols
        for protocol in omit_protocols:
            full_response = full_response.replace(protocol, "")

        # Post-process response to clean all local absolute path leaks
        full_response = sanitize_absolute_paths(full_response)

        return full_response
