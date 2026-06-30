# Phase 12.1 POC Checklist

Use this checklist during the Phase 12.1 Native ADK Wrapper Proof of Concept (POC) to ensure safety boundaries and rule freezes are maintained.

> [!IMPORTANT]
> **Current Status & Disclaimer**:
> * **Not Implemented**: This document is a design and feasibility checklist only. The native ADK integration is not implemented, and Vertex AI / Gemini / Agent Engine services are not deployed.
> * **allocation_tool.py**: Remains unchanged and untouched.

---

## 1. Safety & Compliance Controls
- [ ] **No `allocation_tool.py` Mutation**: Run `git diff boc_agent/tools/allocation_tool.py` and verify the output is completely empty.
- [ ] **No Gemini Decision Power**: Gemini must not make final allocation or eligibility decisions, and the wrapper does not delegate these tasks.
- [ ] **No Secrets Committed**: Scan files to ensure no GCP credentials, API keys, or private service accounts are checked in.
- [ ] **Offline Execution**: Run tests with network connectivity disabled to ensure local fallback functions correctly.

---

## 2. Parity & Validation Checks
- [ ] **Local Parity tests**: Run the wrapper against the standard test inputs and confirm the outputs match the current local runtime exactly.
- [ ] **Existing Harness Integrity**: Verify that all **307** existing unit and integration tests continue to pass.
- [ ] **Isolated POC Tests**: Keep all POC-specific tests isolated under `tests/test_adk_poc.py` to prevent regression side effects.

---

## 3. Rollback Protocol
- [ ] **Clean Git Workspace**: Ensure all changes are committed before starting the POC.
- [ ] **Rollback Command**: Run `git checkout -- .` and delete the `experiments/adk_poc/` directory to completely discard the POC.
