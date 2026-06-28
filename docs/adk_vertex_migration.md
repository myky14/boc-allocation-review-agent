# Optional ADK / Vertex AI Migration Guide

This document describes a conceptual, future migration path for transitioning the local-first Streamlit application to Google Cloud's native AI Agent stack. 

---

## 1. Purpose

This repository intentionally implements an ADK-inspired local runtime to achieve a deterministic, offline accounting review with zero dependency on cloud-based AI. 

Transitioning the application to native Google Cloud AI services is **entirely optional**. Any future migration to managed Google Cloud Agent frameworks is intended strictly as a runtime orchestration transition and should not modify the underlying statutory rules.

---

## 2. Current Architecture

The current implementation utilizes a local, non-mutating execution pipeline:

```
[User Request]
      ↓
ReviewConversationAssistant (boc_agent/chat/assistant.py)
      ↓
BOCReviewAgent (boc_agent/runtime/agent.py)
      ↓
Planner (boc_agent/runtime/planner.py)
      ↓
Executor (boc_agent/runtime/executor.py)
      ↓
ToolRegistry (boc_agent/runtime/registry.py)
      ↓
ResponseBuilder (boc_agent/runtime/builder.py)
      ↓
RuntimeTrace (boc_agent/runtime/trace/trace_models.py)
      ↓
Streamlit UI Dashboard (app.py)
```

Key features of this local architecture:
- **SKILL.md Contract**: Standardizes model descriptions, capability registrations, and grounding rules.
- **Local TF-IDF RAG**: Custom local database searcher (`rag_answerer.py`) utilizing local markdown documentation files without external web APIs.
- **Deterministic Rule Engine**: Governed entirely by `allocation_tool.py` as the deterministic source of truth.
- **Runtime Trace & Observability**: Local execution logs mapping timeline steps, latencies, and stage confidence checklists.
- **Cloud Run Readiness**: Production-ready container configs (`Dockerfile`, `.dockerignore`) configured to run locally or under safe instance scaling.

---

## 3. Google ADK Mapping

The table below outlines a conceptual mapping of current local-first runtime classes to native Google Agent Development Kit (ADK) constructs. 

| Current Component | Possible Google ADK Component | Description of Conceptual Mapping |
| :--- | :--- | :--- |
| `ReviewConversationAssistant` | `Agent` | The orchestrating agent entity managing conversational steps and routing logic. |
| `Planner` | `Planner` | Classifies capabilities, detects prompt injections, and determines appropriate execution paths. |
| `Executor` | Tool execution wrapper | Executes selected tools within a sandbox and records rows accessed and output statuses. |
| `ToolRegistry` | Tool Registry | Registration module declaring tool names, docstrings, parameters, and return types. |
| `RuntimeContext` | Session State | Manages ephemeral metadata and active workbook states across conversational exchanges. |
| `RuntimeTrace` | Execution Trace | Structured logger mapping latency times, planning outputs, and reasoning milestones. |
| `SKILL.md` | Skill definition | Root definition defining agent capabilities, grounding constraints, and error policies. |
| `ResponseBuilder` | Response Composer | Combines tool outputs, RAG document snippets, and disclaimers into clean string formats. |

---

## 4. Vertex AI Mapping

This table outlines how local infrastructure elements conceptually map to Vertex AI and Google Cloud managed services. 

| Current Component | Possible Vertex Service | Description of Conceptual Mapping |
| :--- | :--- | :--- |
| Local ADK-Inspired Runtime | Vertex AI Agent Engine | Managed execution environment for running orchestrations, handling session states, and scaling instances. |
| Local TF-IDF RAG | Vertex AI Search | Managed vector search or grounding indexes containing tax documentation and rule guides. |
| RuntimeTrace | Cloud Trace / Cloud Logging | Persistent telemetry store for logging agent execution traces and latency metrics. |
| RuntimeContext Session | Vertex Agent Session | Managed conversation history and agent session storage. |
| Docker Container | Cloud Run | Secure, autoscaled container runner hosting the user-facing Streamlit dashboard. |

*Note: Google ADK is not implemented today. Vertex AI Agent Engine is not deployed in this repository. Gemini is not integrated in this codebase. Vertex AI Search is not active. Managed sessions are not implemented. No native cloud agent deployment exists.*

---

## 5. Migration Strategy

Any future migration should proceed in distinct, backward-compatible phases:

