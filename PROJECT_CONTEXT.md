# PROJECT_CONTEXT.md

## 1. Project Summary

* **Project Name**: BOC Allocation Review Agent
* **Capstone Track**: Kaggle AI Agents Intensive Capstone Project — Agents for Business Track
* **Repository**: `boc-allocation-review-agent`
* **Context**: This is a practical production-accounting support tool designed for the Canadian film and television industry. It assists production accountants in reviewing General Ledger (GL) entries for Breakdown of Costs (BOC) and CAVCO/provincial tax credit eligibility.
* **Scope boundaries**:
  - It is **NOT** a legal or tax authority and does not provide authoritative tax-credit determinations.
  - It does **NOT** compile or generate the official CAVCO Form 6.
  - It does **NOT** connect to live external databases (e.g. CRA, CAVCO, Ontario Creates, SODEC, ERP, payroll, residency, citizenship, or corporate registries).
* **Architecture Style**: Local-first, rule-engine-first MVP. ADK-inspired orchestration, chat, RAG, HITL, and planned runtime layers wrap around the core deterministic rule engine. The deterministic rules are the final source of truth.

---

## 2. What the Agent Does

* **Input**:
  - A synthetic, pre-cleaned and enriched General Ledger (GL) workbook in Excel (`.xlsx`) or CSV (`.csv`) format.
* **Output**:
  - A reviewed workbook (or CSV) containing the original data with the following agent-generated suggestion and metadata columns appended:
    - `suggested_allocation_column`: Suggested target allocation column (out of 20 possible buckets).
    - `amount_percentage`: Claim percentage represented on a 0.0 to 100.0 scale (e.g., `100.0` or `65.0`).
    - `eligibility_status`: Inferred eligibility status (`Eligible`, `Ineligible`, or `Needs Review`).
    - `confidence_score`: Quantitative reliability score between `0.0` and `1.0`.
    - `review_status`: Final review flag recommended for the accountant. Supported values:
      - `Approved`
      - `Needs Human Review`
    - `rationale`: Explanation string listing applied policy checks and any flagged warnings.
    - `reference_rule`: Reference identifier of the rule applied (e.g., `RULE_OUT_OF_CANADA`).
    - `secondary_allocation_note`: Detailed splits or instructions (e.g., for multi-share creative labor or VICE Canada Quebec fallbacks).

---

## 3. Repository Structure

The current repository layout:
* README.md: Main documentation and setup guide.
* PROJECT_CONTEXT.md: This handoff context file.
* `docs/`: Design and planning specifications:
  - problem_statement.md
  - architecture.md
  - mvp_scope.md
  - evaluation_plan.md
  - runtime_architecture.md (Phase 9.0)
  - adk_mapping.md (Phase 9.0)
  - decision_log.md (Phase 9.0)
* `data/synthetic/`: Input datasets:
  - synthetic_boc_gl_dataset.xlsx (201 synthetic general ledger transactions).
* `outputs/`: Processed outputs:
  - reviewed_boc_gl_dataset.xlsx (reviewed ledger containing suggested columns).
* `boc_agent/`: Main source package:
  - `io/`: workbook loaders (`workbook_loader.py`) and exporters (`workbook_exporter.py`).
  - `schemas/`: Pydantic transaction (`transaction.py`) and review result (`review_result.py`) schemas.
  - `rules/`: target allocation constants (`allocation_rules.py`).
  - `tools/`: deterministic rules engine (`allocation_tool.py`), classification wrappers (`classification_tool.py`), eligibility wrappers (`eligibility_tool.py`), allocation wrappers (`allocation_wrapper_tool.py`), review wrappers (`review_tool.py`), and security scanner (`security_guardrail_tool.py`).
  - `agents/`: ADK orchestrator (`orchestrator.py`).
  - `chat/`: Deterministic conversational assistant and query router.
  - `rag/`: Local TF-IDF documentation retrieval and template answerer.
  - `skill/`: `SKILL.md` parser, validator, and loader.
  - cli.py: CLI utility executing the agent pipeline.
