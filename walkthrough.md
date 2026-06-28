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
* **Expected Final Test Count**: **136 passed tests**
* **Verification Areas**:
  - `tests/test_allocation_rules.py` (23 rule validations)
  - `tests/test_orchestrator.py` (8 orchestrator step validations)
  - `tests/test_chat_assistant.py` (12 conversational assistant validations)
  - `tests/test_rag_pipeline.py` (13 documentation retrieval/RAG validations)
  - `tests/test_human_review.py` (6 human override/HITL validations)
  - `tests/test_workbook_loader.py` (12 loader schema validations)
  - `tests/test_dashboard_helpers.py` (2 dashboard stats validations)
  - `tests/test_scaffold.py` (2 scaffold import validations)
  - `tests/test_skill_runtime.py` (9 skill runtime validations)
  - `tests/test_runtime_agent.py` (19 runtime agent validations)
  - `tests/test_runtime_trace.py` (24 runtime trace validations)
  - `tests/test_deployment_files.py` (6 deployment readiness validations)

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

The Conversational Assistant tab is available both before and after ingesting a workbook.

### A. RAG Documentation Queries (Works even BEFORE uploading a workbook)
Enter these prompts in the chat box to fetch grounded markdown excerpts from the repository documentation:
* **Workflow Inquiry**: `"Explain the Human-in-the-Loop workflow."` (retrieves HITL procedures)
* **Architecture Detail**: `"Where is prompt injection handled?"` or `"Explain the architecture."` (retrieves security and block diagrams)
* **Definitions**: `"What is Location 920?"` (retrieves location code context)
* **Limitations**: `"What are the project limitations?"` (retrieves out-of-scope/limitations lists)
* **Difference Check**: `"What is the difference between the chat assistant and RAG?"` (compares dataframe lookup vs document search)

### B. DataFrame Queries (Requires reviewed workbook loaded first)
Once a ledger has been ingested and reviewed:
* **Metrics Summary**: `"summary"` or `"overview of stats"` (returns total, approved, and ineligible counts).
* **Row Detail Lookup (Trans Ref)**: `"explain transaction 508841"` (displays formatting of contractor individual payee details).
* **Row Detail Lookup (Vendor Name)**: `"tell me about Greenslate Pay"` (resolves and formats payroll vendor).
* **Row Detail Lookup (Our Reference)**: `"explain transaction 88888"` (works with schema aliases).
* **Location Filter Breakdown**: `"Show me all Location 920 rows"` (filters and presents ineligible out of Canada spend).
* **Needs Documentation Summary**: `"Which rows need more documents?"` (shows rows flagged for missing evidence).
* **Official Refusal Guardrail**: `"is this officially eligible?"` or `"optimize my tax credit"` (displays official determination disclaimer warning).
* **Missing Row Fallback**: `"explain row 999"` (returns safe `"Transaction not found / run review first"` message).

---

## 🛑 5. Core Guardrails & Limitations

* **Deterministic & Grounded**: The assistant operates completely locally and read-only. It does NOT mutate reviewed dataframe rows or override human reviewer decisions.
* **Pure Local TF-IDF (No Heavy Vector DBs / No PyTorch)**: Built on a lightweight Python TF-IDF embedding vectorizer and Cosine Similarity retriever. There are no dependencies on sentence-transformers, PyTorch, FAISS, ChromaDB, LangChain, or LlamaIndex.
* **Template Excerpt Grounding (No LLM Hallucinations)**: Answers are formulated strictly by extracting and formatting document snippets. No generative LLM is used, guaranteeing zero hallucinations.
* **No Network Calls / No Cloud APIs**: Operates entirely offline without external Vertex AI / Gemini key configurations.
* **No Official Determinations**: The assistant does not make official tax-credit, legal, CRA, CAVCO, Ontario Creates, or SODEC determinations. All official rulings must come from relevant authorities.

---

## 🏗️ 6. SKILL.md Contract & Runtime Architecture Implementation (Phases 9.1 & 9.2)

The repository includes a root `SKILL.md` runtime contract for capabilities, refusals, grounding policies, and non-mutating tool permissions. Phases 9.1 and 9.2 implement the **ADK-inspired local runtime** and execution trace observability layers under `boc_agent/runtime/`.

* **Status**: Local ADK-inspired runtime and tracing are fully implemented and tested.

---

## 📦 7. Docker + Google Cloud Run Deployment Readiness (Phase 10.1)

Phase 10.1 adds deployment-readiness configurations so the Streamlit dashboard and conversational assistant can be built into a Docker image and deployed to Google Cloud Run.

* **Dockerfile & .dockerignore**: Configures optimized caches, non-root user execution, and headless server bindings to port `8080` (retaining RAG docs and demo data).
* **Cloud Run Guide**: Exposes gcloud CLI source-to-service deployments and cost control setups (`--min-instances 0 --max-instances 1`).
* **Roadmap**: Next recommended phase is Phase 10.2 (Cost Guardrails & Budget Docs) followed by Phase 10.3 (ADK / Vertex AI migration).

For details, see:
- [docs/runtime_architecture.md](docs/runtime_architecture.md): Specifications for the implemented local runtime package.
- [docs/adk_mapping.md](docs/adk_mapping.md): Mapping of local-first components to Google ADK and cloud concepts.
- [docs/decision_log.md](docs/decision_log.md): Architecture Decision Records (ADR-001 to ADR-008) governing the project design.
- [docs/deployment_cloud_run.md](docs/deployment_cloud_run.md): Guide for deploying Streamlit to Google Cloud Run.
