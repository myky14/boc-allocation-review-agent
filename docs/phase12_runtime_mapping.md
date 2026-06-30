# Native Google ADK Runtime Component Mapping

This document maps the custom, local ADK-inspired components of `boc-allocation-review-agent` to their official Google ADK, Vertex AI, and Google Cloud Platform equivalents.

> [!IMPORTANT]
> **Current Status & Disclaimer**:
> * **Not Implemented**: This document is a design and feasibility mapping blueprint only. The native ADK integration is not implemented, and Vertex AI / Gemini / Agent Engine services are not deployed.
> * **allocation_tool.py**: Remains unchanged and untouched.
> * **No Gemini Decision Power**: Gemini must not make final allocation or eligibility decisions.

---

## 1. Component Mapping Table

| Current Component | Current Responsibility | Future ADK / Cloud Mapping | Migration Risk | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **ReviewConversationAssistant** | Orchestrates chat exchanges, parses prompts, and manages history. | `adk.Agent` / `adk.Runner` session orchestrator. | Dynamic model responses could bypass standard context guards. | Wrap with `adk.Agent` maintaining local deterministic filters for input/output. |
| **BOCReviewAgent** | Runs planning steps, executes tools, and compiles results. | `adk.Runner` execution engine. | Loss of custom local trace-builder control. | Preserve local engine; subclass or wrap as an ADK-compatible Runner. |
| **Planner** | Selects capability sequences based on intent matching. | ADK Planner / Routing layers. | Over-reliance on LLM routing can cause incorrect tool calls. | Keep deterministic routing; map to ADK Planner using static lookup templates. |
| **Executor** | Runs the selected tools sequentially. | ADK step-executor. | Runtime exceptions or unhandled tool failures. | Maintain local exception safety wrappers inside the ADK executor. |
| **ToolRegistry** | Registers and exposes operational tools. | ADK Tool Registry (`@tool` decorator). | Tool name/signature mismatch during native registration. | Map existing registry to ADK-compatible tools programmatically. |
| **RuntimeContext** | Holds variables and session state for the active run. | ADK Session Memory / State. | Leakage of sensitive transactional data into cloud state. | Keep state local; sanitize or serialize only safe metadata to ADK sessions. |
| **RuntimeTrace** | Tracks latency, confidence, and reasoning steps. | Cloud Logging & Google Cloud Trace. | Overhead of cloud API calls and potential trace payload size limits. | Exporter to ship local JSON traces to Cloud Logging asynchronously. |
| **SKILL.md** | Runtime capability contract. | ADK Agent Manifest / System Instructions. | Inconsistent parsing by native runtime parsers. | Treat SKILL.md as the source of truth for generating ADK manifest files. |
| **Local TF-IDF RAG** | Offline tax document lookup and response formatting. | Vertex AI Search / local fallback. | Online retrieval cost and API latency. | Keep local TF-IDF as the primary cost-free offline RAG fallback. |
| **response_templates.py** | Safe, static templates for deterministic outputs. | Static output formatter inside ADK. | Model attempts to override templates. | Enforce template application downstream of all ADK agent invocations. |
| **allocation_tool.py** | Deterministic allocation rules and policy evaluation. | Read-Only ADK Tool Wrapper. | Risk of LLM trying to execute math or alter classification outputs. | **Keep completely unchanged**. Expose only as a read-only ADK Tool. |
| **Eligibility/Classification Tools** | Deterministic row classification. | Read-Only ADK Tool Wrapper. | Rule logic evasion. | Expose as read-only ADK Tools with strict input validation. |
| **HITL Queue Builder** | Filters rows and builds human review workbooks. | Local helper script (separate from ADK agent). | None (runs as downstream validator). | Keep as standalone post-processing script. |
| **Streamlit Dashboard** | UI for reviewing transactions and trace outputs. | Streamlit hosted on Cloud Run / App Engine. | Dashboard state mismatch. | Maintain local Streamlit frontend calling ADK-wrapped agent. |
| **CLI** | Local batch processing utility. | Local batch wrapper. | Network requirement during local runs. | Keep offline-first mode active in CLI (skipping ADK Cloud calls). |
| **Docker / Cloud Run** | Container definitions and budget parameters. | Containerized ADK Agent deployment. | Cloud billing escalations if budget alerts are missing. | Use standard Dockerfile; include ADK environment config. |

---

## 2. Safety Guidelines for ADK Wrapping
1. **Rule Isolation**: Under no circumstances should native ADK modules directly modify the logic of `allocation_tool.py`.
2. **Deterministic Precedence**: If any discrepancy arises between the native ADK wrapper output and the deterministic local engine, the local engine's result must override.
3. **Data Security**: Keep all transactions in local scope. Do not pass full database rows to remote ADK session handlers.
