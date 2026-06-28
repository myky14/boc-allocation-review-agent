# Technical Interview Preparation Notes

This guide provides structured Q&A prep for discussing the **BOC Allocation Review Agent** architecture and design decisions during technical interviews.

---

## 1. Core Architecture & Design Decisions

### Q1: Why did you use a deterministic rule engine instead of an LLM for tax eligibility?
- **Answer**: 
  > "Tax eligibility suggestions are based on deterministic internal review rules and synthetic workbook conventions, rather than official statutory interpretation. Large Language Models are probabilistic and prone to mathematical calculations errors and formatting drifts. 
  > In accounting compliance, tax allocations must be deterministic and auditable. We isolate the internal review rules in a core deterministic rule engine (`allocation_tool.py`) while using the AI layer strictly to route queries, summarize details, and format user disclaimers, ensuring it does not provide official tax/legal determinations."

### Q2: Why did you implement a local TF-IDF retriever for RAG instead of semantic embeddings?
- **Answer**: 
  > "We had three goals: privacy, zero-hallucination grounding, and zero API dependency. 
  > TF-IDF is highly effective for searching specific regulatory keywords (like 'Location 920' or 'Form 6') without external API calls or network hops. 
  > It operates entirely offline, keeping corporate General Ledger structures secure within the local filesystem."

### Q3: Why is Human-in-the-Loop (HITL) designed into this agent?
- **Answer**: 
  > "Accounting files cannot be silently modified by an AI agent. 
  > If a transaction's confidence score falls below our threshold, or the query triggers a capability refusal, the agent flags the transaction and routes it to a dedicated Human Review Queue. 
  > Manual overrides are recorded in separate database columns (`human_review_decision`, etc.), ensuring the agent's initial suggestions and human changes are both preserved for audit trails."

### Q4: What is the purpose of SKILL.md?
- **Answer**: 
  > "SKILL.md defines our agent's capability contract. 
  > It declares permitted parameters, grounding policies, and refusal criteria. 
  > The local runtime parses this contract at start-up, allowing the planner to refuse out-of-scope requests (like requests for official legal opinions or tax filing creations) before any execution occurs."

---

## 2. ADK, Tracing & Cloud Deployment

### Q5: Why is the runtime described as "ADK-inspired"?
- **Answer**: 
  > "To prepare for future integration with Google's native Agent Development Kit (ADK), we structured the local runtime to match ADK primitives. 
  > Planners, Tool Registries, Executors, and Runtime Contexts are decoupled as separate Python classes. 
  > Tools are stateless and accept standard python data types, making it simple to wrap them in native ADK wrappers in the future without changing our rules."

### Q6: Why did you build a custom RuntimeTrace instead of using cloud telemetry?
- **Answer**: 
  > "To support local development and offline auditing, we built a local trace logger. 
  > It captures intent classifications, tool execution latency, matched row counts, and confidence timelines. 
  > It captures intent classifications, tool execution latency, matched row counts, and confidence timelines. 
  > It also records observable runtime decisions, checks, and outcomes (such as PII and mutation block status). Permission checks, mutation blocking, and dataframe/tool restrictions are enforced by the runtime, executor, and skill policy layers; RuntimeTrace supports auditability but does not enforce controls itself. This structured JSON trace is exposed on the dashboard and saved locally, providing audit transparency."

### Q7: Why did you containerize for Cloud Run and how do you control cost?
- **Answer**: 
  > "Cloud Run provides a simple, secure hosting target for the Streamlit dashboard. 
  > To control costs, we configure `--min-instances 0` to scale to zero when idle, `--max-instances 1` to limit runaway scaling, and modest CPU/memory limits. 
  > We also recommend Google Cloud Billing budgets and alert emails to monitor cost exposure without creating destructive automated shutdown scripts."

---

## 8. Safety, Cost & Mitigations

### Q8: How does the system prevent model hallucinations?
- **Answer**: 
  > "We apply three layers of protection:
  > 1. Strict Grounding: The local TF-IDF retriever extracts exact paragraphs from documentation. 
  > 2. Zero-Math AI: The AI orchestrator never calculates tax splits; it delegates all calculations to the deterministic rule engine.
  > 3. Disclaimer Policy: Out-of-scope requests trigger predefined refusal strings defined in our SKILL contract."

### Q9: How do you preserve auditability?
- **Answer**: 
  > "Every review run writes suggestions to dedicated agent columns, leaving the original transaction details intact. 
  > Every conversational response logs a detailed execution trace mapping exactly how the planner matched the user query to specific tools or doc references."

### Q10: What would you improve in this project with more time?
- **Answer**: 
  > "I would expand the specialist rules to support British Columbia (FIBC) tax credits, and write a helper script for mapping data structures across custom ERP ledgers."
