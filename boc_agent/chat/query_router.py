import re

def route_query(question: str) -> str:
    """Classifies a natural language question into an intent string.
    
    Supported intents:
      - 'tax_ruling' (Refusal disclaimer)
      - 'summary' (Overall workbook stats)
      - 'review_queue_summary' (Review queue stats/summary)
      - 'row_explanation' (Specific transaction explanation)
      - 'filter_location' (Location 900/910/920 filters)
      - 'ineligible_summary' (Ineligible rows summary)
      - 'needs_documentation' (Missing/low confidence documentation check)
      - 'unknown'
    """
    q_lower = question.lower().strip()
    
    # 1. Tax Ruling / Refusal check
    tax_keywords = [
        "officially eligible",
        "official eligibility",
        "guarantee this tax",
        "can we claim this officially",
        "make a cavco determination",
        "optimize my tax",
        "tax ruling",
        "official tax",
        "legal eligibility",
        "legal determination",
        "make a sodec determination",
        "provincial creates ruling"
    ]
    if any(kw in q_lower for kw in tax_keywords):
        return "tax_ruling"
        
    # 2. Review Queue Summary
    if "review queue" in q_lower or "human review" in q_lower or "flagged rows" in q_lower or "summarize the queue" in q_lower:
        return "review_queue_summary"
        
    # 3. Location Filter
    if "920" in q_lower or "910" in q_lower or "900" in q_lower or "outside canada" in q_lower or "foreign vendor" in q_lower:
        return "filter_location"
        
    # 4. Ineligible Summary
    if "ineligible" in q_lower or "not eligible" in q_lower or "disallowed" in q_lower:
        return "ineligible_summary"
        
    # 5. Needs Documentation / Missing Evidence
    doc_keywords = [
        "more document", "missing evidence", "needs documents", "documentation",
        "missing tax id", "low confidence", "missing/conflicting", "document needs",
        "missing fields"
    ]
    if any(kw in q_lower for kw in doc_keywords):
        return "needs_documentation"
        
    # 6. Row Explanation (Matches specific references, indices, or names)
    row_keywords = [
        "explain row", "explain transaction", "about row", "about transaction",
        "trans ref", "trans_ref", "our reference", "our_reference", "reference id",
        "who is the vendor for", "what does the agent recommend for", "transaction ref",
        "explain the difference between", "about ", "tell me about", "show me "
    ]
    # Check if keywords match or if there is a Trans Ref number pattern (usually 5 to 7 digits)
    if any(kw in q_lower for kw in row_keywords) or re.search(r'\b(row|transaction|ref|tx)\b\s*\d+', q_lower) or re.search(r'\b\d{5,8}\b', q_lower):
        return "row_explanation"
        
    # 7. Summary
    summary_keywords = [
        "summary", "summarize", "overview", "total rows", "how many rows",
        "row count", "stats", "statistics", "approved count", "approved rows"
    ]
    if any(kw in q_lower for kw in summary_keywords):
        return "summary"
        
    # If question is short, treat it as a possible vendor or reference search (row_explanation)
    if len(q_lower.split()) <= 3 and not re.search(r'[?.!]', q_lower):
        return "row_explanation"
        
    return "unknown"
