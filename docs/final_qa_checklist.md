# Final QA Checklist

Use this checklist to perform the final Quality Assurance check before publishing the repository.

---

## 💻 Required Verification Commands
Run the following commands in sequence in your project root environment:
```bash
# 1. Run the full unit and integration test harness
uv run pytest

# 2. Run the local container-ready smoke deployment check
uv run python scripts/smoke_deployment.py

# 3. Compile the Streamlit dashboard code for syntax correctness
uv run python -m py_compile app.py

# 4. Process the synthetic General Ledger workbook through the batch CLI
uv run python -m boc_agent.cli --input data/synthetic/synthetic_boc_gl_dataset.xlsx --output outputs/reviewed_boc_gl_dataset.xlsx

# 5. Evaluate classification accuracy and status metrics
uv run python scripts/evaluate_outputs.py outputs/reviewed_boc_gl_dataset.xlsx

# 6. Generate the Human-in-the-Loop review queue spreadsheet
uv run python scripts/build_review_queue.py outputs/reviewed_boc_gl_dataset.xlsx outputs/human_review_queue.xlsx

# 7. Assert that the core deterministic rules remained unchanged
git diff boc_agent/tools/allocation_tool.py

# 8. Verify codebase formatting hygiene (e.g. no trailing whitespaces)
git diff --check
```

---

## 📈 Expected Verification Results
- [ ] **Test suite passes**: All 307 unit and integration tests must pass cleanly.
- [ ] **Smoke script passes**: Output must show `[SUCCESS] Smoke Deployment Checks Passed`.
- [ ] **Streamlit app compiles**: Command must exit with code `0` and no compilation errors.
- [ ] **CLI workbook processing**: Processes all **201 synthetic transaction rows** and writes a reviewed Excel sheet successfully.
- [ ] **Evaluation metrics**:
  - `Approved`: **113 rows**
  - `Needs Human Review`: **88 rows**
- [ ] **HITL review queue**: Builds an Excel file with exactly **88 rows** corresponding to the flagged transactions.
- [ ] **Rule integrity check**: `git diff boc_agent/tools/allocation_tool.py` must return an empty diff (confirming core rule logic remains the final source of truth).
- [ ] **Git formatting hygiene**: `git diff --check` must be clean, with no formatting warnings.

---

## 🔍 Manual Code and Asset Audit
- [ ] **No Secrets**: Confirm that `.env` is ignored and no passwords, billing accounts, API keys, or private tokens exist in any files.
- [ ] **No Local/Absolute Paths**: Check that no directory structures for local drive paths or POSIX home folders are committed in docs or tests.
- [ ] **No Real Financial Data**: Confirm that only fully synthetic data transactions (e.g., Canadian film/TV ledger rows) are included.
- [ ] **No Fake Screen Captures**: Verify that no placeholder markdown links claim screenshots or videos exist unless the files have actually been recorded and committed.
- [ ] **No Overclaims**: Ensure all docs state the agent is an administrative review co-pilot using deterministic conventions and a local TF-IDF RAG, not a legal tax compliance authority, nor a native Google ADK/Vertex/Gemini deployment.
- [ ] **Valid Links**: Click and check that all relative markdown files and line anchors reference valid files.
- [ ] **Release Tag**: Confirm you are ready to tag and release `v2.0.0-portfolio`.
