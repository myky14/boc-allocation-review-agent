## Description
Briefly describe the changes made in this Pull Request.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Documentation update (non-breaking change to docs)
- [ ] Refactoring (no functional changes)

## Checklist
Please verify the following:
- [ ] All unit, integration, and validation tests pass successfully (`uv run pytest`).
- [ ] Local smoke deployment checks complete (`uv run python scripts/smoke_deployment.py`).
- [ ] The Streamlit dashboard compiles and runs without warnings (`uv run python -m py_compile app.py`).
- [ ] Core business rule logic in `boc_agent/tools/allocation_tool.py` remains completely unchanged (or has gone through formal rule review).
- [ ] Relative markdown links are validated and resolve correctly, and no `file:///` references are present.
- [ ] No hardcoded API keys, passwords, or credentials are committed.
- [ ] No false claims regarding live Cloud Run hosting, native ADK execution, or Gemini/Vertex AI cloud deployments are present in any modified documentation.
