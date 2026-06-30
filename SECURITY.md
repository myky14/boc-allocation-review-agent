# Security Policy

This document outlines the security postures, vulnerability reporting guidelines, and data privacy expectations for the `boc-allocation-review-agent` repository.

---

## 🔒 Responsible Disclosure

If you discover a potential security vulnerability in this project, please notify the maintainers privately rather than opening a public GitHub issue. 

Please provide:
- A detailed description of the vulnerability.
- Steps or a proof-of-concept (PoC) script to reproduce the issue.
- Potential impact on local workbook loading or parsing structures.

Once reported, we will investigate the issue and address it.

---

## 📊 Synthetic Data Policy
- **No Real Financial Data**: To protect industry confidentiality, this repository must contain and process **only synthetic General Ledger data** (e.g. the Canadian film/television datasets located in `data/synthetic/`).
- Never commit or upload real production ledgers, employee payroll details, or corporate tax filings.

---

## 🔑 Secrets & Credentials Policy
- **No Hardcoded Credentials**: No API keys, service account credentials, passwords, or active tokens should ever be committed to the codebase.
- The virtual environment and secrets configurations must reside in the local `.env` file, which is excluded from git tracking via `.gitignore`.
- Developers must use `.env.example` as a template for local variables.

---

## 🛡️ Unsupported Deployment Claims
- **No Live Cloud Deployments**: This project is container-ready (via a multi-stage `Dockerfile`) and contains Cloud Run budget guidelines. However, no live cloud deployment has been executed or is supported. 
- Avoid claiming that the application is hosted on live Google Cloud servers.

---

## 👁️ Privacy & Offline Expectations
- **Zero Third-Party Network Calls**: The agent, TF-IDF RAG retrieval index, and Streamlit frontend are designed to run completely offline.
- No transaction data or search queries are transmitted to external APIs or large language model hosting platforms, ensuring absolute data control.