1. **Step 1: Core Protection**: Maintain the deterministic rule engine in `allocation_tool.py` completely unchanged to preserve rule compliance.
2. **Step 2: Replace Planner**: Replace the local classification rules in `planner.py` with a Vertex AI prompt classifier or a Gemini model agent.
3. **Step 3: Replace Runtime**: Migrate `BOCReviewAgent` orchestration into a native Google ADK `Agent` structure.
4. **Step 4: Move Tool Registry**: Transition local Python functions in `ToolRegistry` to registered Vertex AI Agent Engine tools.
5. **Step 5: Replace RAG**: Transition the local TF-IDF searcher to a Vertex AI Search data store (optional).
6. **Step 6: Enable Vertex AI Agent Engine**: Deploy the fully-integrated ADK agent onto Vertex AI Agent Engine infrastructure.

---

## 6. Components That MUST NOT Change

To preserve audit integrity, the core accounting rules must remain isolated from conversational models. The following files and logics must remain unchanged:
- **allocation_tool.py**: Serves as the deterministic source of truth for CAVCO/SODEC eligibility and allocation limits. It must remain unchanged during migration.
- **Eligibility Rules**: Deterministic logic governing multi-share splits, citizenship, and residency checks.
- **Confidence Calculations**: Calculated using exact matching heuristics.
- **Review Thresholds**: Rules determining whether transaction data needs human reviewer follow-up.
- **Human Review overrides**: Separate columns recording review outcomes (`human_review_decision`, etc.) to maintain a clear audit trail.
- **Rule Engine and DataFrame operations**: Pure Python dataframe manipulation logic.

**Orchestration changes only**: Google ADK / Vertex AI migration should replace orchestration and runtime routing layers only, never the core accounting rules.

---

## 7. Components That MAY Change

- **Planner**: Natural language classification models can replace static keyword classifications.
- **Runtime**: Native Google ADK framework orchestration can manage conversational transitions.
- **Tracing Backend**: Cloud Trace and Google Cloud Logging can store telemetry in place of local JSON output.
- **Search Backend**: Vertex AI Search indexes can host documents.
- **Conversation Memory**: Vertex Session stores can track historical contexts.
- **Deployment Target**: Host the ADK agent natively on Vertex AI Agent Engine.
- **Authentication**: Google Cloud IAM.
- **Cloud Logging**: Standard GCP billing alerts and resource logging.

---

## 8. Risks & Mitigations

| Risk | Description | Mitigation Strategy |
| :--- | :--- | :--- |
| **Hallucination Risk** | LLMs could output incorrect tax calculations. | Enforce strict grounding. Run calculations in `allocation_tool.py` without LLM intervention. |
| **Permission Drift** | Cloud roles could allow unauthorized writes. | Apply least-privilege IAM policies, restricting agent permissions to read-only sheets. |
| **Cloud Cost** | Interactive Gemini API calls could increase billing. | Configure Cloud Billing budget alerts, min/max instances, and API consumption limits. |
| **Latency** | Network hops to Vertex AI could delay UI updates. | Pre-fetch context or utilize asynchronous processing for background audits. |
| **Observability** | Multi-hop cloud executions are hard to debug. | Export detailed execution traces to Cloud Logging and Cloud Trace. |
| **Skill Drift** | Updated models could interpret SKILL rules differently. | Run local regression evaluation datasets post-deployment to verify behavior. |

---

## 9. Migration Checklist

- [ ] Runtime abstraction complete
- [ ] Tool registry abstraction
- [ ] Stateless tools verified
- [ ] Skill contract validated
- [ ] Runtime tracing complete
- [ ] Deployment containerized
- [ ] Cloud Run ready
- [ ] Budget guardrails configured
- [ ] Vertex credentials verified
- [ ] Agent Engine deployment verified

---

## 10. What This Repository Implements Today

| Capability | Local-First Implementation Status |
| :--- | :--- |
| **Deterministic Accounting** | ✓ Implemented via `allocation_tool.py` |
| **Local Runtime** | ✓ Implemented via `boc_agent/runtime/` |
| **Local RAG** | ✓ Implemented via `boc_agent/rag/` |
| **Local Trace** | ✓ Implemented via `boc_agent/runtime/trace/` |
| **Cloud Run Deployment Readiness** | ✓ Implemented via `Dockerfile` and `.dockerignore` |
| **Budget Guidance** | ✓ Implemented via `docs/cost_guardrails.md` |
| **Native Google ADK** | ✗ Not implemented today |
| **Vertex AI Agent Engine** | ✗ Not implemented today |
| **Gemini Integration** | ✗ Not implemented today |
| **Google Search** | ✗ Not implemented today |
| **Managed Sessions** | ✗ Not implemented today |
