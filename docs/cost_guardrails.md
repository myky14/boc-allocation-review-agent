# Google Cloud Run Cost Guardrails & Budget Documentation

This document describes recommended cost-control settings, billing configurations, and safety checklists for deploying the **BOC Allocation Review Agent** on Google Cloud Run.

---

## 1. Purpose

This guide outlines cost-safety practices and billing configurations for running the Streamlit dashboard on Google Cloud Run. 

### Critical Disclaimers (Official Billing Principles)
- **No Zero Cost Guarantee**: Running the application on Google Cloud Run is not free and does not guarantee zero costs.
- **No Hard Spending Caps**: In Google Cloud, Billing Budgets are notification and tracking mechanisms, not hard caps. They do not act as hard spending limits and are not a hard spending cap. Budget alerts do not automatically disable resources when thresholds are exceeded.
- **Alerts Do Not Stop Billing**: Budget alert emails are sent to notify project owners of actual or forecasted spend. They do not shut down billing, terminate services, or freeze compute resources.
- **Non-mutating Local Behavior**: The application continues to run using local-first TF-IDF documentation RAG and the deterministic rule engine in `allocation_tool.py`. No external Vertex AI, Gemini, or Generative AI cloud API requests are configured.

---

## 2. Recommended Low-Cost Cloud Run Settings

Per official Google Cloud Run pricing guidelines, compute charges are billed based on allocated CPU, memory, request volume, and processing durations. To control resource consumption and scale down idle costs, we recommend the following container limits:

- **Min Instances**: `0` (`--min-instances 0`)
  - *Why*: Setting min instances to `0` allows the service to scale down to zero when idle, helping reduce compute costs when no active audit reviews are running. Setting min instances to any value greater than 0 will incur charges for kept-warm instances regardless of request traffic.
- **Max Instances**: `1` (`--max-instances 1`)
  - *Why*: Setting max instances to `1` limits normal autoscaling to one configured maximum instance, reducing the risk of runaway scaling. Cloud Run may briefly exceed the configured maximum during traffic spikes, so this is a guardrail, not a hard guarantee.
- **CPU**: `1` (`--cpu 1`)
  - *Why*: Limits compute allocation to a single core, which is sufficient for local rules processing.
- **Memory**: `1Gi` (`--memory 1Gi`)
  - *Why*: Modest memory sizing reduces the hourly pricing rate per instance second.
- **Timeout**: `300` seconds (`--timeout 300`)
  - *Why*: Bounds execution duration to prevent stuck operations from running indefinitely.

*Note: While these settings minimize cost exposure, they do not guarantee that zero charges will be incurred.*

---

## 3. Google Cloud Billing Budget Setup

To track compute spend and receive warning notifications, configure a Billing Budget in the Google Cloud Console:

1. Open the **Google Cloud Console** and navigate to **Billing**.
2. Select **Budgets & alerts** from the left navigation menu.
3. Click **Create budget**.
4. **Scope**: Give the budget a descriptive name (e.g. `boc-agent-demo-budget`) and scope it to your specific project if possible.
5. **Budget Type**: Set the budget type to **Specified Amount**.
6. **Alert Thresholds**: Configure the following recommended starter alert thresholds:
   - **50% of budget**: Sent when actual spend reaches 50%.
   - **90% of budget**: Sent when actual spend reaches 90% (helps warn of approaching limits).
   - **100% of budget (Actual)**: Sent immediately when actual spend matches the budget amount.
   - **100% of budget (Forecasted)**: Sent when Google Cloud forecasts that spend will reach 100% by the end of the billing period.
7. **Actions**: Configure **Email alerts** to send notifications to project billing administrators and users.
8. Click **Finish** to save the budget.

---

## 4. Suggested Starter Budget Amounts

These amounts represent example starter ranges only for project tracking. They are not recommendations, billing allocations, or guarantees of actual costs:

- **USD 1.00 – USD 5.00**: Typical starter range for tracking short private demonstrations or verification runs.
- **USD 10.00 – USD 20.00**: Typical starter range for tracking repeated developer testing cycles.

*Actual costs depend on region selection, traffic volume, logging activity, build logs, and Artifact Registry container sizes. Users should select budget amounts matching their own organization's financial policies and risk tolerance.*

---

## 5. Cost Monitoring Checklist

Actively monitor resource billing to identify unexpected charges:
- **Billing Dashboard**: Review the Cloud Billing reports daily after initiating cloud testing to trace exact SKU costs.
- **Cloud Run Revisions**: Confirm that active revisions maintain `--min-instances 0` and `--max-instances 1` configurations.
- **Artifact Registry**: Cloud Build uploads Docker layers to Artifact Registry. Inspect storage volumes regularly, as container image storage incurs persistent storage charges.
- **Cloud Build Logs**: Monitor Cloud Build history, as build minutes are billed separately.
- **Cloud Logging**: Check Cloud Logging volume and storage settings, as excessive debug logs will increase ingestion costs.
- **Access Policy**: Keep deployment private by default (using `roles/run.invoker`) to prevent public users or automated search bots from triggering requests.

---

## 6. Resource Cleanup Checklist

To stop Cloud Run service request processing and reduce remaining resource exposure:

1. **Delete Cloud Run Service**:
   ```bash
   gcloud run services delete boc-allocation-review-agent \
     --region us-central1
   ```
   *Note: Deleting the Cloud Run service stops active compute request processing for this service. However, it does not delete related build and storage artifacts.*

2. **Clean up Artifact Registry**: Locate the Docker repository created for the service and delete unused image tags to reduce storage charges.
3. **Clean up Storage Buckets**: Check Cloud Storage for any buckets created during Cloud Build or deployment, and delete build logs or cached layers.
4. **Disable Unused APIs**: If the project is no longer in use, disable the Cloud Run API (`run.googleapis.com`) and Cloud Build API (`cloudbuild.googleapis.com`).
5. **Retain Budget**: Keep your Cloud Billing budget active to track any lingering storage charges or API requests.

---

## 7. Demo Safety Checklist

Follow these practices before and during demonstrations:
- **Private Default**: Use `--no-allow-unauthenticated` by default to ensure only authenticated IAM users can access the application.
- **Invoker Role**: Explicitly grant `roles/run.invoker` to authenticated demo users using `gcloud run services add-iam-policy-binding`.
- **Demo Data Only**: Do not upload actual sensitive corporate payroll or production accounting ledgers.
- **Synthetic Ledger**: Use the provided `data/synthetic/synthetic_boc_gl_dataset.xlsx` for all demo runs.
- **Enforce Limits**: Confirm that the runtime properties `--max-instances 1` and `--min-instances 0` are active in your configuration.
- **De-provision**: Delete the Cloud Run service immediately after the demonstration completes.
- **Billing Audit**: Review the Billing Console 24-48 hours post-demo to verify all compute resources have scaled down and trace any lingering storage costs.

---

## 8. What Phase 10.2 Does NOT Do

This phase focuses strictly on documentation and cost guardrails. It does not:
- Does not deploy Vertex AI Search indexes or native vector databases.
- Does not deploy Gemini or other Generative LLM API configurations.
- Integrate native Google Cloud Agent Engine runtime objects.
- Create automated resource deletion scripts that could accidentally destroy user assets.
- Provide official legal, CRA, CAVCO, or SODEC tax audit certifications.

---

## 9. Future Phase 10.3

Phase 10.3 will be the **Optional ADK / Vertex AI Migration Guide**. It will describe the transition path from local deterministic and TF-IDF RAG components to Vertex AI Agent Engine and Vertex Search, maintaining the deterministic rules engine in `allocation_tool.py` as the source of truth.