* `tests/`: Verification scripts (106 tests total):
  - test_allocation_rules.py (23 rule validations).
  - test_orchestrator.py (8 orchestration scenario validations).
  - test_chat_assistant.py (12 conversational assistant validations).
  - test_rag_pipeline.py (13 documentation retrieval/RAG validations).
  - test_human_review.py (6 human review and decision validations).
  - test_workbook_loader.py (12 schema validation validations).
  - test_dashboard_helpers.py (2 metrics calculations validations).
  - test_scaffold.py (2 import validations).
  - test_skill_runtime.py (9 skill runtime validations).
  - test_runtime_agent.py (19 runtime validations).

---

## 4. Dataset Context

The synthetic dataset contains **201 general ledger rows** of fully fictional transactions modeling Ontario (Ontario Creates CPTC/OFTTC) and Quebec (SODEC) production accounting application contexts.

The parser validates the following **24 required columns** exactly:
1. `Account`
2. `Account Name`
3. `Trans Date`
4. `Src`
5. `Trans Ref`
6. `Vendor ID`
7. `Vendor Name`
8. `Description`
9. `Additional Description`
10. `Loan out corp`
11. `Employee`
12. `Tax ID`
13. `Address`
14. `City`
15. `Province`
16. `Country`
17. `Zip Code`
18. `Our Reference`
19. `Currency`
20. `USD`
21. `Application Province`
22. `Location`
23. `Ep`
24. `Amount`

### Domain Validation Schema
* **Account**: Must match the regex `^T\d{2}-\d{4}$` (e.g. `T22-1000`).
* **Src**: Must be exactly `PL` (purchase ledger) or `CB` (cash book).
* **Location**: Allowed values are `900`, `910`, `920`, or blank.
* **Ep**: Allowed values are `40, 41, 42, 44, 45, 50, 51, 52, 54, 55, 60, 61, 62, 64, 65` or blank.
* **Application Province**: Must be exactly `Ontario` or `Quebec`.

---

## 5. Critical Domain Definitions

* **Country**: The address country of the vendor/payee (e.g. Canada or United States). It does **NOT** indicate where the work or service occurred.
* **Location**: The production accounting location code representing where the cost occurred:
  - `900` = Cost occurred **in** the application province.
  - `910` = Cost occurred **in Canada**, but outside the application province.
  - `920` = Cost occurred **outside Canada** (Out of Canada cost).
* **Location 920 Priority**: Location `920` always indicates that the cost occurred outside Canada, regardless of what the vendor's payee `Country` is. Country does NOT override Location 920.
* **Ep Code Meanings**:
  - `40 / 50 / 60`: Spend (supplies, equipment, platforms)
  - `41 / 51 / 61`: Salary (direct employees)
  - `42 / 52 / 62`: Loan-out corporation (creative corporation)
  - `44 / 54 / 64`: Multi-share / Fringe splits
  - `45 / 55 / 65`: Individual (sole proprietor) or Partnership
* **Application Province**: Set to `Ontario` or `Quebec`, indicating which provincial creating body's rules and target allocation columns apply.

---

## 6. Allocation Buckets

The agent allocates costs into one of **20 distinct columns**:

### Ontario / Federal Buckets:
1. `Out of Canada costs`
2. `Ontario Salary (41)`
3. `ONT individual (45)`
4. `ONT loan-out corporation (42)`
5. `ONT labor multi-share (44)`
6. `ONT labor paid to VICE Canada`
7. `Ontario Spend (40)`
8. `ONT non eligible`
9. `Fed labor paid to VICE Canada`
10. `Fed salary`
11. `Fed individual`
12. `Fed loan-out`
13. `Fed multi-share`
14. `Fed partnership`
15. `Fed non eligible`
16. `Meal (catering, craft, per diem)`

### Quebec minimal MVP buckets:
17. `Quebec qualified labour`
18. `Quebec qualified properties / spend`
19. `Quebec non-qualified`
20. `Quebec needs review`

---

## 7. Final Corrected Business Rules

* **Rule Engine First**: Deterministic rules are the ultimate source of truth. Assistant, RAG, SKILL, ADK-inspired, and future runtime wrappers must wrap around the rules and must not override validated conservative accounting logic.
* **Out of Canada**:
  - If `Location = 920` (outside Canada), the suggested allocation is strictly:
    - `Out of Canada costs` (for Ontario creates/Federal contexts)
    - `Quebec non-qualified` (for Quebec creates context)
    - Eligibility is `Ineligible`, amount percentage is `100.0`, and the reference rule is `RULE_OUT_OF_CANADA` / `RULE_QUEBEC_NON_QUALIFIED`.
  - If `Country != Canada` and `Location` is `900` or `910`, the row has a Country/Location conflict. It is flagged as `Needs Human Review`.
