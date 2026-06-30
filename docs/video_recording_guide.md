# Video Recording Guide

This document provides step-by-step instructions for recording a 5 to 7 minute presentation walkthrough of the **BOC Allocation Review Agent**.

> [!IMPORTANT]
> **Asset Status**: No demonstration videos exist in this repository. Presenters must record their own video walks from their local workspace.
>
> **Safety boundaries**: No cloud deployment has occurred in this repository. All recording guides below focus on local terminal execution and local Streamlit dashboard views.

---

## 🔒 Recording Safety & Privacy Checklist
Before starting your screen recording software, ensure the following constraints are met:
- **Synthetic Data Only**: Execute all terminal processes and dashboard views using the provided synthetic General Ledger dataset (`data/synthetic/synthetic_boc_gl_dataset.xlsx`).
- **Hide Personal Info**: Close unrelated tabs, messaging apps, and personal folder views. Do not show usernames in terminal paths if possible (use terminal configurations that hide absolute user paths, or clear terminal views).
- **No Credentials**: Ensure no API keys, config secrets, or local credentials are displayed in code blocks during IDE views.
- **No Billing Project IDs**: Avoid opening any GCP billing consoles displaying active corporate project billing details.

---

## 🛠️ Preparation Steps
Prior to recording, run these setup commands in your terminal to ensure clean local datasets and verified states:
```bash
# 1. Synchronize package dependencies
uv sync

# 2. Run the test harness to verify the 307-test suite passes
uv run pytest

# 3. Process the synthetic General Ledger workbook via batch CLI
uv run python -m boc_agent.cli --input data/synthetic/synthetic_boc_gl_dataset.xlsx --output outputs/reviewed_boc_gl_dataset.xlsx

# 4. Generate the Needs Human Review queue workbook (88 rows exported)
uv run python scripts/build_review_queue.py outputs/reviewed_boc_gl_dataset.xlsx outputs/human_review_queue.xlsx

# 5. Launch the Streamlit dashboard locally
uv run streamlit run app.py
```

---

## ⏱️ Suggested Recording Timeline (5 - 7 Minutes)

### 1. Problem Statement & Intro (0:00 - 0:30)
- **Visual**: Repository homepage README or Streamlit Auditor Workspace landing view.
- **Suggested Narration**: 
  > "Hello, today I am walking through the BOC Allocation Review Agent. Media production companies face complex compliance challenges when matching labor and expenses to regional tax credits under Canadian and Quebec rules.
  > This local-first review assistant helps production accountants identify incorrect allocations and review expenses before compiling tax credit applications. 
  > Note that this is strictly a review support aid and does not provide official tax or legal determinations."

### 2. Decoupled Architecture (0:30 - 1:15)
- **Visual**: Display the system diagram from the case study or architecture docs.
- **Suggested Narration**: 
  > "Our architecture is inspired by Google ADK framework primitives. 
  > It decouples conversational planning from rule calculation. 
  > An orchestrator manages planning, tool registry lookup, and tracing, while all calculations are executed by a deterministic rules engine in allocation_tool.py. 
  > This guarantees repeatable rule-based suggestions and complete separation from LLM probabilistic drifts."

### 3. CLI Workbook Review (1:15 - 2:15)
- **Visual**: Terminal window. Run the CLI review command.
- **Suggested Narration**: 
  > "Let's run the batch review CLI. It processes a synthetic General Ledger containing 201 transaction rows. 
  > It matches transactions against our deterministic rules, flags anomalies, and outputs a reviewed workbook in under two seconds. 
  > This local-first processing ensures sensitive financial records remain completely secure and offline."

### 4. Streamlit Dashboard & Metrics (2:15 - 3:30)
- **Visual**: Streamlit Auditor Workspace tab. Show the metrics cards and filters.
- **Suggested Narration**: 
  > "Now, looking at the dashboard, we can load our reviewed file. 
  > Out of 201 processed rows, the agent approved 113 allocations and flagged 88 rows for human review. 
  > Accountants can filter transactions by location, regional credit tags, or rule code to analyze flagged items instantly."

### 5. Human-in-the-Loop Review Queue (3:30 - 4:20)
- **Visual**: Needs Human Review queue table. Point to the Excel export controls.
- **Suggested Narration**: 
  > "To ensure audit integrity, the agent exports all flagged transactions to human_review_queue.xlsx. 
  > Human override decisions are recorded in separate columns, leaving the agent's original suggestions intact. 
  > This preserves a clear audit trail of both the deterministic calculations and human review outcomes."

### 6. Conversational Review Assistant & RAG (4:20 - 5:10)
- **Visual**: Streamlit Review Assistant tab. Type `"What is Location 920?"`.
- **Suggested Narration**: 
  > "Under the Review Assistant tab, accountants can query the workbook and compliance documentation. 
  > When I ask about Location 920, the agent executes our local TF-IDF RAG retriever. 
  > It extracts documentation-grounded templates explaining that Location 920 denotes outside-Canada expenses, grounding the answer without external vector databases or internet dependency."

### 7. Runtime Trace & Observability (5:10 - 5:50)
- **Visual**: Expand the Runtime Trace accordion under the assistant's chat response.
- **Suggested Narration**: 
  > "Every interaction logs a detailed execution trace. 
  > Expanding the accordion, we can audit the step-by-step latency, the planner's intent matching, tool matched row counts, and the confidence timeline score for each stage. 
  > This provides total observability and audit grounding."

### 8. Docker & Cloud Run Readiness (5:50 - 6:30)
- **Visual**: Multi-stage `Dockerfile` and `docs/cost_guardrails.md` in the IDE.
- **Suggested Narration**: 
  > "The application is container-ready, utilizing a non-root user for security. 
  > In cost_guardrails.md, we document recommended configurations to scale down to zero when idle and set up billing console budgets to monitor cost boundaries securely."

### 9. Closing Summary (6:30 - 7:00)
- **Visual**: Return to Streamlit homepage dashboard.
- **Suggested Narration**: 
  > "To conclude, the BOC Allocation Review Agent offers an ADK-inspired, offline-first co-pilot for production accounting reviews. 
  > With our full 307-test suite passing successfully, the system is verified and ready. Thank you!"
