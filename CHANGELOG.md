# Changelog

All notable changes to this project will be documented in this file.

## v2.0.0-portfolio (Draft)

*Planned release notes for portfolio publication.*

### Added
- **Recruiter Quick-Start**: High-level onboarding guide for code reviewers ([docs/recruiter_quickstart.md](docs/recruiter_quickstart.md)).
- **Portfolio Publishing Checklist**: Steps for repository safety, topics, and GitHub publishing ([docs/portfolio_publishing_checklist.md](docs/portfolio_publishing_checklist.md)).
- **Project Pitch Snippets**: Reusable elevator pitches, CV bullet points, and LinkedIn post drafts ([docs/project_pitch.md](docs/project_pitch.md)).
- **Final QA Checklist**: Automated commands, metrics expectations, and audit checks ([docs/final_qa_checklist.md](docs/final_qa_checklist.md)).
- **Demo Asset Guides**: Added guides for screenshot capture checklists, video recording scripts, and flow presentation guidance.
- **Cost Guardrails**: Instructions for low-cost setups and Google Cloud budget safety.
- **ADK / Vertex Migration Guide**: Conceptual blueprint mapping local patterns to native cloud services.

### Changed
- **Documentation Polish**: Standardized and refined README, case study, and architecture reviews for clear portfolio presentation.
- **Verification Suite**: Expanded the automated test harness to 287 passing tests, adding robust claim detection, absolute path scanners, and local image link resolution checks.

---

### Notes
- **Deterministic Rule Integrity**: Core business rule engine (`boc_agent/tools/allocation_tool.py`) remains the deterministic final source of truth and was untouched.
- **Truthful Scope**: This project does not deploy to live GCP servers, does not use paid API keys, and does not provide official tax/legal determinations.