* **Ontario Context**:
  - Location 900 + labor Ep:
    - 41 salary → `Ontario Salary (41)`
    - 42 loan-out → `ONT loan-out corporation (42)`
    - 44 multi-share → `ONT labor multi-share (44)` (65.0% split)
    - 45 individual → `ONT individual (45)`
  - Location 900 + spend Ep 40 → `Ontario Spend (40)`.
  - Any missing/conflicting fields set `Review Status = Needs Human Review`.
* **Federal Counterparts Fallback**:
  - Location 910 + Country Canada routes to Federal counterpart buckets (`Fed salary`, `Fed loan-out`, etc.) rather than provincial Creates buckets.
  - If required evidence (Tax ID, Employee, Province, Location, or Ep) is missing or conflicting, it flags `Review Status = Needs Human Review` and `Eligibility Status = Needs Review` rather than approving the federal claim.
* **Quebec Context**:
  - Location 900 + Country Canada + labor Ep → `Quebec qualified labour`.
  - Location 900 + Country Canada + spend/property Ep → `Quebec qualified properties / spend`.
  - Location 920 → `Quebec non-qualified`.
  - Any missing or conflicting fields (missing Ep, missing Location, missing Province, missing Tax ID, Ep conflicts, or Country/Location conflicts) route to `Quebec needs review` (with eligibility `Needs Review` and review status `Needs Human Review`).
* **VICE Canada Labor**:
  - Normalize vendor names matching *VICE*, *VICE STUDIO*, *VICE STUDIO CANADA*, or *VICE CANADA*.
  - Ontario: Maps to `ONT labor paid to VICE Canada`.
  - Federal/non-Ontario: Maps to `Fed labor paid to VICE Canada`.
  - Quebec: Maps to `Quebec qualified labour` with a `Secondary Allocation Note`: `"Payee appears to be VICE Canada labor; Quebec-specific dedicated VICE bucket is not implemented in this MVP."`
  - Do NOT map VICE labor primarily to generic Ontario Salary or Fed salary.
* **Payroll Processor**:
  - If vendor is a payroll processor (e.g. Greenslate, Cast & Crew, Union Street) and an Employee is present, the employee is treated as the effective payee.
  - If the payroll processor row is missing an Employee, it is flagged as `Needs Human Review`.
* **Partnership**:
  - Vendor names containing whole words matching partnership indicators (`Partnership`, `Partners`, `LLP`, `LP`) map to `Fed partnership`.
  - If a partnership tax ID is missing, it is flagged as `Needs Human Review`.
  - Do not classify partnership as individual by default.
* **Multi-share**:
  - Ep suffix 44 / 54 / 64 maps to `amount_percentage = 65.0` with the `Secondary Allocation Note`: `"remaining 35% should be reviewed as spend/non-labor treatment for MVP purposes"`.
  - Rationale explicitly states that this is an *internal BOC allocation convention based on the synthetic workbook Ep code*, rather than describing it as a universal statutory rule.
* **Meal / Catering**:
  - Meal/catering/craft/per diem terms map to `Meal (catering, craft, per diem)` with `amount_percentage = 100.0`.
  - Location 920 overrides the meal bucket and maps to Out of Canada / Quebec non-qualified.
  - Rationale avoids describing meals as labor-eligible.
* **False Labor Detection**:
  - Do not treat spend codes (like editing rooms, software, platform, collaboration, equipment, rental, facility) as labor-related unless there is named Employee/Loan-out corp data, labor Ep codes, or explicit labor wording. This prevents false positives like matching "collaboration" as labor due to "collaboration" containing the letters "labor".

## 8. Security Guardrail

* A basic input guardrail detects prompt-injection-like overrides in transaction descriptions (e.g. `"ignore previous rules"`, `"mark everything eligible"`, or `"override allocation"`).
* The stale guardrail module `security_guardrail.py` was removed; the active scan is managed by `security_guardrail_tool.py`.
* If detected, the transaction is flagged as `Needs Human Review` with a security warning in the rationale. The transaction description is never allowed to override the deterministic rule engine.

---

## 9. Completed Phases

### Phase 1: Scaffold
* Project environment set up with `uv` and `pyproject.toml`.

