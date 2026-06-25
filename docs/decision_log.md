# Architecture Decision Log

This log records the key architectural decisions made during the design and development of the **BOC Allocation Review Agent**.

---

## ADR-001 — Deterministic Rule Engine as Source of Truth

* **Status**: Accepted
* **Context**: Production accounting allocation review in the Canadian film and television industry must be conservative, auditable, and grounded in deterministic workbook evidence. Mistakes can lead to significant audit penalties or lost tax credits. Large Language Models (LLMs) are prone to hallucinations and are unsuitable as authorities for financial compliance rules.
* **Decision**: We use a fully deterministic rules engine (`allocation_tool.py`) as the final source of truth for cost classifications, eligibility suggestions, and claim percentages. The conversational agent and RAG components wrap around this engine and can query it, but are prohibited from overriding or inventing rule outcomes.
* **Consequences**:
  - Zero hallucinated cost allocations.
  - Highly testable and regression-proof rule suite.
  - Lower operational cost (no LLM tokens spent on core classification rules).
* **Future Revisit Conditions**: Revisit if new, highly ambiguous cost categories require probabilistic classification models (e.g. general receipt OCR description sorting).

---

## ADR-002 — Conservative Review Behavior

* **Status**: Accepted
* **Context**: Production audits must identify ineligible expenses to prevent compliance leakage. Obvious claims should be pre-approved, but any ambiguous, inter-provincial, or foreign transactions must be reviewed manually by an accountant.
* **Decision**: Implement a "conservative-first" rule posture. Any transaction containing missing fields, out-of-province payees, or conflicting residency metrics is flagged as `Review Status = Needs Human Review` and `Eligibility Status = Needs Review` (or `Ineligible` if explicitly out-of-scope).
* **Consequences**:
  - Increased Human-in-the-Loop review queue size (88 flagged rows out of 201).
  - Maximizes compliance safety and prevents accidental pre-approval of ineligible items.
* **Future Revisit Conditions**: Revisit if human reviewers request higher confidence thresholds to reduce queue volume.

---

## ADR-003 — Local-First MVP

* **Status**: Accepted
* **Context**: Film production accounting data is highly sensitive and subject to strict confidentiality agreements. Cloud-based LLMs or external database requests introduce privacy and compliance risks.
* **Decision**: Design the MVP as an entirely offline, local-first system. It requires no network calls, cloud databases, external APIs, or keys to load workbook files, run rules, search documentation, or serve the dashboard UI.
* **Consequences**:
  - High performance and immediate response times.
  - Complete data privacy (all processing happens in-memory on the accountant's local workstation).
  - Simple, self-contained local installation process.
* **Future Revisit Conditions**: Revisit when integrating with real ERPs, payroll databases, or live corporate registries requiring cloud APIs.

---

## ADR-004 — TF-IDF RAG Instead of Heavy Vector DB

* **Status**: Accepted
* **Context**: Setting up heavy vector databases (ChromaDB, FAISS, Milvus) and local neural embedding models (SentenceTransformers) requires heavy dependencies (PyTorch, C++ compilers) which complicate local environments and dashboard compilation.
* **Decision**: Implement a lightweight, pure-Python local RAG retrieval system using TF-IDF vectorization and Cosine Similarity. The index is built and queried in-memory from repository markdown files.
* **Consequences**:
  - Zero dependency footprint (no PyTorch or massive wheel installations).
  - Extremely fast execution times (under 5 milliseconds for retrieval).
  - Perfect alignment with local repository documentation scale.
* **Future Revisit Conditions**: Revisit if the corpus scales to thousands of policy PDFs requiring semantic, dense vector search.

---

## ADR-005 — SKILL.md as Runtime Contract

* **Status**: Accepted
* **Context**: Evolving the agent toward Google ADK requires a configuration document that defines what capabilities the agent has, what tools are active, and what refusals are enforced, separated from Python code.
* **Decision**: Establish the root `SKILL.md` file as a machine-readable runtime contract parsed at application startup. The current query router and future runtime executor validate requests against the capabilities, tool scopes, and disclaimers specified inside `SKILL.md`.
* **Consequences**:
  - Changes to safety wording, disclaimer texts, and permitted capabilities can be made directly in `SKILL.md` without modifying core code.
  - Future ADK migration can map cleanly to native ADK skill or instruction manifests.
* **Future Revisit Conditions**: Revisit if multiple independent agent personas are introduced requiring separate, concurrent skill files.

---

## ADR-006 — Human Decisions Stored Separately

* **Status**: Accepted
* **Context**: A critical requirement of Human-in-the-Loop workflows is that the user's manual adjustments must be recorded transparently without destroying the audit trail of what the agent originally suggested.
* **Decision**: Design the Streamlit review dashboard to export human overrides and decisions into separate columns prefixed with `human_` (e.g. `human_suggested_allocation_column`, `human_review_status`). The agent's original suggestions are preserved intact.
* **Consequences**:
  - Clean comparison datasets for evaluation.
  - Uncompromised audit trail for production compliance records.
* **Future Revisit Conditions**: Revisit if ERP import specifications restrict column counts or schemas.

---

## ADR-007 — ADK-Inspired Runtime Before Cloud Deployment

* **Status**: Accepted
* **Context**: Cloud deployment is expensive, complex, and requires setting up secrets and Vertex AI services. Transitioning immediately to the cloud makes local debugging and rapid iteration difficult.
* **Decision**: Design a modular, ADK-inspired runtime architecture locally in Phase 9.0, then implement it in Phase 9.1 using standard Python structures before considering cloud runtime components.
* **Consequences**:
  - Easy offline testing and troubleshooting.
  - The local Streamlit dashboard and CLI pipelines remain functional.
  - Clear cloud roadmap with predefined interfaces.
* **Future Revisit Conditions**: Revisit when starting cloud deployment phases (GCP / Vertex AI Agent Engine).
