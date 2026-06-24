# Problem Statement: Production Accounting & Tax Credit Compliance

## 1. The Real-World Pain Point

In the Canadian film and television industry, production financing relies heavily on public tax incentives. The federal **Canadian Film or Video Production Tax Credit (CPTC)**, administered by **CAVCO** (Canadian Audio-Visual Certification Office) and the **Canada Revenue Agency (CRA)**, provides a refundable tax credit based on qualified labour expenditures. In combination with provincial tax credits (such as the Ontario Creates or Quebec SODEC tax credits), tax incentives represent a critical portion of a production's financing.

However, claiming these credits requires production accountants to manually analyze every transaction in the General Ledger (GL) to determine if it meets specific eligibility criteria and map it to the correct tax credit categories (the "Breakdown of Costs"). 

This GL review is historically tedious, manual, and prone to human error because of the following realities in production accounting offices:
- **Payee & Vendor Structures**: Payees are structured differently (employees, sole proprietors, loan-out corporations, corporate suppliers, or partnerships), each requiring distinct classification and documentation treatment.
- **Residency Status**: Eligibility is highly dependent on individual residency and service location constraints.
- **Complex Capping Guidelines**: Certain expense types (such as catering, craft services, per diems, and creative multi-share labor) have specific regulatory caps or partial claim percentages.

---

## 2. Why BOC Allocation Reviews Are Difficult

Reviewing a ledger for a Breakdown of Costs (BOC) submission is a multi-layered classification task governed by nested regulatory rules:

1. **Hierarchy of Rules**: 
   A cost's eligibility depends on several dependent variables. For instance, to classify labor paid to a **loan-out corporation** (a personal services corporation owned by an actor or crew member) as an eligible Ontario Creates expense, the accountant must verify:
   * Is the loan-out corporation registered in the province?
   * Is the individual owner/employee a Canadian citizen/PR?
   * Is the individual owner/employee a resident of that province?
   * Was the service rendered within provincial boundaries?
   * If any of these conditions are unverified, the transaction must be allocated to a different bucket (e.g., Out of Canada labor, Fed-only eligible, or completely non-eligible).

2. **Vague and Confusing Ledger Entries**:
   GL transaction logs are notoriously sparse and filled with shorthand. An entry like `P/R O.T. J. SMITH DEP 41` contains no explicit citizenship or residency information. In a real workflow, accountants must manually cross-reference names against crew rosters, residency declarations, and department codes. In our synthetic environment, the agent must evaluate the transaction using available workbook fields (like address fields, Ep codes, application province, and transaction descriptions) and suggest likely treatments.

3. **Complex Capping and Exclusions**:
   - **Meals & Catering**: Meal expenses (catering, craft service, and per diems) must be isolated from standard labor or equipment spend.
   - **Multi-Share Labor**: Creative professionals working in multiple roles (e.g., a director who also acts or produces) must have their compensation split according to specific allocation percentages.

---

## 3. How Accountants Currently Perform This Work

Currently, the process is highly manual, retrofitted, and spreadsheet-reliant:

- **Spreadsheet Filters**: At the end of production, accountants export the general ledger into Microsoft Excel.
- **Manual Mapping**: They manually filter payee columns, cross-referencing names against crew files and residency sheets.
- **Formula Copy-Pasting**: Accountants spend hours mapping each line to tax-credit worksheets, manually applying formulas to calculate the eligible portion of per diems or loan-out fees.
- **Time Constraints**: Because of time limits, accountants are forced to perform deep reviews only on high-value transactions, which leaves the production vulnerable to classification errors on smaller expenses.

---

## 4. The Business Impact of Mistakes

Errors in BOC allocation have immediate, high-stakes consequences for production companies:

* **Financial Under-claiming (Lost Revenue)**:
  If accountants miss eligible provincial or federal costs due to vague ledger descriptions, the production company under-claims its tax credit, resulting in direct financial loss.
* **Audit Clawbacks and Delayed Financing**:
  If the CRA or CAVCO audits the production and finds that ineligible expenses (e.g., non-resident labor or unverified loan-outs) were claimed, they will claw back the credit with interest. Furthermore, production banks provide interim loans secured against these anticipated tax credits. If CAVCO delays certification due to errors, the bank will freeze drawdowns, risking default.

---

## 5. How the AI Agent Helps

The **BOC Allocation Review Agent** is a focused AI assistant that helps accountants review already-cleaned/enriched GL workbooks. It does **not** replace human professionals, connect to live governmental systems, query citizenship databases, or produce finalized official tax forms.

Instead, the agent provides value by:
- **Analyzing Available Workbook Fields**: The agent processes transaction columns (e.g., Application Province, Location, Ep code, vendor/payee structure, employee/loan-out data, tax ID placeholders, address fields, and descriptions) and applies synthetic policy documents and mapping rules.
- **Suggesting Likely Treatment**: It outputs a suggested allocation column, eligible amount percentage, and eligibility status.
- **Flags Missing or Conflicting Evidence**: The agent identifies rows with missing or conflicting evidence (e.g., missing tax IDs, missing addresses, or missing Location values) and marks them for human review.
- **Generating Reasoning and Reference Rules**: It provides a clear, natural language explanation and cites the reference rules used, supporting accountant review rather than replacing professional judgment.
- **Routing Ambiguous Cases**: It flags ambiguous rows as `Needs Human Review` directly in the output workbook, allowing the accountant to focus their expertise on high-risk or complex transactions.