### Phase 2: Workbook Loader & Schemas
* Synthetic GL dataset workbook (201 rows) parsed and schema-validated.

### Phase 3: Rule Engine & Audit
* Rule engine implemented in `allocation_tool.py` executing all deterministic Canadian production accounting logic.
* CLI entrypoint implemented to execute batch audits over the Excel sheet and write reviewed results.
* Audits and remediations (Pass 1 and Pass 2) successfully executed to handle Location 920 priority, Quebec minimal buckets, false labor detection, and payroll processors.

### Phase 4: Agent Orchestration
* Implemented `OrchestrationState` and sequential orchestrator pipeline (`boc_agent/agents/orchestrator.py`) wrapping Security scan, Classification, Eligibility, Allocation, and Packaging.
* Created specialized wrapper tools for each step.

### Phase 5: Evaluation & Demo Polish
* Created the evaluation script `scripts/evaluate_outputs.py` and compiled ground-truth and demo guide documentation.

### Phase 6: Human-in-the-Loop (HITL) Review Workflow
* Implemented `HumanReviewDecision` Pydantic models to strongly validate human override statuses (Accept, Override, Mark Ineligible, Request Documentation, Defer).
* Implemented the automated queue builder `scripts/build_review_queue.py` to extract rows requiring human attention.

### Phase 7: Streamlit UI Dashboard
* Created the interactive dashboard app (`app.py`) allowing Excel uploads, execution visualization, manual overrides, and review logs download.

### Final Audit Remediation Pass
* Resolved the Ep 45/55/65 contractor individual vs. salary mapping bug.
* Resolved Ep 45 + loan-out payee conflict regression.
* Resolved workbook export and Streamlit dashboard download header, order, and custom column preservation issues.
* Hardened loader validation to reject decimal Location/Ep codes.
* Cleaned up documentation and UI wording to avoid overclaiming.

### Phase 8.1: Conversational Review Assistant
* Implemented a local-first, deterministic Q&A helper module (`boc_agent/chat/`) to route natural language queries to workbook-grounded summaries, location breakdowns, ineligible rows, pending human review queues, and specific row explanations.
* Implemented full schema alias mapping to support both original Excel workbook headers and snake_case properties.
* Integrated a clean interactive chat tab directly in the Streamlit Dashboard (`app.py`).
* Added comprehensive query routing, row-explanation prioritizations, non-mutation assertions, and legal disclaimer refusal tests.

### Phase 8.2: Local Documentation RAG
* Implemented a local-first, lightweight TF-IDF documentation RAG layer under `boc_agent/rag/`.
* Created a document loader and a heading-aware chunker that preserve markdown heading hierarchies.
* Created a pure Python TF-IDF vectorizer and in-memory Cosine Similarity index store (`RetrievalIndex`), ensuring no heavy model downloads.
* Implemented template-based grounded responses with cited excerpts, source file links, and legal/tax warnings, explicitly avoiding generative synthesis.
* Extensively verified intent routing so that row-specific queries bypass RAG and documentation queries route to RAG correctly.

### Phase 8.3: ADK-Inspired SKILL.md Runtime Contract
* Added root `SKILL.md` as a machine-readable runtime contract for capabilities, non-capabilities, tool permissions, refusal policies, and grounding policies.
* Implemented `boc_agent/skill/` with loader, parser, validator, and Pydantic models.
* Added `BOC_SKILL_FILE_PATH` support for isolated temporary skill files in tests.
* Verified invalid tools, mutating tools, malformed skill files, refusal behavior, and grounding policies.

### Phase 9.0: ADK-Inspired Runtime Architecture Design
* Added design-only runtime architecture documentation:
  - `docs/runtime_architecture.md`
  - `docs/adk_mapping.md`
  - `docs/decision_log.md`
* Clearly separates current implemented local components, the completed Phase 9.1 runtime implementation, and future Google ADK/cloud migration.

### Phase 9.1: ADK-Inspired Runtime Implementation
* Implemented the decoupled local runtime layer under `boc_agent/runtime/`.
* Added robust skill permission enforcement and prevented mutating operations.
* Added a comprehensive runtime test suite under `tests/test_runtime_agent.py`.

