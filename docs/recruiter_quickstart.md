# Recruiter & Hiring Manager Quick-Start Guide

Welcome! This guide provides a high-level technical overview of the `boc-allocation-review-agent` capstone project to help recruiters, hiring managers, and technical interviewers evaluate the codebase efficiently.

---

## 🔍 What This Project Is
The **BOC Allocation Review Agent** is an offline-first administrative review assistant designed for the Canadian film and television industry. It assists production accountants by reviewing General Ledger (GL) entries for provincial (Ontario Creates/SODEC) and federal tax-credit eligibility.

The core architecture wraps a deterministic rule-based allocation engine with an ADK-inspired runtime, a local TF-IDF RAG pipeline, structured execution tracing, and a Streamlit dashboard.

---

## 🎯 What to Look at First
1. **Core Runtime**: Inspect [boc_agent/runtime/](../boc_agent/runtime/) (`agent.py`, `planner.py`, `executor.py`) to see the decoupled agent execution design.
2. **Deterministic Rules**: See [boc_agent/tools/allocation_tool.py](../boc_agent/tools/allocation_tool.py) for the final source of truth on eligibility rules.
3. **Observability**: Look at [boc_agent/runtime/trace/](../boc_agent/runtime/trace/) to review the structured auditing trace implementation.
4. **Portfolio Case Study**: Read [portfolio_case_study.md](portfolio_case_study.md) for detailed design decisions, trade-offs, and architecture flow.

---

## ⏱️ 3-Minute Review Path
1. **Project Hero (README)**: Skim the [README.md](../README.md) to understand the workflow and local setup.
2. **Architecture Blueprint**: Review the diagram in [runtime_architecture.md](runtime_architecture.md).
3. **Test Suite Execution**: Notice the 287 unit and integration tests covering allocation rules, loader schemas, and RAG pipelines.
4. **Deployment Readiness**: Review the [Dockerfile](../Dockerfile) and [deployment_cloud_run.md](deployment_cloud_run.md) demonstrating container readiness.

---

## 🛠️ Technical Highlights
* **Deterministic Eligibility sugerstions**: Appends structured tax-credit metadata to ledger transactions based on location, account codes, and province.
* **Human-in-the-Loop Review Dashboard**: Streamlit interface letting accountants override rules and export audited sheets.
* **ADK-inspired Modular Agent**: Decoupled tool execution model utilizing a central Tool Registry.
* **Structured Auditing Trace**: Captures reasoning steps, confidence stages, and latency metrics locally.
* **Cloud Run Deployment Ready**: Fully containerized with strict cost safety guardrails.

---

## ⚠️ What This Project Does Not Claim
* **Not a Tax Authority**: It provides review support based on internal synthetic workbook conventions, not official statutory or legal tax credit determinations.
* **No Live Cloud Deployments**: The system is container-ready, but is not currently deployed to Cloud Run.
* **No Live LLM API Primitives**: Uses deterministic templates and a local TF-IDF document RAG index, ensuring zero API runtime costs and strict data privacy.

---

## 💻 Quick Setup & Execution
Run the system locally in less than a minute:
```bash
# Install dependencies
uv sync

# Run the test suite
uv run pytest

# Execute smoke deployment checks
uv run python scripts/smoke_deployment.py

# Launch the Streamlit dashboard
uv run streamlit run app.py
```
