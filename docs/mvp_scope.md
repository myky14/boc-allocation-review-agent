# Project Scope: In-Scope vs. Out-of-Scope (MVP)

To ensure this capstone project is completed within a two-week timeframe as a focused MVP, the boundaries of the **BOC Allocation Review Agent** are defined below.

---

## 1. In Scope

The MVP will focus on the core reasoning, classification, mapping logic, and output formatting:

* **Workbook Ingestion & Normalization**:
  - Direct processing of a synthetic, cleaned/enriched General Ledger (GL) workbook in Excel or CSV format.
  - Normalization of fictional production accounting headers (Application Province, Location, Ep code, vendor/payee structure, employee/loan-out data, tax ID placeholders, address fields, currency, and transaction descriptions).
* **Security & Guardrail Middleware**:
  - Scanning transaction descriptions for prompt-injection-like overrides.
  - Redaction of sensitive PII-like placeholders (e.g. SIN-like patterns) in description and payee name fields.
* **Specialist Tool execution (Classification & Mapping)**:
  - Applying rule-based and AI-assisted classification models to suggest the target allocation.
  - Mapping transactions to the 20 target allocation columns (supporting Ontario, Federal, and minimal Quebec columns).
  - Defining Location as the production cost location code (900 = application province, 910 = Canada outside application province, 920 = outside Canada / Out of Canada cost) and Country as payee/vendor address country. Location 920 always means out-of-Canada cost regardless of vendor Country.
  - Calculating amount percentages (e.g., meals mapped to 100% of the meal bucket, direct labor to 100%, multi-share labor splits like 65%).
* **Compliance Suggestion Outputs**:
  - Adding the agent-generated review fields to the BOC allocation review workbook (not an official filing):
    * Suggested Allocation Column
    * Amount Percentage
    * Eligibility Status
    * Confidence Score
    * Review Status
    * Reasoning
    * Reference Rule
    * Secondary Allocation Note
* **Workbook-based Human-in-the-Loop representation**:
  - Automatically setting `Review Status = Needs Human Review` directly in the output file if required fields are missing/conflicting (e.g., missing address, location, Ep code, or tax ID), if confidence is below 85%, or if a transaction belongs to a special review category.
* **Local Evaluation Harness**:
  - Compiling accuracy results against a manually labeled subset of the synthetic transactions.

---

## 2. Out of Scope

The following features are excluded from the MVP:

* **ERP and Live System Integrations**:
  - No direct connections or webhook synchronization with live production accounting databases (e.g. PSL, Ease, Cast & Crew).
* **Document Parsing (OCR)**:
  - No scanning of paper invoices, receipts, or PDF contracts. The input is assumed to be a pre-digitized workbook.
* **Government Database Lookups**:
  - No connections to real government databases (citizenship, permanent residency, corporate registries, or municipal address databases) and no validation of real tax IDs or official RC64/RC65 forms.
* **Official Tax Form Generation**:
  - Direct compilation of the final CAVCO Form 6 PDF is omitted. Form 6 generation is completely out of scope. The output is an internal BOC allocation review workbook, not an official CAVCO filing output.
* **Complex Web Dashboard**:
  - No multi-tenant web dashboard. The human review is handled directly by filtering the exported reviewed CSV/Excel workbook.
* **Live Cloud Deployment**:
  - Managed Cloud Run or live Vertex AI platform deployments are optional stretch features. The core MVP runs as a local python workflow.

---

## 3. Rationale for MVP Scope

This scope is tailored to deliver a credible solo capstone project:

1. **Academic & Portfolio Focus**:
   By avoiding heavy software engineering integrations (DB hosting, OAuth, multi-tenant UI), 100% of the focus goes into designing robust agent reasoning structures, tool execution, and local validation.
2. **Realistic 2-Week Development Cycle**:
   By assuming the ledger workbook is already digitized and cleaned/enriched with fictional metadata, we avoid the high error rates and time commitments of OCR and external API integrations.
3. **Immediate Workflow Utility**:
   In production accounting offices, Excel and CSV formats are the standard communication files. An agent that outputs an annotated ledger with reasons, suggestion percentages, and flagged review statuses provides immediate assistance without changing the accountant's software environment.
