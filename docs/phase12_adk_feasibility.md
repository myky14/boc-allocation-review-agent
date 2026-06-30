# Native Google ADK Migration Feasibility Analysis

This document provides a technical feasibility analysis for replacing or wrapping the custom local ADK-inspired agentic runtime of `boc-allocation-review-agent` with the official Google Agent Development Kit (ADK) in a future release.

> [!IMPORTANT]
> **Current Status & Disclaimer**:
> * **Not Implemented**: This phase is a design and feasibility blueprint only. This phase does not implement native ADK.
> * **Active Local Runtime**: The existing ADK-inspired local runtime remains active as the sole operational execution layer.
> * **allocation_tool.py Frozen**: The deterministic rule engine (`boc_agent/tools/allocation_tool.py`) remains completely untouched and is the final source of truth for this repository's synthetic review workflow.
> * **No Cloud Deployment**: Vertex AI, Gemini, and Cloud Agent Engine are not deployed. Native ADK migration is future optional work.
> * **No LLM Decision Authority**: Gemini / LLM models must not make final allocation or eligibility decisions.

---

## 1. Purpose
Evaluate the readiness, benefits, and architectural implications of adopting native Google ADK components to wrap or migrate the current custom Planner/Executor loop.

---

## 2. Current Local Runtime Summary
The current agent runtime is an offline-first system composed of:
* **Planner**: Determines which capabilities (capabilities registry) to execute next.
* **Executor**: Processes step sequences and runs tools.
* **ToolRegistry**: Manages custom capabilities (e.g. TF-IDF retrieval, classification rules).
* **RuntimeContext**: Tracks row data and audit traces across steps.
* **RuntimeTrace**: Collects monotonic latency, confidence values, and reasons.

This architecture runs locally, offline, and deterministically.

---

## 3. Candidate Native ADK Components
* **ADK Agent/Runner**: To encapsulate execution state and orchestrate calls.
* **ADK Tools**: To register deterministic helper tools (`allocation_tool.py` wrappers).
* **ADK Sessions**: To manage execution scope and memory across interactions.
* **ADK Observability**: Exporting traces to Google Cloud Trace and Cloud Logging.

---

## 4. What Can Migrate Safely
* **Tool Definitions**: Exposing local read-only functions as ADK-decorated tools.
* **Trace Metadata**: Exposing the local `RuntimeTrace` structure via structured logs.
* **Planner Routing**: The custom sequence planner can map to ADK planners/routing definitions in future phases.

---

## 5. What Must Remain Unchanged
* **allocation_tool.py**: The deterministic allocation rules must stay frozen. No business logic can be migrated to dynamic code.
* **Human-in-the-Loop Queue Builder**: The logic for filtering transaction rows (`Needs Human Review`) must remain deterministic.
* **Local-First Fallback**: The CLI and local test suites must remain fully functional offline.

---

## 6. What Must NOT be Delegated to Gemini/LLM
* **Final Allocation Decisions**: Gemini must not make final allocation or eligibility decisions.
* **Transaction Math**: Cost and rate arithmetic must remain deterministic.
* **Workbook Mutation**: Gemini must not write or directly mutate output Excel worksheets.

---

## 7. Required Security Boundaries
* **Least-Privilege Service Accounts**: Future deployment must prefer user-specified service accounts with limited access rather than default computer credentials.
* **Data Access Control**: Sensitive transaction logs must not be sent to external LLMs.
* **Network Isolation**: Maintain local offline execution capabilities for private compliance workflows.

---

## 8. Cost and Deployment Implications
* **Zero Run-Time Cost Fallback**: The offline local TF-IDF RAG system guarantees zero API fees for local operations.
* **Managed Services Costs**: Future deployment to Vertex AI Agent Engine or Cloud Run will incur standard compute fees. Budgets and cloud trace limits must be strictly configured.

---

## 9. Feasibility Verdict
* **Verdict**: **Proceed only with Phase 12.1 proof-of-concept wrapper, not a full runtime replacement.**
* **Justification**: A full native replacement introduces risks of vendor lock-in and breaks the offline-first requirement. A wrapper bridge ensures we get ADK compatibility while preserving the deterministic local runtime.

---

## 10. Recommended Next Step
Proceed with **Phase 12.1 — Native ADK Wrapper POC**, which builds a minimal experimental bridge (`experiments/adk_poc/` or `boc_agent/adk_bridge/`) to test parity without changing runtime production code.
