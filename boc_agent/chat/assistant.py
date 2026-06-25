import re
import pandas as pd
from typing import List, Optional
from boc_agent.chat.query_router import route_query
from boc_agent.chat.response_templates import (
    format_summary_response,
    format_row_explanation,
    format_tax_ruling_refusal
)

class ReviewConversationAssistant:
    """Conversational assistant for explaining and querying the reviewed GL workbook.
    
    This is a local-first, deterministic Q&A helper. Phase 8.1 implements
    dataframe Q&A for workbook transaction inquiries, and Phase 8.2 adds
    local deterministic documentation RAG for general policy and setup queries.
    It contains no LLMs and no mutating database operations.
    """

    def _get_column_name(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Finds the actual column name present in the DataFrame from a list of possibilities."""
        for name in possible_names:
            if name in df.columns:
                return name
        return None

    def _resolve_row(self, question: str, df: pd.DataFrame) -> Optional[pd.Series]:
        """Resolves a specific row by Trans Ref, Our Reference, Vendor Name, or Index fallback."""
        q_lower = question.lower()
        
        # 1. Match by Trans Ref / trans_ref
        ref_col = self._get_column_name(df, ["Trans Ref", "trans_ref"])
        if ref_col:
            # Look for 5 to 8 digit numbers in the question
            num_matches = re.findall(r'\b\d{5,8}\b', question)
            for num in num_matches:
                matched_rows = df[df[ref_col].astype(str) == num]
                if not matched_rows.empty:
                    return matched_rows.iloc[0]
                    
        # 2. Match by Our Reference / our_reference
        our_ref_col = self._get_column_name(df, ["Our Reference", "our_reference"])
        if our_ref_col:
            # Look for any number in the question
            num_matches = re.findall(r'\b\d+\b', question)
            for num in num_matches:
                matched_rows = df[df[our_ref_col].astype(str) == num]
                if not matched_rows.empty:
                    return matched_rows.iloc[0]

        # 3. Match by Vendor Name substring
        vendor_col = self._get_column_name(df, ["Vendor Name", "vendor_name"])
        if vendor_col:
            # Check unique vendors to see if any vendor name is mentioned in the question
            unique_vendors = df[vendor_col].dropna().unique()
            # Sort by length descending to match longest substring first
            unique_vendors = sorted(unique_vendors, key=len, reverse=True)
            for vendor in unique_vendors:
                if str(vendor).lower() in q_lower:
                    matched_rows = df[df[vendor_col] == vendor]
                    if not matched_rows.empty:
                        return matched_rows.iloc[0]

        # 4. Fallback: match by Index / Row number
        # Look for patterns like "row 12" or "index 12"
        idx_match = re.search(r'\b(row|index|line)\b\s*(\d+)', q_lower)
        if idx_match:
            idx_num = int(idx_match.group(2))
            # Excel rows usually start at 2 (1-based index + header), but let's support direct pandas index
            if idx_num in df.index:
                return df.loc[idx_num]
            # fallback to 0-based offset
            if 0 <= idx_num < len(df):
                return df.iloc[idx_num]

        return None

    def _check_permissions(self, intent: str, reviewed_df: Optional[pd.DataFrame], skill) -> Optional[str]:
        """Validates tool permissions and constraints against loaded Skill policies."""
        if not skill:
            return None

        # Map intents to required tools defined in SKILL.md
        intent_to_tools = {
            "row_explanation": ["classification_tool", "eligibility_tool", "allocation_tool"],
            "ineligible_summary": ["eligibility_tool"],
            "needs_documentation": ["eligibility_tool"],
            "filter_location": ["eligibility_tool"],
            "rag": ["RAG_retriever"]
        }

        required_tools = intent_to_tools.get(intent, [])
        for tool_name in required_tools:
            tool = next((t for t in skill.tools if t.name.lower() == tool_name.lower()), None)
            if not tool:
                return f"Tool permission denied: {tool_name} is not configured in SKILL.md."

            # Check if intent is permitted by the tool configuration
            if intent not in tool.intents:
                if intent == "filter_location" and "ineligible_summary" in tool.intents:
                    pass
                else:
                    return f"Tool permission denied: {tool_name} is not permitted for intent '{intent}'."

            # Validate mutating constraint
            if tool.mutating:
                return f"Tool permission denied: Mutating tool '{tool_name}' is prohibited."

            # Validate required dataframe constraint
            if tool.required_dataframe and (reviewed_df is None or reviewed_df.empty):
                return f"Tool permission denied: {tool_name} requires a loaded DataFrame."

        return None

    def answer(self, question: str, reviewed_df: Optional[pd.DataFrame]) -> str:
        """Processes the question and returns a grounded answer from the reviewed DataFrame or RAG."""
        skill = None
        try:
            from boc_agent.skill.loader import get_active_skill
            skill = get_active_skill()
        except Exception:
            pass

        intent = route_query(question)

        # 1. Handle Refusals
        if intent == "tax_ruling":
            if skill and skill.refusal_rules:
                q_lower = question.lower().strip()
                for rule in skill.refusal_rules:
                    if any(kw in q_lower for kw in rule.matches):
                        return rule.refusal_response
            return format_tax_ruling_refusal()

        # 2. Check dataframe existence first for dataframe queries
        if intent != "rag" and (reviewed_df is None or reviewed_df.empty):
            return "No reviewed workbook data is currently loaded. Transaction not found / run review first."

        # 3. Check Tool Permissions
        permission_error = self._check_permissions(intent, reviewed_df, skill)
        if permission_error:
            return permission_error

        # 4. Route to execution
        if intent == "rag":
            from boc_agent.rag.rag_answerer import RAGAnswerer
            answerer = RAGAnswerer()
            return answerer.answer(question)

        # Copy is not required since we perform only read-only operations, 
        # but let's keep the operations strictly query-based to prevent any mutations.

        # Get relevant column names (handling original workbook and snake_case headers)
        status_col = self._get_column_name(reviewed_df, ["review_status", "Review Status"])
        eligibility_col = self._get_column_name(reviewed_df, ["eligibility_status", "Eligibility Status"])
        suggested_col = self._get_column_name(reviewed_df, ["suggested_allocation_column", "Suggested Allocation Column"])
        confidence_col = self._get_column_name(reviewed_df, ["confidence_score", "Confidence Score"])
        rationale_col = self._get_column_name(reviewed_df, ["rationale", "Rationale"])
        location_col = self._get_column_name(reviewed_df, ["Location", "location"])

        if intent == "summary":
            total = len(reviewed_df)
            approved = int((reviewed_df[status_col] == "Approved").sum()) if status_col else 0
            needs_review = int((reviewed_df[status_col] == "Needs Human Review").sum()) if status_col else 0
            eligible = int((reviewed_df[eligibility_col] == "Eligible").sum()) if eligibility_col else 0
            needs_elig_review = int((reviewed_df[eligibility_col] == "Needs Review").sum()) if eligibility_col else 0
            ineligible = int((reviewed_df[eligibility_col] == "Ineligible").sum()) if eligibility_col else 0
            
            return format_summary_response(total, approved, needs_review, eligible, needs_elig_review, ineligible)

        elif intent == "row_explanation":
            row = self._resolve_row(question, reviewed_df)
            if row is not None:
                return format_row_explanation(row.to_dict())
            return "Transaction not found / run review first."

        elif intent == "review_queue_summary":
            # Recreate queue filtering logic
            cond_status = (reviewed_df[status_col] == "Needs Human Review") if status_col else pd.Series(False, index=reviewed_df.index)
            cond_rationale = (reviewed_df[rationale_col].astype(str).str.contains("Potential prompt injection|warning|injection", case=False, na=False)) if rationale_col else pd.Series(False, index=reviewed_df.index)
            cond_eligibility = (reviewed_df[eligibility_col] == "Needs Review") if eligibility_col else pd.Series(False, index=reviewed_df.index)
            cond_confidence = (reviewed_df[confidence_col] < 0.8) if confidence_col else pd.Series(False, index=reviewed_df.index)
            
            queue_df = reviewed_df[cond_status | cond_rationale | cond_eligibility | cond_confidence]
            count = len(queue_df)
            
            if count == 0:
                return "Good news! No rows are currently flagged for the human review queue."
                
            # Grab top 3 rationales or themes
            themes = []
            if rationale_col and not queue_df.empty:
                themes = queue_df[rationale_col].value_counts().head(3).index.tolist()
            themes_str = "\n".join([f"- {t}" for t in themes])
            
            # 3 sample rows
            samples = []
            ref_col = self._get_column_name(reviewed_df, ["Trans Ref", "trans_ref"])
            vendor_col = self._get_column_name(reviewed_df, ["Vendor Name", "vendor_name"])
            amount_col = self._get_column_name(reviewed_df, ["Amount", "amount"])
            
            for _, r in queue_df.head(3).iterrows():
                ref_val = r[ref_col] if ref_col else "N/A"
                vendor_val = r[vendor_col] if vendor_col else "N/A"
                amount_val = r[amount_col] if amount_col else 0.0
                rat_val = r[rationale_col] if rationale_col else "N/A"
                samples.append(f"- **Ref {ref_val}** ({vendor_val}, ${amount_val}): *{rat_val}*")
            samples_str = "\n".join(samples)
            
            return f"""### 🔍 Review Queue Summary
There are currently **{count} rows** flagged for human review.

**Top Flagged Themes**:
{themes_str}

**Sample Flagged Rows**:
{samples_str}

*This assistant explains the reviewed workbook. It does not provide official tax-credit determinations.*"""

        elif intent == "filter_location":
            # Identify which location is mentioned in the query
            q_lower = question.lower()
            target_loc = "920"
            if "910" in q_lower:
                target_loc = "910"
            elif "900" in q_lower:
                target_loc = "900"
                
            if not location_col:
                return "Location column not found in DataFrame."
                
            filtered = reviewed_df[reviewed_df[location_col].astype(str).str.startswith(target_loc, na=False)]
            count = len(filtered)
            
            explanation = ""
            if target_loc == "920":
                explanation = "\n*Note: Under deterministic accounting rules, Location 920 represents costs incurred outside of Canada and is treated as ineligible provincial spend.*"
            elif target_loc == "910":
                explanation = "\n*Note: Location 910 represents inter-provincial costs (outside the application province) which typically fall back to Federal tax allocations.*"
            elif target_loc == "900":
                explanation = "\n*Note: Location 900 represents standard costs incurred within the application province.*"
                
            # Summarize outcomes
            outcomes_str = ""
            if count > 0 and suggested_col:
                outcomes = filtered[suggested_col].value_counts()
                outcomes_str = "\n".join([f"- **{col}**: {cnt} rows" for col, cnt in outcomes.items()])
                
            return f"""### 📍 Location {target_loc} Breakdown
Found **{count} rows** mapped to Location {target_loc}.
{explanation}

**Outcome Distribution**:
{outcomes_str if outcomes_str else "No allocations mapped."}

*This assistant explains the reviewed workbook. It does not provide official tax-credit determinations.*"""

        elif intent == "ineligible_summary":
            if not eligibility_col:
                return "Eligibility Status column not found."
                
            filtered = reviewed_df[reviewed_df[eligibility_col] == "Ineligible"]
            count = len(filtered)
            
            outcomes_str = ""
            if count > 0 and suggested_col:
                outcomes = filtered[suggested_col].value_counts()
                outcomes_str = "\n".join([f"- **{col}**: {cnt} rows" for col, cnt in outcomes.items()])
                
            return f"""### 🔴 Ineligible Costs Summary
There are **{count} ineligible rows** in the workbook.

**Outcome Distribution**:
{outcomes_str if outcomes_str else "No ineligible rows."}

*This assistant explains the reviewed workbook. It does not provide official tax-credit determinations.*"""

        elif intent == "needs_documentation":
            cond_review = (reviewed_df[status_col] == "Needs Human Review") if status_col else pd.Series(False, index=reviewed_df.index)
            cond_conf = (reviewed_df[confidence_col] < 0.8) if confidence_col else pd.Series(False, index=reviewed_df.index)
            cond_rat = (reviewed_df[rationale_col].astype(str).str.contains("missing|evidence|document|evidence", case=False, na=False)) if rationale_col else pd.Series(False, index=reviewed_df.index)
            
            filtered = reviewed_df[cond_review | cond_conf | cond_rat]
            count = len(filtered)
            
            samples = []
            ref_col = self._get_column_name(reviewed_df, ["Trans Ref", "trans_ref"])
            vendor_col = self._get_column_name(reviewed_df, ["Vendor Name", "vendor_name"])
            
            for _, r in filtered.head(5).iterrows():
                ref_val = r[ref_col] if ref_col else "N/A"
                vendor_val = r[vendor_col] if vendor_col else "N/A"
                rat_val = r[rationale_col] if rationale_col else "N/A"
                samples.append(f"- **Ref {ref_val}** ({vendor_val}): *{rat_val}*")
            samples_str = "\n".join(samples)
            
            return f"""### 📄 Documentation & Follow-up Actions
Found **{count} rows** that may require manual document requests or additional payee verification.

**Actions Suggested**:
- Request supporting contracts or pay stubs.
- Verify provincial residency documents.
- Inspect original invoices for Location code verification.

**Flagged Transactions**:
{samples_str if samples_str else "No document issues flagged."}

*This assistant explains the reviewed workbook. It does not provide official tax-credit determinations.*"""

        else:
            return ("I'm sorry, I couldn't classify your question. I can help summarize the ledger, "
                    "explain specific transactions (by Trans Ref or vendor name), show Location 920 rows, "
                    "or summarize the human review queue. Please rephrase your question.")
