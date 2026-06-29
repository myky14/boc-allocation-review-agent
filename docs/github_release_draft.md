# GitHub Release Draft: v2.0.0-portfolio

## Release Title
`v2.0.0-portfolio — Offline-First AI Accounting Review Agent`

## Summary
This release packages the `boc-allocation-review-agent` capstone project for public portfolio presentation and recruiter review. It implements an offline-first administrative co-pilot for production accounting reviews in the Canadian film and television industry.

> [!NOTE]
> This project is designed as an educational portfolio showcase demonstrating agentic architectures, local RAG pipelines, runtime tracing, and Cloud Run deployment readiness. It is not an official compliance or tax engine.

---

## Technical Highlights
* **Deterministic Allocation Review Engine**: The source of truth for this repository's synthetic review workflow and 20-category target allocation suggestions.
* **CLI & Streamlit Dashboard**: Provides both batch workbook processing capabilities and an interactive Human-in-the-Loop review dashboard.
* **Human-in-the-Loop (HITL) Workflow**: Allows production accountants to inspect agent confidence metrics, override classification rules, and export audited queues.
* **Local Conversational Assistant**: Decoupled routing agent that answers ledger queries using local template-based logic.
* **Local Documentation RAG**: Offline-first documentation query pipeline powered by a local TF-IDF index.
* **SKILL.md Runtime Contract**: Machine-readable agent capabilities definition and permission schema.
* **ADK-Inspired Runtime Agent**: Modular local executor featuring decoupled Planner, Executor, and Tool Registry classes.
* **RuntimeTrace Observability**: Latency tracking, confidence stages, and reasoning step logging exported to local JSON traces.
* **Docker & Cloud Run Readiness**: Containerized using a multi-stage `Dockerfile` and configured with cloud cost safety guardrails.
* **246 Automated Tests**: Broad automated test coverage ensuring regression-focused validation.

---

## Verification Commands
Verify the complete project setup and tests locally:
```bash
# 1. Sync dependencies
uv sync

# 2. Run the test harness
uv run pytest

# 3. Execute local smoke deployment check
uv run python scripts/smoke_deployment.py

# 4. Verify compilation
uv run python -m py_compile app.py

# 5. Check git integrity
git diff boc_agent/tools/allocation_tool.py
git diff --check
```

---

## Important Boundaries & Limitations
* **No Official Authority**: Does not provide official tax or legal determinations and does not compile the official CAVCO Form 6.
* **No Live Database Connections**: Does not connect to live government, corporate, or residency registries.
* **Local-First Design**: Utilizes local-first, deterministic, and template-based RAG engines, not live LLM prompts or hosted vector search databases.
* **Deployment Readiness**: The project is container-ready and prepared for Cloud Run, but no active/live deployment has been executed.

---

## Suggested Tag Command
```bash
git tag -a v2.0.0-portfolio -m "Release v2.0.0-portfolio"
git push origin v2.0.0-portfolio
```
