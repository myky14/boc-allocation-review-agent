# Walkthrough & Verification Guide

This document provides step-by-step setup, execution, verification, and demo instructions for the **BOC Allocation Review Agent**.

---

## 🛠️ 1. Installation & Environment Setup

Synchronize dependencies and prepare the python environment:
```bash
uv sync
```

---

## 🧪 2. Run the Verification Suite (Tests)

Run the comprehensive unit and integration test suite:
```bash
uv run pytest
```
* **Expected Final Test Count**: **65 passed tests**
* **Verification Areas**:
  - `tests/test_allocation_rules.py` (23 rule validations)
  - `tests/test_orchestrator.py` (8 orchestrator step validations)
  - `tests/test_chat_assistant.py` (12 conversational assistant validations)
  - `tests/test_human_review.py` (6 human override/HITL validations)
  - `tests/test_workbook_loader.py` (12 loader schema validations)
  - `tests/test_dashboard_helpers.py` (2 dashboard stats validations)
  - `tests/test_scaffold.py` (2 scaffold import validations)

---

## 🚀 3. Run the Agent Pipeline & Review Commands

### A. Run Batch Review Agent (CLI)
Analyze the synthetic General Ledger workbook and generate suggested allocations:
```bash
uv run python -m boc_agent.cli --input data/synthetic/synthetic_boc_gl_dataset.xlsx --output outputs/reviewed_boc_gl_dataset.xlsx
```
* **Result**: Processes 201 transaction rows successfully and outputs `outputs/reviewed_boc_gl_dataset.xlsx` with suggestions appended.

### B. Run Evaluation Summary
Analyze accuracy rates, status distributions, and rule highlights:
```bash
uv run python scripts/evaluate_outputs.py outputs/reviewed_boc_gl_dataset.xlsx
```
* **Result**: Displays distribution breakdown (113 Approved, 88 Needs Human Review).

### C. Run HITL Queue Builder
Extract transactions flagged for human attention:
```bash
uv run python scripts/build_review_queue.py outputs/reviewed_boc_gl_dataset.xlsx outputs/human_review_queue.xlsx
```
* **Result**: Exports exactly 88 flagged rows into `outputs/human_review_queue.xlsx`.

### D. Run Streamlit Dashboard
Launch the interactive audit reviewer and conversational assistant UI:
```bash
uv run streamlit run app.py
```
* **Result**: Launches local web server on port 8501.

---

## 💬 4. Conversational Assistant Demo Prompts

Once the Streamlit Dashboard is running and a ledger has been ingested and reviewed:
1. Navigate to the **"💬 Conversational Assistant"** tab.
2. Enter these sample prompts to verify the assistant's behavior:
   - **Metrics Summary**: `"summary"` or `"overview of stats"` (returns total, approved, and ineligible counts).
   - **Row Detail Lookup (Trans Ref)**: `"explain transaction 508841"` (displays formatting of contractor individual payee details).
   - **Row Detail Lookup (Vendor Name)**: `"tell me about Greenslate Pay"` (resolves and formats payroll vendor).
   - **Row Detail Lookup (Our Reference)**: `"explain transaction 88888"` (works with schema aliases).
   - **Location Filter Breakdown**: `"Show me all Location 920 rows"` (filters and presents ineligible out of Canada spend).
   - **Needs Documentation Summary**: `"Which rows need more documents?"` (shows rows flagged for missing evidence).
   - **Official Refusal Guardrail**: `"is this officially eligible?"` or `"optimize my tax credit"` (displays official determination disclaimer warning).
   - **Missing Row Fallback**: `"explain row 999"` (returns safe `"Transaction not found / run review first"` message).

---

## 🛑 5. Core Guardrails & Limitations

* **Deterministic & Grounded**: The assistant operates completely locally and read-only. It does NOT mutate reviewed dataframe rows.
* **No RAG / No LLMs**: This is Phase 8.1 (deterministic local-first Q&A). There are no external Vertex AI/Gemini API calls, network calls, or regulatory database connections.
* **No Official Determinations**: The assistant does not make official tax-credit, legal, CRA, CAVCO, Ontario Creates, or SODEC determinations. All official rulings must come from relevant authorities.
