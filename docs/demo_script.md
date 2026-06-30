# Presenter Demo Script: BOC Allocation Review Agent

**Estimated Duration**: 5 – 7 minutes  
**Target Audience**: Technical recruiters, AI engineers, and product managers.

---

## 1. Opening & Problem Statement (0:00 - 1:00)
- **Presenter Action**: Show the project homepage or project repository README.
- **Wording / Talking Points**:
  > "Hello, today I'll demonstrate the BOC Allocation Review Agent. Media production projects face complex compliance challenges when allocating labor and corporate expenses for tax credits under Canadian and Quebec rules.
  > Historically, matching transactions against these rules has been a slow, manual process. Our goal is to provide a local-first, ADK-inspired review assistant that provides deterministic and auditable review support. 
  > Crucially, this agent is an administrative review support tool; it does not provide official tax/legal determinations or compile government applications."

---

## 2. Architecture Overview (1:00 - 1:45)
- **Presenter Action**: Display the system diagram from the case study or README.
- **Wording / Talking Points**:
  > "To ensure auditability, our architecture decouples conversational AI from rule calculation. 
  > We use an ADK-inspired pipeline: an orchestrator manages planning, tool registry lookup, and tracing. 
  > However, all calculations are executed by a core deterministic rule engine. 
  > We also include a local TF-IDF retriever for text search, a human-in-the-loop review pipeline, and local runtime tracing, all containerized and ready for Google Cloud Run."

---

## 3. CLI Workbook Review Demo (1:45 - 2:30)
- **Presenter Action**: Open terminal and run the CLI review command:
  ```bash
  uv run python -m boc_agent.cli --input data/synthetic/synthetic_boc_gl_dataset.xlsx --output outputs/reviewed_boc_gl_dataset.xlsx
  ```
- **Wording / Talking Points**:
  > "Let's start in the terminal. I am running our batch review CLI to process a synthetic General Ledger containing 201 transaction rows. 
  > The CLI executes our deterministic specialist tools, runs the validation rules, and writes suggestions back to a new workbook. 
  > As you can see, the batch runs completely locally in under two seconds. Let's see the metrics in the dashboard."

---

## 4. Streamlit Dashboard Demo (2:30 - 3:15)
- **Presenter Action**: Open your browser to the local Streamlit dashboard (usually `http://localhost:8501` or proxy URL):
  ```bash
  uv run streamlit run app.py
  ```
  Navigate to the **Auditor Workspace** tab and point to the charts.
- **Wording / Talking Points**:
  > "In the Streamlit interface, we load our reviewed workbook. 
  > Out of 201 rows, the agent approved 113 transactions and routed 88 to our Human-in-the-Loop review queue. 
  > We can filter by location, regional credit flags, or rule code to inspect exactly why certain expenses were flagged."

---

## 5. HITL Review Queue Demo (3:15 - 4:00)
- **Presenter Action**: Point to the "Needs Human Review" queue. Run the queue builder command or demonstrate the review queue export:
  ```bash
  uv run python scripts/build_review_queue.py outputs/reviewed_boc_gl_dataset.xlsx outputs/human_review_queue.xlsx
  ```
- **Wording / Talking Points**:
  > "For compliance integrity, we never overwrite data. 
  > Flagged rows are exported to `human_review_queue.xlsx`. 
  > The auditor reviews the items and writes manual override decisions. 
  > These are stored in dedicated columns like `human_review_decision`, ensuring the agent's calculations and the human overrides are both preserved as a clean audit trail."

---

## 6. Conversational Assistant & RAG Demo (4:00 - 5:00)
- **Presenter Action**: Navigate to the **Review Assistant** tab. Enter the following example questions:
  1. Question: `Show me the review queue summary.`
  2. Question: `What is Location 920?`
  3. Question: `Explain transaction Ref 100.`
  4. Question: `What does the Human-in-the-Loop process do?`
- **Wording / Talking Points**:
  > "Now, let's look at the Review Assistant. This conversational interface allows accountants to query the workbook and rules. 
  > If I ask 'What is Location 920?', the agent runs our local TF-IDF RAG retriever to search local documentation files. 
  > It extracts the exact section explaining that Location 920 is outside Canada and requires out-of-Canada handling, and formats the answer with strict grounding disclaimers. 
  > The assistant operates completely offline, ensuring zero external LLM hallucinations."

---

## 7. Runtime Trace & Observability Demo (5:00 - 5:45)
- **Presenter Action**: Expand the **Runtime Trace** accordion under the assistant's response.
- **Wording / Talking Points**:
  > "Every conversational interaction generates a complete, auditable timeline trace. 
  > Here, we see the step-by-step latency, the planner's intent classification, the matched tools, the exact rows of data accessed, and the stage confidence timeline. 
  > We also verify that PII and data mutation blocks are fully active, preventing any unauthorized changes during query execution."

---

## 8. Docker & Cloud Run Readiness (5:45 - 6:30)
- **Presenter Action**: Open `Dockerfile` and `docs/cost_guardrails.md` in the editor.
- **Wording / Talking Points**:
  > "The application is packaged inside a non-root Docker container, ready for Cloud Run. 
  > To ensure deployment safety, we have documented low-cost configurations, such as min-instances 0 to scale to zero, max-instances 1 to limit runaway scaling, and GCP Billing budget alerts. 
  > Our doc validation tests ensure that all disclaimers are accurate and cost cautions are in place before deployment."

---

## 9. Closing Summary (6:30 - 7:00)
- **Presenter Action**: Return to the repository homepage.
- **Wording / Talking Points**:
  > "To summarize, the BOC Allocation Review Agent combines a deterministic rule engine, a local TF-IDF RAG, runtime tracing, and Cloud Run deployment readiness into an offline-first compliance support tool. 
  > With 307 unit tests passing, the system is fully verified and ready. Thank you for your time!"
