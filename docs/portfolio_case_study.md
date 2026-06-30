# Portfolio Case Study: BOC Allocation Review Agent

## 1. Problem Statement
Media production projects (e.g. film, television, and digital animation) seeking tax credits under Canadian/Quebec regulations (CAVCO and SODEC) face complex compliance challenges. Allocating creative labor and corporate expenses across regional jurisdictions requires matching transactions against rigid, deterministic regulations. While administrative assistants and accountants historically review these allocations manually, the process is error-prone, time-consuming, and lacks structured audit trails.

---

## 2. Project Goal
The **BOC Allocation Review Agent** is designed as a local-first accounting review support tool to assist accountants in auditing General Ledger (GL) workbooks. It identifies incorrect allocations, logs confidence timeline scores, provides explanation reasoning graphs, flags potential prompt injections, and organizes human-in-the-loop (HITL) review queues. 

*Boundary Statement: The application is strictly an administrative review support aid. It does not provide official tax or legal determinations (not official tax, not legal determinations) and does not compile official tax applications (such as CAVCO Form 6). Currently, there is no Vertex AI or Gemini integration (no vertex, no gemini).*

---

## 3. System Architecture
The application is structured around a decoupled, local-first execution pipeline inspired by Google Agent Development Kit (ADK) patterns:

1. **User Interface / CLI**: Streamlit dashboard or batch terminal processing script.
2. **Orchestrator (BOCReviewAgent)**: Governs the routing, validation registry, execution context, and disclaimer formatting.
3. **Planner**: Classifies capabilities, performs guardrail validations, and routes queries.
4. **Tool Registry**: Manages registered specialist lookup and calculation tools.
5. **Deterministic Specialist Tools**: Executes transaction rules, splits creative shares, and computes eligibility.
6. **Local TF-IDF RAG**: Custom documentation searcher extracting tax rule excerpts.
7. **Runtime Trace Logger**: Generates monotonic timelines detailing execution steps, latency, and confidence scores.

---

## 4. Why Deterministic Rules Instead of LLM Decisions
Large Language Models (LLMs) are probabilistic and prone to hallucinations, formatting drifts, and calculation errors. In accounting compliance, tax allocations must be strictly auditable. For this reason, the agent leaves all eligibility determinations and expense splits to a core **deterministic rule engine** in `allocation_tool.py`. 

The AI orchestrator routes, summarizes, and explains the data, but it is prohibited from altering the rule engine's outputs. This architecture ensures repeatable rule-based suggestions and deterministic, auditable review support.

---

## 5. Why Local TF-IDF RAG
For text-based question answering regarding tax regulations, a local TF-IDF retriever was chosen:
- **Zero Hallucination Grounding**: Answers are formulated strictly by extracting and formatting document snippets from a local directory of documentation-grounded templates based on internal synthetic workbook conventions.
- **Offline & No API Dependency**: Operates entirely offline without external vector databases, embedding APIs, or network calls.
- **Privacy**: Keeps sensitive corporate General Ledger structures and transaction logs within the local filesystem.

---

## 6. Why Human-in-the-Loop (HITL)
To prevent silent errors, any transaction with a confidence score below a designated threshold or marked with a capability refusal is routed to a separate **Human Review Queue**. The agent exports these transactions to an Excel sheet (`human_review_queue.xlsx`) where human reviewers can record manual overrides. These overrides are written to dedicated columns (`human_review_decision`, `human_reviewer`) to preserve the agent's original audit suggestions and maintain a clear audit trail.

---

## 7. Why SKILL.md
A root `SKILL.md` acts as a declarative capability contract. It explicitly registers the agent's capabilities, parameters, grounding policies, and refusal criteria. The local runtime parses and enforces this contract dynamically, ensuring the agent refuses out-of-scope requests (e.g. requests for legal rulings or corporate audits) at the planning stage.

---

## 8. Why ADK-Inspired Runtime
To facilitate future optional cloud integration, the agent's execution layer is modeled after **Google ADK framework primitives**:
- Runtimes, tools, contexts, and planners are structured as independent Python classes.
- Tools are stateless and accept inputs via standard python datatypes.
- This decoupling allows the agent to be wrapped in native Google ADK classes in the future without modifying the underlying rules engine.
- *Status: This is not native Google ADK integration today, but an ADK-inspired design.*

---

## 9. Why Runtime Trace and Observability
For enterprise audibility, every user query generates a detailed `RuntimeTrace` recording:
- Intent classification and capability matching.
- Specialist tool selection and row match counts.
- Step-by-step latency tracking.
- Confidence timeline checkpoints.
- Strict PII and mutation block verification.

This trace is exposed via the Streamlit UI and exported as a local JSON file, ensuring absolute transparency.

---

## 10. Cloud Run Readiness & Cost Guardrails
The Streamlit dashboard is prepared for Google Cloud Run container hosting:
- **Dockerfile**: Employs a non-root `appuser` and optimizes caching using `uv`.
- **Cost Guardrails**: Recommends resource configurations (`--min-instances 0` to scale down to zero when idle, `--max-instances 1` to limit runaway scaling, and modest CPU/memory allocations).
- **Billing alerts**: Recommends Cloud Billing budgets and alert thresholds to track cost exposure without implementing destructive automated shutdowns.
- **Disclaimers**: Acknowledges that budgets are not hard caps and that related resources (like Artifact Registry container images) may still incur costs.

---

## 11. Evaluation & Testing
The repository enforces high code-quality standard through an extensive test harness:
- **307 unit and integration tests** validating allocation logic, schema loading, parser safety, local trace accuracy, and deployment files.
- **Regression suite**: Verifies that new conversational capabilities do not modify core deterministic rules in `allocation_tool.py`.
- **Smoke checks**: A container-ready smoke test (`smoke_deployment.py`) verifies SKILL.md loading, BOCReviewAgent string response, and RuntimeTrace capture.

---

## 12. Key Challenges
- **Circular Imports**: Resolved packaging import bottlenecks where public agent definitions interfered with chat routers by moving eager imports to lazy local imports.
- **Cache-Optimized Container Build**: Structured the Dockerfile layers to copy package configurations and lockfiles first, execute `uv sync --no-install-project`, and copy code afterwards to leverage Docker layer caching.
- **Wording Disclaimers**: Handled the challenge of keeping the agent helpful while preventing it from generating unauthorized tax rulings by wrapping documentation-grounded templates and RAG formatting with strict CRA/CAVCO disclaimers.

---

## 13. Lessons Learned
- **Decoupling Orchestration from Calculation**: Keeping business rules separate from agent routing prevents LLM instability from corrupting compliance data.
- **Local-First Prototyping**: Developing offline-ready TF-IDF retrievers and local trace formats simplifies local debugging and reduces development runtime cost.
- **Safety as a First-Class Citizen**: Restricting tool mutations and isolating credentials early prevents cloud deployment security regressions.

---

## 14. Future Work
- **Optional ADK / Vertex AI Migration**: Transitioning the local orchestration wrappers to native Google Cloud Agent Engine and Vertex AI Search (conceptual plan mapped in `docs/adk_vertex_migration.md`).
- **Multi-Province rules**: Expanding calculation specialists to handle British Columbia Film and Television Tax Credit rules and deeper Quebec regional bonuses.
