# Release Checklist

This checklist must be executed and verified before tagging and releasing version `v2.0.0-portfolio` of the **BOC Allocation Review Agent**.

*Note: This release checklist is for the portfolio version of the review support assistant, which does not provide official tax or legal determinations.*

---

## 1. Local Testing & Compilation
- [ ] **All tests pass**: Run the pytest suite and ensure all tests are green:
  ```bash
  uv run pytest
  ```
- [ ] **app.py compiles**: Verify that the Streamlit application compiles without errors:
  ```bash
  uv run python -m py_compile app.py
  ```
- [ ] **Smoke deployment check passes**: Verify that the local deployment smoke test runs and logs success:
  ```bash
  uv run python scripts/smoke_deployment.py
  ```

---

## 2. CLI & Pipeline Processing Verification
- [ ] **CLI workbook processing**: Process the synthetic ledger and verify that exactly 201 rows are processed:
  ```bash
  uv run python -m boc_agent.cli --input data/synthetic/synthetic_boc_gl_dataset.xlsx --output outputs/reviewed_boc_gl_dataset.xlsx
  ```
- [ ] **Evaluation script execution**: Run the evaluation output analyzer on the reviewed file:
  ```bash
  uv run python scripts/evaluate_outputs.py outputs/reviewed_boc_gl_dataset.xlsx
  ```
- [ ] **HITL Queue Export**: Generate the human-in-the-loop review queue workbook and verify that exactly 88 rows are exported:
  ```bash
  uv run python scripts/build_review_queue.py outputs/reviewed_boc_gl_dataset.xlsx outputs/human_review_queue.xlsx
  ```

---

## 3. Core Protection & Security Audits
- [ ] **Core rule engine unchanged**: Verify that `allocation_tool.py` has no uncommitted modifications (its git diff must be completely empty):
  ```bash
  git diff boc_agent/tools/allocation_tool.py
  ```
- [ ] **No hardcoded secrets**: Check deployment templates for obvious hardcoded secrets. Review repository manually before release for secrets. Use git-secrets/trufflehog or equivalent separately if needed.
- [ ] **No local absolute paths**: Verify that no machine-specific absolute file structures (e.g. `/absolute/path/to/project`) exist in documentation or configuration settings (verified via `tests/test_deployment_files.py`).
- [ ] **Git diff check clean**: Verify that there are no trailing whitespace errors or formatting issues:
  ```bash
  git diff --check
  ```

---

## 4. Documentation & Repository Polish
- [ ] **README up-to-date**: Confirm that `README.md` correctly reflects the 145-test pass count and links to all new guides.
- [ ] **Project Context up-to-date**: Confirm that `PROJECT_CONTEXT.md` lists Phase 11.1 as completed.
- [ ] **Links validated**: Click and verify all markdown relative files and line anchors link to valid files.

---

## 5. Release Tagging
- [ ] Prepare git release tag:
  ```bash
  git tag -a v2.0.0-portfolio -m "Release v2.0.0-portfolio for capstone presentation"
  ```
