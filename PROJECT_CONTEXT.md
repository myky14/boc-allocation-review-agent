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
* **Architecture Style**: Local-first, rule-engine-first MVP. AI/ADK orchestration wraps around the core deterministic rule engine. The deterministic rules are the final source of truth.

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
  - cli.py: CLI utility executing the agent pipeline.
* `tests/`: Verification scripts:
  - test_allocation_rules.py (30 pass validations).
  - test_orchestrator.py (7 orchestration scenario validations).
  - test_scaffold.py (scaffold imports testing).
  - test_workbook_loader.py (schema validation testing).

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

* **Rule Engine First**: Deterministic rules are the ultimate source of truth. LLM/ADK wrappers must wrap around the rules and must not override validated conservative accounting logic.
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

---

## 8. Security Guardrail

* A basic input guardrail detects prompt-injection-like overrides in transaction descriptions (e.g. `"ignore previous rules"`, `"mark everything eligible"`, or `"override allocation"`).
* If detected, the transaction is flagged as `Needs Human Review` with a security warning in the rationale. The transaction description is never allowed to override the deterministic rule engine.

---

## 9. Completed Phases

### Phase 1: Scaffold
* Project environment set up with `uv` and `pyproject.toml`.
* Standard package structure created (`boc_agent/io`, `boc_agent/schemas`, `boc_agent/rules`, `boc_agent/tools`, `boc_agent/agents`, `tests`).
* Placeholder modules created and scaffold import tests passing.

### Phase 2: Workbook Loader & Schemas
* Synthetic GL dataset workbook (201 rows) copied into `data/synthetic/`.
* `workbook_loader.py` implemented to parse files and validate the schema row-by-row against domain validation rules (Account regex, Src CB/PL, Ep codes, Locations, and Application Provinces).
* Pydantic schemas implemented in `transaction.py` and `review_result.py` with alias mappings.

### Phase 3: Rule Engine & Audit
* Rule engine implemented in `allocation_tool.py` executing all deterministic Canadian production accounting logic.
* CLI entrypoint implemented to execute batch audits over the Excel sheet and write reviewed results.
* Audits and remediations (Pass 1 and Pass 2) successfully executed to handle Location 920 priority, Quebec minimal buckets, false labor detection, and payroll processors.
* **pytest status**: 38 tests collect and pass successfully (30 rules tests + 8 orchestrator tests).

---

## 10. Key Commands

```bash
# Synchronize environment
uv sync

# Run all test suites (38 tests)
uv run pytest

# Execute rule engine over the synthetic ledger and export reviewed output
uv run python -m boc_agent.cli --input data/synthetic/synthetic_boc_gl_dataset.xlsx --output outputs/reviewed_boc_gl_dataset.xlsx
```

---

## 11. Current Known Outputs

The processed sheet `outputs/reviewed_boc_gl_dataset.xlsx` has the following validated example outputs:
* **Row 1**: Quebec qualified labour (Approved, 100.0% claim).
* **Row 2**: Quebec qualified labour (Approved, 100.0% claim).
* **Row 3**: Out of Canada costs (Needs Human Review, United States vendor).
* **Row 4**: Ontario Salary (41) (Approved, Union Street payroll row using Employee Nina Chen as effective payee).
* **Row 5**: Quebec non-qualified (Needs Human Review, United States vendor at Location 920).
* **Row 6**: Quebec qualified properties / spend (Approved, 100.0% claim).
* **Row 7**: Quebec qualified labour (Approved, Union Street payroll row using Employee Noah Walsh as effective payee).
* **Row 8**: Out of Canada costs (Needs Human Review, United Kingdom vendor).
* **Row 9**: Fed salary (Needs Human Review, Ontario application but payee province is Quebec).
* **Row 10**: Quebec qualified properties / spend (Approved, 100.0% claim).

---

## 12. Completed Phase 4 & Phase 5: Agent Orchestration & Presentation Readiness

Phases 4 and 5 implemented a structured, ADK-style agent orchestration pipeline over the deterministic rule engine and polished the project for capstone presentation.

### Key Components Implemented:
1. **Orchestration State**: A dataclass tracking transaction context, security warnings, classification metadata, and step-by-step execution traces.
2. **Orchestrator Agent** (`boc_agent/agents/orchestrator.py`): Manages the sequential review execution flow:
   - **Step 1: Security Guardrail Check** (`boc_agent/tools/security_guardrail_tool.py`) detects prompt-injection keyword overrides.
   - **Step 2: Transaction Classification** (`boc_agent/tools/classification_tool.py`) extracts payee and location metadata.
   - **Step 3: Eligibility Assessment** (`boc_agent/tools/eligibility_tool.py`) evaluates regional eligibility.
   - **Step 4: Allocation Suggestion** (`boc_agent/tools/allocation_wrapper_tool.py`) delegates to the deterministic rule engine.
   - **Step 5: Final Review Packaging** (`boc_agent/tools/review_tool.py`) combines outputs, overriding review status and rationale if security warning overrides are flagged.
3. **CLI Integration**: CLI call routes transactions through the Orchestrator seamlessly (backward compatible).
4. **Validation Test Suite**: 8 orchestration scenario tests in `tests/test_orchestrator.py` validating return types, mappings, priorities, security overrides, and batch processing.
5. **Evaluation Script** (`scripts/evaluate_outputs.py`): Calculates and prints workbook stats, status counts, allocation distribution, and highlights.
6. **Demo Guide** (`docs/demo_cases.md`): Documents 10 representative scenarios for capstone presentation.

---

## 13. Next Recommended Phase

Now that Phase 5 is completed, the project is submission-ready. Future recommended integration or expansion phases include:
1. **Stateful Human-in-the-Loop Interruption**: Incorporate Vertex AI session service and `RequestInput` stateful interrupts to allow accountants to resolve "Needs Human Review" warnings directly from the CLI or dashboard.
2. **Expansion to Other Provinces**: Add specialist modules for British Columbia Creates (FIBC) guidelines.
3. **Form 6 Template Export**: Map audited allocation columns directly to the CAVCO Schedule of Production Costs structure.

---

## 14. Important Review Instruction

Any future assistant or Antigravity session must treat Canadian production accounting logic carefully.
* If a transaction is ambiguous or lacks supporting documentation, **Do NOT guess**.
* Mark the row as `Review Status = Needs Human Review` and lower the `confidence_score` to `0.70`.
* In Quebec context, if a row fails checks, map to the dedicated `Quebec needs review` bucket.
* In case of doubt, pause and ask the user for clarification. Do not overclaim eligibility.

Last updated after Phase 5 Presentation Readiness completion. Project is fully submission-ready.
