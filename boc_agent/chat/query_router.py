import re

def route_query(question: str) -> str:
    """Classifies a natural language question into an intent string.
    
    Supported intents:
      - 'tax_ruling' (Disclaimer warning refusal)
      - 'row_explanation' (Specific transaction explanation)
      - 'review_queue_summary' (Review queue stats/summary)
      - 'filter_location' (Location 900/910/920 filters)
      - 'ineligible_summary' (Ineligible rows summary)
      - 'needs_documentation' (Missing/low confidence documentation check)
      - 'summary' (Overall workbook stats)
      - 'rag' (Documentation / Policy / Setup RAG lookup)
      - 'unknown'
      
    Priority Order:
      1. Tax/legal refusal intent
      2. Row/dataframe intent (specific row explanation)
      3. Review queue, status, location, ineligible dataframe intents
      4. Documentation/RAG intent
      5. Unknown
    """
    q_lower = question.lower().strip()
    
    # 1. Tax Ruling / Refusal check (Priority 1)
    tax_keywords = [
        "officially eligible", "official eligibility", "guarantee this tax",
        "can we claim this officially", "make a cavco determination", "optimize my tax",
        "tax ruling", "official tax", "legal eligibility", "legal determination",
        "make a sodec determination", "provincial creates ruling"
    ]
    if any(kw in q_lower for kw in tax_keywords):
        return "tax_ruling"
        
    # Check if there are row indicators
    has_specific_ref = any(kw in q_lower for kw in ["trans ref", "trans_ref", "our reference", "our_reference", "reference id", "transaction ref"])
    has_row_number = re.search(r'\b(row|index|line|tx|transaction)\b\s*\d+', q_lower) is not None
    has_digit_id = re.search(r'\b\d{5,8}\b', q_lower) is not None

    # Check if the query is a documentation question (starts with "what is", "how does", contains "workflow", etc.)
    doc_keywords = [
        "what is", "what does", "explain the", "how does", "where is", "why does",
        "architecture", "workflow", "process", "limitation", "limitations", "difference between", 
        "rules engine", "prompt injection", "ruling", "policy", "documentation", 
        "walkthrough", "setup", "install", "meaning of", "means", "sodec", "creates", "cavco", "cra"
    ]
    is_doc_q = any(kw in q_lower for kw in doc_keywords)
    
    # Specific row references override documentation classification
    if has_digit_id or has_row_number or has_specific_ref:
        is_doc_q = False

    # 2. Specific Row Explanation Intent
    row_keywords = [
        "explain row", "explain transaction", "about row", "about transaction",
        "who is the vendor for", "what does the agent recommend for",
        "explain transaction ref", "tell me about"
    ]
    is_row_intent = any(kw in q_lower for kw in row_keywords) or has_row_number or has_digit_id or has_specific_ref
    
    # Short query (3 words or less, no punctuation) -> treat as vendor name search
    # But only if it's not a doc query, and does not contain location/summary/queue/tax/eligibility terms
    reserved_terms = [
        "920", "910", "900", "outside canada", "foreign vendor", 
        "summary", "summarize", "overview", "stats", "statistics", "count",
        "review queue", "human review", "flagged", "ineligible", "not eligible", "disallowed",
        "tax", "legal", "officially", "eligible", "document", "documentation", "evidence", "rules"
    ]
    is_vendor_search = (
        len(q_lower.split()) <= 3 
        and not re.search(r'[?.!]', q_lower) 
        and not any(kw in q_lower for kw in reserved_terms)
        and not is_doc_q
    )
    
    if (is_row_intent or is_vendor_search) and not is_doc_q:
        return "row_explanation"

    # 3. DataFrame aggregate/filter intents (Only if not a doc query)
    if not is_doc_q:
        # Review Queue Summary
        if "review queue" in q_lower or "human review" in q_lower or "flagged rows" in q_lower or "summarize the queue" in q_lower:
            return "review_queue_summary"
            
        # Location Filter
        if "920" in q_lower or "910" in q_lower or "900" in q_lower or "outside canada" in q_lower or "foreign vendor" in q_lower:
            return "filter_location"
            
        # Ineligible Summary
        if "ineligible" in q_lower or "not eligible" in q_lower or "disallowed" in q_lower:
            return "ineligible_summary"
            
        # Needs Documentation
        doc_indicator_words = [
            "more document", "missing evidence", "needs documents", "documentation",
            "missing tax id", "low confidence", "missing/conflicting", "document needs",
            "missing fields"
        ]
        if any(kw in q_lower for kw in doc_indicator_words):
            return "needs_documentation"
            
        # Overall Summary stats
        summary_keywords = [
            "summary", "summarize", "overview", "total rows", "how many rows",
            "row count", "stats", "statistics", "approved count", "approved rows"
        ]
        if any(kw in q_lower for kw in summary_keywords):
            return "summary"

    # 4. RAG Intent (Triggered if identified as a doc question or has doc keywords)
    # Must also contain at least one repository/domain keyword to prevent generic noise routing
    domain_terms = [
        "location", "ep", "rule", "rules", "workflow", "process", "human", "review", 
        "agent", "architecture", "limitation", "limitations", "setup", "install", 
        "installation", "difference", "individual", "salary", "loan-out", "multi-share", 
        "document", "documentation", "provincial", "creates", "sodec", "cavco", "cra", 
        "inject", "injection", "guardrail", "assistant", "rag", "walkthrough", "900", "910", "920", 
        "45", "41", "42"
    ]
    has_domain_term = any(t in q_lower for t in domain_terms)
    
    if (is_doc_q or any(kw in q_lower for kw in doc_keywords)) and has_domain_term:
        return "rag"
        
    return "unknown"