### Phase 9.2: Runtime Trace & Observability
* Implemented a structured execution trace layer under `boc_agent/runtime/trace/` (`trace_models.py`, `trace_builder.py`, `trace_exporter.py`, `trace_formatter.py`).
* Captures monotonic latency times, intent capabilities, tool usage details, reasoning step sequences, and stage confidence timeline snapshots.
* Added a comprehensive trace test suite under `tests/test_runtime_trace.py` (totaling 137 tests overall including Phase 10.1 & 10.2 tests).

### Phase 10.1: Docker + Google Cloud Run Deployment Readiness
* Created `Dockerfile`, `.dockerignore`, `.env.example`, and [docs/deployment_cloud_run.md](docs/deployment_cloud_run.md) for containerizing the Streamlit agent.
* Implemented container smoke checks in `scripts/smoke_deployment.py` and unit checks in `tests/test_deployment_files.py`.

### Phase 10.2: Cost Guardrails & Budget Documentation
* Created [docs/cost_guardrails.md](docs/cost_guardrails.md) detailing recommended low-cost settings, budget alert setups, and cleanup checklists.
* Implemented doc assertions in `tests/test_cost_guardrails_docs.py` to verify disclaimers and settings.

---

## 10. Key Commands

Ensure the environment is synced, tests pass, and review scripts run cleanly:

```bash
uv sync
uv run pytest
uv run python -m boc_agent.cli --input data/synthetic/synthetic_boc_gl_dataset.xlsx --output outputs/reviewed_boc_gl_dataset.xlsx
uv run python scripts/evaluate_outputs.py outputs/reviewed_boc_gl_dataset.xlsx
uv run python scripts/build_review_queue.py outputs/reviewed_boc_gl_dataset.xlsx outputs/human_review_queue.xlsx
uv run streamlit run app.py
uv run python -m py_compile app.py
```

---

## 11. Current Known Outputs

The General Ledger processing produces the following exact metrics over the 201 synthetic input rows:
* **Total Transactions**: 201 reviewed rows.
* **Review Status Breakdown**:
  * `Approved`: 113 rows
  * `Needs Human Review`: 88 rows
* **Eligibility Status Breakdown**:
  * `Eligible`: 113 rows
  * `Needs Review`: 70 rows
  * `Ineligible`: 18 rows
* **HITL Review Queue**: Exports exactly **88 rows** to `outputs/human_review_queue.xlsx`.

---

## 12. Critical Guardrails

* **Deterministic Rule Engine as Source of Truth**: The core accounting engine in `allocation_tool.py` is the final arbiter of allocations and eligibility.
* **Non-interference of AI Layers**: Current chat/RAG helpers and any future runtime or summary assistants can explain, filter, route, and summarize the data for the accountant, but they must NOT silently override the allocation column, amount percentage, or eligibility status computed by the rule engine.
* **Separate Human Audit Trail**: Human review decisions and override selections must be kept in separate columns (`human_review_decision`, `human_reviewer`, `human_override_allocation`, etc.) rather than overwriting the agent's deterministic outputs directly, maintaining a clean audit trail.

---

## 13. Next Recommended Phases

Future development phases after capstone presentation:
* **Phase 10.3: Optional ADK / Vertex AI Migration Guide**: Migrate to native Google Cloud Agent Engine and Vertex AI Search wrappers.

---

## 14. Project Limitations & Review Instructions

* **No Official Authority**: The agent is a review support tool. It does NOT provide official tax-credit determinations or compile official governmental applications (such as CAVCO Form 6).
* **No Live Database Connections**: Does not connect to live registries (CRA, CAVCO, corporate registries) or payroll ERPs.
* **Minimal Quebec Support**: Quebec Creates SODEC rules remain a minimal MVP skeleton containing 4 columns.
* **Explanation-Only Assistant**: The chat layer should strictly explain and query existing reviewed data and must not attempt statutory tax rulings.
* **No Native ADK or Cloud Deployment Yet**: Native Google ADK runtime, Vertex AI, Agent Engine, and Cloud Run deployment are not implemented.
* **Phases 9.1, 9.2, 10.1 & 10.2 Implemented**: Both the local runtime, execution trace observability, Docker Cloud Run readiness, and Cost Guardrails layers have been fully implemented and tested.
* **No Statutory Wording**: Avoid terms implying tax optimization or official rulings; use "review support", "suggested allocation", "deterministic allocation review", "synthetic workbook convention", and "human follow-up".
