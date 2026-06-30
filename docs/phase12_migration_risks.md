# Native Google ADK Migration Risk Register

This document outlines the risk factors, severity levels, mitigation strategies, and verification controls associated with migrating to a native Google ADK / Vertex AI Agent Engine runtime.

> [!IMPORTANT]
> **Current Status & Disclaimer**:
> * **Not Implemented**: This document is a design and feasibility risk blueprint only. The native ADK integration is not implemented, and Vertex AI / Gemini / Agent Engine services are not deployed.
> * **allocation_tool.py**: Remains unchanged and untouched.
> * **No Gemini Decision Power**: Gemini must not make final allocation or eligibility decisions.

---

## 1. Core Risk Matrix

| Risk ID | Risk Description | Severity | Mitigation Strategy | Test / Control |
| :--- | :--- | :--- | :--- | :--- |
| **R-01** | **LLM Hallucination in Allocation Decisions**: LLM makes accounting eligibility determinations, overriding rules. | **Critical** | Do not let LLM make decisions. Rules in `allocation_tool.py` remain the final source of truth. | Assertion test verifying LLM output matches rules-only outputs. |
| **R-02** | **Prompt Injection via RAG**: Unsanitized search text or reference manuals inject system instructions. | **High** | Sanitize all RAG query parameters. Use strict system prompt framing. | Injection vulnerability test suites passing malicious payloads. |
| **R-03** | **Cloud Billing Surprises**: Recursive loops in ADK agent calling tools repeatedly. | **High** | Set execution step limiters (e.g., max 5 steps). Configure GCP budget alerts. | Step-limit unit tests asserting error on exceeding max steps. |
| **R-04** | **Overly Broad Service Account Permissions**: Managed agent deployment using default computer credentials. | **High** | Prefer least-privilege, user-specified service accounts. Restrict roles to minimum needed. | IAM policy scanner checks. |
| **R-05** | **Loss of Deterministic Auditability**: Non-deterministic LLM response makes explaining choices difficult. | **High** | Log static rule IDs and parameters for every reviewed row. | Schema validator asserting rule ID presence in all output traces. |
| **R-06** | **Tool Mutation Risk**: ADK agent attempts to modify transaction values or database tables. | **High** | Force all tools exposed to ADK to be read-only. | Write-prevention integration tests. |
| **R-07** | **Session State Leakage**: Multi-user session state cached or shared in managed memory. | **Medium** | Sanitize memory contexts and clear session state after review runs. | Multi-session boundary tests. |
| **R-08** | **Trace Sensitive Data Leakage**: Transaction data or names included in trace payloads. | **Medium** | Redact synthetic-sensitive data fields before exporting traces. | Redaction regex test on trace exports. |
| **R-09** | **Deployment Complexity**: Dependency conflicts with native Google Cloud ADK packages. | **Medium** | Isolate ADK dependencies inside a separate bridge package or module. | Container build tests. |
| **R-10** | **Vendor Lock-in**: Hard dependency on Vertex AI Agent Engine. | **Medium** | Maintain the local ADK-inspired runtime as the primary engine. | Offline execution tests with network disabled. |
| **R-11** | **Broken Local-First Workflow**: CLI fails to run locally without internet/GCP access. | **Medium** | Keep offline execution path active in the local executor code. | Offline CLI dry run tests. |

---

## 2. Identity and Access Management (IAM) Guidance
Managed agent platforms require careful identity and access management. When deploying the ADK wrapper or native agents to GCP:
* **User-Specified Service Accounts**: Do not use the default Compute Engine service account. Create a custom service account (e.g. `boc-reviewer-sa@PROJECT.iam.gserviceaccount.com`).
* **Role Restrictor**: Grant only `roles/logging.logWriter`, `roles/cloudtrace.agent`, and `roles/aiplatform.user`.
* **No Secret Commits**: All credentials must be loaded at runtime via environment variables (e.g., loaded via `.env` file or GCP Secret Manager).
