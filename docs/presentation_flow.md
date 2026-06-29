# Presentation Flow Guide

This document maps out different presentation formats and focal points for demonstrating the **BOC Allocation Review Agent** to interviewers, recruiters, or technical audiences.

> [!IMPORTANT]
> **Asset Status**: All visual assets, gifs, and video walkthroughs referenced in this repository are placeholders. Any presentation slide deck or recorded demo must be created manually using synthetic data only.
>
> **Safety boundaries**: No cloud deployment has occurred in this repository. All demo guides focus on local terminal execution and local Streamlit dashboard views.

---

## 🔒 Safety & Anonymization Rule
- **Synthetic Data Only**: All slides, walk-throughs, and code snippets must show only synthetic data from the provided ledger `synthetic_boc_gl_dataset.xlsx`.
- **No Credentials**: Hide all local path references, credentials, access keys, or cloud billing IDs in your slides or code repository.

---

## ⏱️ Presentation Formats

### 1. The 1-Minute Elevator Pitch
- **Goal**: High-level value proposition and system boundary clarity.
- **Timeline**:
  - **0:00 - 0:20**: Introduce the problem (labor allocation compliance for media tax credits) and our solution (an offline-first co-pilot).
  - **0:20 - 0:40**: Emphasize that the core rules engine is completely decoupled from the AI planner to ensure deterministic correctness.
  - **0:40 - 1:00**: Highlight safety boundaries: strictly a review support tool, no live government registry connections, and no official statutory rulings.

### 2. The 3-Minute Technical Overview
- **Goal**: Architecture details and decoupling validation.
- **Timeline**:
  - **0:00 - 0:45**: Pitch & Decoupled Architecture. Show the system flow diagram. Explain that all calculations are left to `allocation_tool.py`.
  - **0:45 - 1:45**: CLI & Streamlit walk. Emphasize local processing speed (201 rows reviewed in under 2 seconds) and the Human-in-the-Loop review queue.
  - **1:45 - 2:30**: Observability. Demonstrate the `RuntimeTrace` accordion logging intent capability matching and confidence timelines.
  - **2:30 - 3:00**: Cloud Run containerization readiness and GCP budget guardrail checklists.

### 3. The 5-7 Minute Full capstone Demo
- **Goal**: Comprehensive presentation, including conversational RAG and codebase walkthroughs.
- **Timeline**: Follow the detailed script documented in [docs/video_recording_guide.md](video_recording_guide.md).

### 4. The 10-Minute Technical Interview
- **Goal**: Code review, design trade-offs, and Q&A.
- **Timeline**:
  - **0:00 - 2:00**: Full demo presentation.
  - **2:00 - 5:00**: Codebase tour. Open `boc_agent/runtime/` and show the Planner, Executor, and Tool Registry classes. Open `tests/` and show the 246-test suite coverage.
  - **5:00 - 10:00**: Interactive Q&A. Prepare answers using the guide in [docs/interview_notes.md](interview_notes.md).

---

## 🎯 Key Engineering Focal Points to Emphasize

- **Deterministic Rule Engine as Source of Truth**:
  Explain that you chose *not* to delegate accounting eligibility rules to probabilistic LLMs. All allocations are calculated deterministically by python code in `allocation_tool.py`, eliminating hallucinations.
  
- **No LLM-Based Accounting Decisions**:
  The AI orchestrator performs routing, capability checks, and grounding descriptions, but it is strictly prohibited from altering or overriding rules engine calculations.
  
- **Human-in-the-Loop (HITL) Safety**:
  Uncertain allocations are routed to `human_review_queue.xlsx`. The agent never overwrites original inputs; override selections are kept in separate columns to preserve the audit trail.
  
- **Runtime Observability**:
  Highlight the local `RuntimeTrace` recording classified user intent, latency metadata, and confidence scores across each stage.
  
- **Cloud Run Readiness & Billing Budget Guardrails**:
  Describe containerization safety (running as non-root `appuser`) and low-cost configuration guidance (`min-instances 0` to scale to zero, and billing budget alert thresholds).
  
- **Optional ADK/Vertex AI Migration Path**:
  Show that the local components map directly to Google ADK concepts, making a native cloud migration simple and modular without modifying the underlying rules engine.
