# Portfolio Publishing Checklist

Use this checklist to ensure a professional, secure, and accurate public release of the `boc-allocation-review-agent` repository.

---

## 📋 1. Repository Safety & Content Checks
- [ ] **Secrets & Credentials**: Verify that no API keys, private tokens, passwords, or active credentials are committed (check `.env` is ignored).
- [ ] **No Real Financial Data**: Confirm that only the synthetic datasets under `data/synthetic/` are checked in.
- [ ] **No Local/Absolute Paths**: Assert that no local path structures or POSIX home directory paths are present in documentation or tests.
- [ ] **No Fake Screen Captures**: Verify that no placeholder markdown links claim screenshots or videos exist unless the files have actually been recorded and committed.
- [ ] **Truthful Boundaries**: Confirm the README and case studies use precise, safe terms:
  - *"ADK-inspired runtime"*, not native Google ADK.
  - *"Cloud Run deployment readiness"*, not official cloud deployment.
  - *"Offline-first review assistant"*, not official tax legal determination.
  - *"Deterministic rule engine and template-based local RAG"*, not live LLM prompts.
- [ ] **Logic Integrity**: Verify that `boc_agent/tools/allocation_tool.py` has not been modified.
- [ ] **Harness Passing**: Confirm all 307 unit and integration tests pass locally.

---

## 🏷️ 2. GitHub Setup Recommendations
- [ ] **Repository Description**:
  *Use this description on your GitHub repository settings:*
  > Offline-first AI accounting review agent with deterministic rules, HITL workflow, local RAG, ADK-inspired runtime, tracing, and Cloud Run readiness.
- [ ] **Repository Topics**:
  *Add these tags/topics to maximize project discoverability:*
  `ai-agents` `google-adk-inspired` `streamlit` `human-in-the-loop` `rag` `accounting-automation` `cloud-run` `python` `runtime-observability` `portfolio-project`

---

## 🚀 3. Release Publishing Steps
- [ ] **Commit Changes**: Ensure your workspace is clean and all files are committed.
- [ ] **Tag the Commit**:
  ```bash
  git tag -a v2.0.0-portfolio -m "Release v2.0.0-portfolio"
  git push origin v2.0.0-portfolio
  ```
- [ ] **Create GitHub Release**:
  - Go to your repository's Releases page on GitHub.
  - Click "Draft a new release".
  - Choose the tag `v2.0.0-portfolio`.
  - Copy and paste the contents of [docs/github_release_draft.md](github_release_draft.md) into the description.
  - Attach synthetic demo screenshots or recordings under assets if captured.
  - Click "Publish release".

---

## 🌐 4. Portfolio Website Integration
- [ ] **Case Study Link**: Add a link to [docs/portfolio_case_study.md](portfolio_case_study.md).
- [ ] **Architecture Link**: Link to [docs/runtime_architecture.md](runtime_architecture.md) for hiring managers who want a deep-dive into the agent design.
- [ ] **Demo Guide Link**: Link to [docs/demo_assets_guide.md](demo_assets_guide.md).

---

## 💼 5. LinkedIn & CV Optimization
- [ ] **Safeguards Checked**: Ensure resume bullet points describe the *architecture* and *readiness* of the agent rather than claiming real cloud deployment, hosted LLM usage, or official regulatory authority.
