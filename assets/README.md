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
If you decide to capture and store visual assets, place them in the following subfolders:
- **`screenshots/`**: Holds static interface captures.
- **`gifs/`**: Holds short animated recordings of interactions.
- **`videos/`**: Holds high-resolution video walkthroughs.
- **`diagrams/`**: Holds architecture flowcharts.

---

## ⏱️ Recording Order & GIF Lengths

When capturing animated GIFs for GitHub presentation, follow this recommended recording flow to maximize recruiter engagement:

1. **GIF 1: Workbook Upload & Audit Processing**
   - *Presenter Action*: Open the Streamlit dashboard, drag and drop `data/synthetic/synthetic_boc_gl_dataset.xlsx`, click "Run Review Pipeline", and watch the metrics cards populate.
   - *Target Length*: 8 - 12 seconds.
   - *Recommended Filename*: `gifs/01_upload_and_review.gif`
2. **GIF 2: Human-in-the-Loop Override Action**
   - *Presenter Action*: Filter the review queue to rows with low confidence, select one row, override the suggested allocation category, type an override reason, and click "Submit Audit Decision".
   - *Target Length*: 10 - 15 seconds.
   - *Recommended Filename*: `gifs/02_human_override.gif`
3. **GIF 3: Conversational Review Assistant & Local RAG**
   - *Presenter Action*: Open the chat tab, type "What is Location 920?", watch the template-grounded RAG response display the relative markdown source file and parent heading instantly.
   - *Target Length*: 6 - 10 seconds.
   - *Recommended Filename*: `gifs/03_conversational_rag.gif`

---

## 📦 Compression & Naming Conventions

To keep page load speeds fast on GitHub and portfolios, apply these compression guidelines:
- **GIF Optimization**: Use tools like `gifsicle` or Ezgif with lossy compression level 30–50. Keep individual GIF file sizes under **3MB**.
- **Alternative Video Formats**: For longer high-definition sequences, record in **WebM** or **MP4 (H.264)** formats and target under **10MB** total size.
- **Image Resolution**: Save screenshots as PNG-8 or compressed WebP at a standard width of **1280px** or **1920px**.
- **Naming Conventions**: Use lowercase alphanumeric characters with snake_case and step-number prefixes (e.g. `screenshots/01_streamlit_upload.png`, `gifs/02_override_flow.gif`).

---

## 🖼️ Thumbnail Suggestions
- **Repository Social Image**: Create a primary preview thumbnail at 1280x640 containing a split screen layout: Streamlit metrics dashboard on the left and the decoupled Planner/Executor code layout on the right.
- **Mermaid Flowchart Render**: Export the Mermaid diagram from `docs/architecture_diagram_guide.md` as a high-contrast PNG to use as the visual cover for technical architecture posts.
