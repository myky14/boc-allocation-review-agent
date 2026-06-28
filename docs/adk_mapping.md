# Google ADK Conceptual Mapping

This document outlines how the architectural design of the **BOC Allocation Review Agent** maps to the Google Agent Development Kit (ADK) framework. 

> [!NOTE]
> **Important Clarification**: This project is built on an **ADK-inspired, future ADK-compatible** local runtime pattern. It is **not currently deployed on the native Google ADK framework** or hosted within Google Cloud Agent Engine. It models ADK concepts locally to ensure a seamless future migration.

---

## 1. Architectural Concept Mapping

| Google ADK Concept | Project Equivalent | Current Status | Future Phase | Description |
| --- | --- | --- | --- | --- |
| **Agent** | `BOCReviewAgent` | Implemented | Local Runtime | Encapsulates planning, registry, and execution pipeline layers. |
| **Tool** | `classification_tool`, `eligibility_tool`, `review_tool`, `RAG_retriever` | Implemented | Registry Integration | Individual Python modules wrapping specialized lookup and rule functions. |
| **Skill / Instruction Contract** | `SKILL.md` | Implemented | Runtime Enforcement | Configuration document defining permitted capabilities and tool intents. |
| **Session State** | Streamlit Session State / `RuntimeContext` | Implemented | RuntimeContext | In-memory container storing dialogue history and transaction records. |
| **Retrieval Tool** | Local TF-IDF RAG | Implemented | Vertex AI Search Migration | Document search index built from local Markdown files. |
| **Human-in-the-Loop** | `boc_agent/hitl` | Implemented | Runtime Tool Registration | Separate queue builder and override logging columns. |
| **Deployment** | Local Streamlit / CLI | Docker-ready | Cloud Run / Vertex AI Agent Engine | Execution environment (currently local-first, offline, prepared for Cloud Run). |
| **Execution Trace / Telemetry** | `boc_agent/runtime/trace/` | Implemented | Cloud Trace / Cloud Logging Integration | Monotonic stage latencies, reasoning graphs, and confidence timelines. |

---

## 2. Alignment Status

### What Maps Well Today
- **Decoupled Tools**: Specialist modules (e.g. classification, eligibility) do not contain hardcoded user chat logic and can be registered as discrete, callable functions.
- **Skill-Based Contracts**: The `SKILL.md` parser enforces capability boundaries and checks tool parameters dynamically, matching ADK's configuration contract model.
- **Grounded Retrieval**: The RAG pipeline relies on retrieved markdown chunks rather than generative inference, matching ADK's strict grounding policy concepts.
- **Human Review Isolation**: Override workflows preserve the underlying data state, keeping agent suggestions and human edits distinct.

### What Does Not Exist Yet
- **Native Google ADK SDK Runtime Objects**: The current application does not instantiate native Google ADK agents, sessions, or cloud runtime objects.
- **Active Google Cloud Run Live Instance**: While the containerization files and Cloud Run deployment guide are implemented, a live active cloud service instance has not been provisioned.
- **Gemini / LLM Orchestration**: The system runs entirely locally and deterministically, using no external Vertex AI Gemini LLM APIs.
- **Vertex Vector Search / Vertex AI Search**: The RAG retriever uses a local TF-IDF model rather than a cloud vector database.

---

## 3. Why Local-First Aligns with ADK

ADK emphasizes that agents should be composed of deterministic, modular tools rather than unstructured prompts. By building a local-first, rule-engine-first system:
1. **Tool Independence**: Every tool has a clear, programmatic signature, making cloud wrapper creation trivial.
2. **Contract Enforced Routing**: Routing is treated as a deterministic planner routing task based on configuration parameters, mirroring ADK's agent orchestration design.
3. **Safety First**: Prohibiting mutating operations and isolating the rules engine ensures that moving to a cloud environment introduces no security regression risks.

---

## 4. Future Cloud Migration Path

The possible future cloud architecture could map the planned local agent to Google Cloud services:

```text
Local BOCReviewAgent (Phase 9.1)
        │
        ▼
ADK Agent Wrapper (future native ADK SDK integration)
        │
        ▼
Docker Containerized Service (future Cloud Run API deployment)
        │
        ▼
Vertex AI Agent Engine / Vertex Search (future exploration)
```

During this migration, the core rules engine (`allocation_tool.py`) remains unchanged, guaranteeing that production accounting rules are preserved identically across all hosting targets.
