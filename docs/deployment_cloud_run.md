# Google Cloud Run Deployment Guide

This document describes how to containerize and deploy the **BOC Allocation Review Agent** Streamlit application to Google Cloud Run.

---

## 1. Purpose

This deployment places the local-first Streamlit audit dashboard and conversation co-pilot on Google Cloud Run for accessibility by review teams.

### Operational Boundaries
- **No Cloud AI APIs**: In Phase 10.1, the agent does not connect to Vertex AI, Gemini, or any external LLM services.
- **Local RAG & Rules**: The documentation RAG uses the local TF-IDF retriever index, and transaction analysis uses the local deterministic rules in `allocation_tool.py`.
- **Offline Integrity**: The application operates completely self-contained and offline. No live registry validation (CRA, CAVCO, Ontario Creates, SODEC) or payroll integrations are executed.

---

## 2. Prerequisites

Before deploying, ensure you have:
1. A **Google Cloud Project** with **Billing Enabled**.
2. Installed and authenticated the [gcloud CLI](https://cloud.google.com/sdk/gcloud).
3. Local **Docker Desktop** installed (if building images locally) or access to **Cloud Build**.
4. IAM permissions:

   For the deployer/user:
   - **Cloud Run Source Developer**: `roles/run.sourceDeveloper` (to build from source)
   - **Service Usage Consumer**: `roles/serviceusage.serviceUsageConsumer` (to call APIs)
   - **Service Account User**: `roles/iam.serviceAccountUser` (to run services as service accounts)

   For whichever service account performs the Cloud Build operation:
   - **Cloud Run Builder**: `roles/run.builder` (to package and deploy)

   The active build service account depends on project and organization policy. It may be the legacy
   `PROJECT_NUMBER@cloudbuild.gserviceaccount.com` account, the Compute Engine default
   `PROJECT_NUMBER-compute@developer.gserviceaccount.com` account, or a custom service account.
   Identify the account used by your project before granting permissions. When possible, explicitly
   select a least-privilege custom account with:

   ```bash
   gcloud run deploy boc-allocation-review-agent \
     --source . \
     --build-service-account projects/PROJECT_ID/serviceAccounts/BUILD_SERVICE_ACCOUNT_EMAIL
   ```

   The selected account requires `roles/run.builder`.

   *Note: Avoid broad admin roles unless testing in isolated environments.*

---

## 3. Recommended Safe Deployment Settings

To prevent runaway costs during demonstration and testing, configure the following values:
- **Min Instances**: `0` (scales down to zero when idle to reduce idle costs).
- **Max Instances**: `1` (limits normal autoscaling to one configured maximum instance to reduce the risk of runaway scaling. Note that Cloud Run may briefly exceed the configured maximum during traffic spikes, so this is a guardrail, not a hard guarantee).
- **CPU**: `1` (modest compute allocation).
- **Memory**: `1Gi` (sufficient for the local Python TF-IDF index and Streamlit sessions).
- **Concurrency**: `80` (default Streamlit load sharing).
- **Timeout**: `300` seconds.

---

## 4. Local Docker Build & Execution

To test the containerized application on your workstation before pushing to the cloud:

1. Build the Docker image:
   ```bash
   docker build -t boc-allocation-review-agent .
   ```

2. Run the container:
   ```bash
   docker run --rm -p 8080:8080 --env-file .env.example boc-allocation-review-agent
   ```
   Open `http://localhost:8080` in your browser.

---

## 5. Cloud Run Deploy Command

By default, deployments require authentication for secure enterprise use. Run the following command to deploy from source using Google Cloud Build:

```bash
gcloud run deploy boc-allocation-review-agent \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated \
  --min-instances 0 \
  --max-instances 1 \
  --cpu 1 \
  --memory 1Gi \
  --timeout 300 \
  --set-env-vars BOC_ENV=production,BOC_SKILL_FILE_PATH=SKILL.md
```

> [!NOTE]
> - **Region**: The default region is set to `us-central1`. You can replace this with any supported region close to your users.
> - **Public Demo**: If hosting a public/unauthenticated demonstration dashboard is explicitly required for temporary demo purposes, replace `--no-allow-unauthenticated` with `--allow-unauthenticated`.

---

## 6. Post-Deploy Smoke Test

Once deployed, Google Cloud Run will print a service URL (e.g. `https://boc-allocation-review-agent-xxxx.a.run.app`). Because private deployment (`--no-allow-unauthenticated`) is the safer default, you cannot open this URL directly in an unauthenticated browser. Follow these steps to verify readiness:

Any user, group, or service account accessing a private Cloud Run service must have **Cloud Run
Invoker** (`roles/run.invoker`). For example, grant access to a reviewer with:

```bash
gcloud run services add-iam-policy-binding boc-allocation-review-agent \
  --region us-central1 \
  --member="user:YOUR_EMAIL@example.com" \
  --role="roles/run.invoker"
```

### Option A: Local Proxy (Recommended)
Launch a local proxy tunnel that automatically injects your credentials:
```bash
gcloud run services proxy boc-allocation-review-agent --region us-central1
```
Then navigate to the proxy URL provided (`http://localhost:8080`) in your browser to interact with the dashboard.

### Option B: Authenticated HTTP Request
Verify the response code using an identity token with `curl`:
```bash
curl -i -H "Authorization: Bearer $(gcloud auth print-identity-token)" https://boc-allocation-review-agent-xxxx.a.run.app
```
Confirm the server responds with HTTP `200` or a valid page payload.

### Interacting with the Application
Once accessed:
1. **Verify Home Tab**: Check that the app loads and shows the "reviewed GL upload" interface.
2. **Review Upload**: Upload `data/synthetic/synthetic_boc_gl_dataset.xlsx` and run the review.
3. **Verify Metrics**:
   - Total rows: `201`
   - Approved: `113`
   - Needs Human Review: `88`
4. **Inspect Conversational Assistant**: Go to the chat tab and ask `"What is Location 920?"` to confirm the local TF-IDF retriever retrieves matching documentation excerpts.
5. **Audit Trace**: Inspect the details output to verify the ADK-inspired execution trace operates correctly.

---

## 7. Shutdown & Cost Control

To manage resource usage and scale down idle costs:

1. **Cost Control**: Set `--min-instances 0` and `--max-instances 1` to minimize compute billing when inactive.
2. **Service Deletion**: To stop Cloud Run service request processing for this service, delete the Cloud Run service:
   ```bash
   gcloud run services delete boc-allocation-review-agent \
     --region us-central1
   ```
   *Note: Deleting the service stops Cloud Run service request processing for this service. Other related resources such as build artifacts, logs, storage, or project-level services may still incur costs. Review and clean associated resources to reduce remaining costs.*
3. **Budget Guardrails**: Configurable GCP budget alerts, cost safety disclaimers, and resource cleanup checklists are detailed in the [docs/cost_guardrails.md](cost_guardrails.md) guide.

---

## 8. Limitations & Scope

- **No Official Determinations**: The tool is an administrative aid. It does not issue official CRA/CAVCO rulings or output official CAVCO Form 6 PDF applications.
- **No Vertex AI / Gemini Integration**: Vertex AI Agent Engine and Gemini API integration are not active in Phase 10.1.
- **Demo Scope Only**: Do not upload actual sensitive production payroll ledgers or proprietary corporate spreadsheets during public demonstrations.
