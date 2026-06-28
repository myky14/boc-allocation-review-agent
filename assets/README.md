# Demo Assets Repository

This directory acts as a structured folder system designed to hold optional visual assets (such as screenshots, GIFs, diagrams, and video walkthroughs) for portfolio presentations and repository showcases.

> [!WARNING]
> **Placeholder Directory**: No actual screenshots, GIFs, or walkthrough videos are committed in this folder to prevent repository bloat and ensure confidentiality. Developers or presenters are expected to capture these assets from their local environment following the guides below.

---

## 🔒 Safety & Confidentiality Guidelines
When capturing visual assets, adhere strictly to the following rules:
- **Synthetic Data Only**: Only capture screens using the provided synthetic datasets (e.g., `data/synthetic/synthetic_boc_gl_dataset.xlsx`).
- **No Private Data**: Never capture or show real financial details, payroll summaries, or corporate General Ledgers.
- **No Credentials**: Hide all local machine paths, usernames, email addresses, access tokens, API keys, or security credentials.
- **No Billing Project IDs**: Blur or exclude any actual Google Cloud project identifiers or billing account numbers from billing console screenshots.

---

## 📁 Suggested Subfolder Structure
If you decide to capture and store visual assets, place them in the following subfolders using the recommended example filenames:

- **`screenshots/`**: Holds static interface captures.
  - *Example filename*: `screenshots/01_dashboard_overview.png` (Suggested screenshot of the Streamlit Auditor Workspace page).
  - *Example filename*: `screenshots/02_review_metrics.png` (Suggested screenshot of the workbook metrics cards).
  - *Example filename*: `screenshots/03_human_review_queue.png` (Suggested screenshot of the Needs Human Review queue table).
  - *Example filename*: `screenshots/04_conversational_assistant.png` (Suggested screenshot of the Review Assistant tab answering a question).
  - *Example filename*: `screenshots/05_runtime_trace.png` (Suggested screenshot of the expanded Runtime Trace observability timeline).
  - *Example filename*: `screenshots/06_cloud_run_ready_docs.png` (Suggested screenshot of the cost safety checklist documentation).

- **`gifs/`**: Holds short animated recordings of interactions.
  - *Example filename*: `gifs/streamlit_dashboard_demo.gif` (Placeholder GIF demonstrating filtering workbook rows).
  - *Example filename*: `gifs/conversational_assistant_demo.gif` (Placeholder GIF demonstrating RAG document search).

- **`videos/`**: Holds high-resolution video walkthroughs.
  - *Example filename*: `videos/capstone_demo_walkthrough.mp4` (Placeholder for the 5-7 minute walkthrough recording).

- **`diagrams/`**: Holds architecture flowcharts.
  - *Example filename*: `diagrams/runtime_architecture.png` (Placeholder for the decoupled runtime pipeline flowchart).
  - *Example filename*: `diagrams/cloud_run_deployment.png` (Placeholder for the Cloud Run container deployment structure).

---

## 🔗 Related Guides
- Review the [screenshot checklist](../docs/screenshot_checklist.md) to understand which screens to capture.
- Review the [video recording guide](../docs/video_recording_guide.md) for recording step-by-step narration scripts.
- Review the [demo assets guide](../docs/demo_assets_guide.md) to learn how to present these visuals on portfolios or GitHub.
