# Demo Assets Guide

This document explains how to utilize, place, and format optional visual demo assets for showcasing the **BOC Allocation Review Agent** project.

> [!IMPORTANT]
> **Asset Status**: All visual folders and guidelines in this repository contain placeholder `.gitkeep` files only. Presenters must capture and place actual screenshots or videos from their local workspace.
>
> **Safety boundaries**: No cloud deployment has occurred in this repository. All assets must use synthetic data only and exclude sensitive financial records, local machine paths, usernames, or cloud billing IDs.

---

## 📁 Related Assets & Guides
Use the following resources to prepare your portfolio presentation:
- **Folder structure**: [assets/README.md](../assets/README.md) details the recommended folder mappings and example filenames.
- **Screenshot Checklist**: [docs/screenshot_checklist.md](screenshot_checklist.md) contains the capture checklist for dashboard, assistant, and trace interfaces.
- **Video Walkthrough Guide**: [docs/video_recording_guide.md](video_recording_guide.md) provides timing allocations and narration talking points.

---

## 🎨 Asset Application in Presentations

### 1. GitHub Repository README
If you capture suggested screenshots, you can link to them in your repository README or update the README to embed them.
- *Tip*: Do not commit large uncompressed images. Convert captured PNGs to optimized formats or link to them relative to the repository assets folder.
- *Caution*: Do not embed markdown images referencing missing files or use HTML image tags for placeholders; use links to the checklist instead.

### 2. GitHub Release Attachments
When building a release tag (e.g. `v2.0.0-portfolio` following the [release checklist](release_checklist.md)), upload your captured walkthrough video (`videos/capstone_demo_walkthrough.mp4`) as a release attachment.
- *Suggested wording*: *"A video walkthrough of the offline-first auditor workspace and Review Assistant using synthetic workbook data is attached to this release."*

### 3. Portfolio Website Case Study
When presenting this capstone on a personal portfolio website:
- Embed the suggested screenshots showing the Streamlit dashboard metrics cards and the interactive Human-in-the-Loop review queue.
- Show the custom `RuntimeTrace` accordion to demonstrate depth in AI engineering observability.
- Explain the decoupled architecture (ADK-inspired orchestrator vs deterministic rules engine) using structured flowcharts.

### 4. LinkedIn Project Post
- Share a short 1-2 minute clip (converted from your walkthrough video) demonstrating terminal execution of the CLI review tool processing the 201 transaction rows.
- Highlight the decision to isolate accounting rules in a deterministic python script to eliminate LLM math hallucinations.

---

## 🛡️ Safety & Anonymization Audit
Before publishing any captured asset publicly, run this audit checklist:
1. **Synthetic data validation**: Confirm that the transaction IDs (e.g., `Ref 1` to `Ref 201`) match the synthetic workbook format.
2. **Path check**: Ensure terminal commands do not reveal absolute local file system roots (e.g. drive folders like Users/Username/...).
3. **Billing ID check**: Check that no actual cloud project accounts or billing email alerts are visible.
