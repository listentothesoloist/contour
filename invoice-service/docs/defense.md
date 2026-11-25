# Presentation Outline and Demo Script

Basis: Case 04, kick-off briefing, and defense guidelines. This is a talk track and slide outline; submission status, private repository settings, and reviewer access are verified separately by the project owner.

## 1. Client and Problem

**North Berry**, Accounting Department. To prepare a payment, an accountant manually reconciles each supplier email against the ERP purchase order, posted warehouse receipt, and Directum RX approval. Duplicates, differing packaging units, and revised versions increase review time and create the risk of an inaccurate payment registry.

## 2. Three Findings from the Data

1. Out of 25 emails, only 8 are ready for the draft payment registry, 14 require follow-up, and 3 are informational. A flat inbox hides very different next actions.
2. Duplicate invoices and superseded versions account for $131,500 in risk flags. Invoice numbers must be normalized per supplier, and the full revision chain must be preserved.
3. Warehouse receipt does not authorize a price or quantity overrun; absence of a receipt does not mean automatic rejection. Signed amendment boundaries and contract payment terms are required.

$274,280 is the total value of flagged amounts, not proven prevented losses.

## 3. Solution: Before → After

**Before:** email → manual lookup across multiple systems → manual unit/math recalculation → ad-hoc messaging → manual registry assembly.

**After:** email → automated matching and explainable rule checks → specific discrepancy and draft follow-up → accountant verifies decision → treasurer confirms bank statement → CFO approves payment registry.

How it differs from a spreadsheet: revision history, invoice number normalization, compound packaging conversion, approval scope enforcement, cumulative receipt tracking, and next-step guidance in a single card. This is a working prototype running on a local snapshot without live ERP integrations.

## 4. Value and Verification

Verified by automated tests: all 25 source documents, their statuses and amounts; 5 demo presets; regression audit cases; HTTP API and revision chains. Independent accuracy on live production traffic is not measured by these tests.

Estimated time savings: `(160 × (15 − 1.5)) / 60 = 36 hours per month`. At $1,200/hr equivalent rate units (configurable in the calculator), all parameters and assumptions are transparent. No live accountant benchmarks or time studies have been run yet; deployment and maintenance costs are excluded.

Measurement plan: process the same batch of new anonymized invoices manually and with the pilot; measure elapsed time, manual clarification rate, false approvals, and missed discrepancies against an accountant-approved ground truth before recalculating ROI and TCO.

## 5. Demo Walkthrough (4–5 minutes)

"Let me walk through the flow from an incoming email to explainable checks and controlled export."

1. Queue: `E-06` — corrected invoice and conversion from bags to kilograms.
2. `E-13` — approval is signed, but not yet effective for this delivery date.
3. Open **Check**, select **"AI: 'adhesion' instead of 'adhesive'"**, and click **Run reconciliation**. Show the mapping `"adhesion"` → `"adhesive"`, order `PO-08`, and amount `$22,800`. Then change `48 mm` to `50 mm` and show how the engine flags the dimension mismatch.
4. Enter an unknown order or an email missing quantity/price: the system asks for manual review with `$0` payable.
5. Show the draft follow-up message and payment registry: export remains disabled until bank statement verification is explicitly checked.

Before presenting, start Ollama, pull `qwen3:1.7b`, run `python3 app.py --verify`, and launch `python3 app.py`. Run the AI demo once beforehand and keep the app open in the browser.

## Risks and Rollout

| Limitation | Action Before Production Rollout |
| --- | --- |
| Parser targets single-line invoices in the case format | Validate on new document layouts; add attachment extraction with human field confirmation |
| ERP / Directum snapshots can become stale | Connect live data feeds with refresh timestamps and a decision audit log |
| Bank details, contracts, and bank statements are absent | Integrate verified vendor master data, prepayment terms, and treasury reconciliation |
| No explicit delivery batch IDs | Link invoices to receipt IDs and allocate invoices across partial deliveries |
| Automated decisions can make mistakes | Start in advisory mode, preserve manual sign-off, and maintain regression tests |
| Support and access control | Assign a rule owner, configure accountant/treasurer/CFO roles, and document exception handling |

In the pilot, a local LLM maps informal wording to the ERP order description and extracts missing fields from free-form emails. The rule engine validates every mapping against Excel and highlights the substitution. An operator explicitly confirms proposed fields in the invoice card. Both in the single-email form and during Excel upload, the model is invoked only on rows where rule-based reconciliation is insufficient. Local execution incurs no per-request API fee; hardware, operations, and actual time savings should be measured separately.

For model comparisons and ROI calculations, see [Model Selection and Impact Estimate](model-selection.md).
