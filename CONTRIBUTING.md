# Contributing Guidelines

Thank you for your interest in contributing to the `boc-allocation-review-agent` project! This document outlines the setup, testing, formatting, and submission procedures.

---

## ⚠️ Critical Rule: allocation_tool.py Freeze
- **No changes to `boc_agent/tools/allocation_tool.py` or its wrapped rules are permitted without an official rule review.**
- This file contains the deterministic, verified source of truth for the tax-credit logic. To prevent regression, any proposed modifications must go through a formal policy and regression test review.

---

## 🛠️ Local Development Setup

We use `uv` for lightning-fast Python package and workspace management.

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/boc-allocation-review-agent.git
cd boc-allocation-review-agent

# 2. Sync virtual environment and install dependencies
uv sync
```

---

## 🎨 Code Style & Formatting
- **Linter & Formatter**: We use `ruff` to enforce styling and lint rules.
- Run formatting and check lint rules before committing:
  ```bash
  uv run ruff format
  uv run ruff check --fix
  ```
- **Git Hygiene**: Always run `git diff --check` to verify no trailing whitespaces or formatting warnings are introduced.

---

## 🧪 Testing Guidelines

We enforce a comprehensive automated regression suite. All tests must pass before submitting a Pull Request.

- Run the full test suite (including the RAG and release validations):
  ```bash
  uv run pytest
  ```
- Run the local smoke deployment check:
  ```bash
  uv run python scripts/smoke_deployment.py
  ```
- Ensure `app.py` compiles cleanly without warnings:
  ```bash
  uv run python -m py_compile app.py
  ```

---

## 📝 Commit Style

We follow the standard [Conventional Commits](https://www.conventionalcommits.org/) specification:
- `feat:` A new feature or tool registration.
- `fix:` A bug fix or syntax correction.
- `docs:` Documentation improvements or case study updates.
- `test:` Adding or refactoring tests.
- `refactor:` Code refactoring with no behavior changes.

---

## 📋 Pull Request Checklist
Before submitting a PR, verify:
- [ ] All unit, integration, and validation tests pass (`uv run pytest`).
- [ ] Smoke deployment check completes (`uv run python scripts/smoke_deployment.py`).
- [ ] Streamlit interface compiles successfully (`uv run python -m py_compile app.py`).
- [ ] No changes have been made to `boc_agent/tools/allocation_tool.py` without rule review.
- [ ] Relative markdown links are validated and resolve correctly.
- [ ] No local/absolute drive paths (e.g. C-drive or POSIX home folders) or credentials are present.
- [ ] No false deployment claims (e.g., claiming live Google Cloud Run hosting, Vertex AI agent engine deployments, or active Gemini API keys) are committed.
