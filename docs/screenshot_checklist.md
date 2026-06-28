# Screenshot Capture Checklist

This document provides a guide for capturing interface screenshots from your local Streamlit application and codebase to showcase in portfolio presentations or repository write-ups.

> [!IMPORTANT]
> **Asset Status**: No visual assets are pre-packaged in this repository. All screenshot references below denote suggested screens for you to capture manually from your local execution environment.
>
> **Safety boundaries**: No cloud deployment has occurred in this repository. Any cloud console screens must be captured from your own GCP sandboxed environment using synthetic data only.

---

## 🔒 Safety and Confidentiality Rules
Before taking any screenshots, verify the following:
- **Synthetic Data Only**: Run all tools and Streamlit pages using the provided synthetic General Ledger workbook (`data/synthetic/synthetic_boc_gl_dataset.xlsx`).
- **No Financial PII**: Do not capture any screens displaying actual corporate accounting information, true personal salaries, or sensitive vendor details.
- **No Credentials**: Exclude all local path roots (e.g. usernames in paths), active API keys, credentials, or client secrets.
- **No Billing Project IDs**: Exclude or blur Google Cloud billing account numbers or project IDs from any GCP console screens.

---

## 📸 Capture Checklist

### 1. Streamlit Dashboard Screenshots
- [ ] **Streamlit Home / Overview Screen**: Capture this screen showing the main landing workspace of the Streamlit application.
- [ ] **Reviewed Workbook Metrics**: Suggested screenshot of the KPI metric cards showing the breakdown of total processed rows (201 rows processed).
- [ ] **Approved vs Needs Review Counts**: Capture this screen showing the allocation breakdown charts (e.g., 113 approved, 88 routed to the review queue).
- [ ] **Human Review Queue Table**: Capture this screen showing the filtered list of transactions requiring accountant review.
- [ ] **Human Override & Audit Form**: Suggested screenshot showing the interactive columns (`human_review_decision`, `human_reviewer`) where overrides are entered.
- [ ] **Download / Export Controls**: Capture this screen showing the Excel export buttons for saving the reviewed results.

### 2. Conversational Assistant Screenshots
- [ ] **Assistant Summary Query**: Capture this screen showing the Review Assistant responding to `"Show me the review queue summary."`
- [ ] **Row Explanation Query**: Suggested screenshot showing the assistant explaining a transaction (e.g., `"Explain transaction Ref 100"`).
- [ ] **RAG Documentation Query**: Capture this screen showing TF-IDF documentation lookup (e.g. `"What is Location 920?"` explaining outside-Canada handling, or `"Explain Human-in-the-Loop"`).
- [ ] **Safe Refusal Query**: Suggested screenshot showing the assistant politely refusing to make statutory rulings (e.g. `"Can this be officially claimed as a tax credit?"` resulting in a RAG refusal response).

### 3. Runtime Trace Screenshots
- [ ] **Observability Trace Accordion**: Capture this screen showing the expanded Runtime Trace details below the assistant response.
- [ ] **Planner Trace**: Suggested screenshot showing the classified user intent and matching capability.
- [ ] **Tool Trace**: Capture this screen showing the list of matching rules tools executed and the matched row counts.
- [ ] **Confidence Timeline**: Suggested screenshot showing the confidence score timeline checkpoints (Planner, Tool Selection, Row Match, Formatter stages).
- [ ] **Latency Metadata**: Capture this screen showing the step-by-step millisecond execution time logging.

### 4. Code & Deployment Architecture Screenshots
- [ ] **Dockerfile Configuration**: Suggested screenshot of your IDE displaying the multi-stage, cache-optimized `Dockerfile`.
- [ ] **Cost Guardrails Guide**: Capture this screen showing the `docs/cost_guardrails.md` file detailing Console budget alerts and min/max instance configs.
- [ ] **ADK / Vertex Migration Guide**: Suggested screenshot of your IDE showing the conceptual migration roadmap (`docs/adk_vertex_migration.md`).
