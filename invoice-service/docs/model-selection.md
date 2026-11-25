# Why This Model Was Chosen for the Pilot

> Accountants lose time when an invoice arrives in free-form text and individual fields have to be copied manually. We invoke a local LLM only for such emails. It proposes quantity, price, unit, and total with exact source quotes. The accountant confirms the proposed fields, after which deterministic rules verify the purchase order, warehouse receipt, and arithmetic. The local model has no per-request API cost, and operator confirmation time is included in our impact measurement.

## Comparison on the Pilot Task

| Model | Ollama Weights | Field Checks | Final Decisions | Median Latency |
| --- | --- | ---: | ---: | ---: |
| [qwen3:1.7b](https://ollama.com/library/qwen3:1.7b) | 1.4 GB | 20/20 | 5/5 | 0.86 s |
| [gemma4:e4b](https://ollama.com/library/gemma4:e4b) | 9.6 GB | 20/20 | 5/5 | 3.25 s |

We selected Qwen3 1.7B. It passed all five benchmark scenarios and takes only 1.4 GB on disk. On an initial run without few-shot examples in the prompt, the model missed the unit price in an email with a unit typo. After refining the prompt, the server also rejects attempts to reuse the grand total as the unit price. Reliability depends on both the model and server-side validation. The size in the table is the weight footprint on disk. Gemma was measured on an earlier prompt revision with the same set of emails and expected outcomes.

BGE-M3 solves semantic catalog search. Testing on local Ollama showed cosine similarity of 0.894 between "Plastic barrel 200 L" and "Plastic barrels 200 liters", and 0.804 for "Plastic barrel 50 L". Even a close semantic match can refer to a different container size. Reconciliation requires exact extracted field values validated against order data. [BGE-M3 Model Card](https://huggingface.co/BAAI/bge-m3)

### Control Emails

Five anonymized text variants were tested independently against purchase order `PO-13`. Ground truth was labeled from the email text and source Excel workbook. Four fields per email were evaluated — quantity, unit, unit price, and total — including the expected absence of unit price in the third variant. Final status and proposed payable amount were also verified.

| Variant | Expected Result |
| --- | --- |
| "Shipped 4000 peice. Each — 4 dollars. Amount due — 16,000 dollars" | 4,000 pcs at $4. Ready for draft registry ($16,000) after confirmation. |
| "Shipped four berry pouches 500 g. Each — 4 dollars. Amount due — 16 dollars" | 4 pcs at $4. Ready for draft registry ($16) after confirmation. |
| First email with the unit-price sentence removed | Unit price missing. Manual review. |
| First email with a second purchase order number added | Manual review until order linkage is clarified. |
| First email stating "berry pouch 50 g" vs 500 g in the order | Manual review due to material specification mismatch. |

The rule-based parser routed all five emails to manual review. Latency measurements cover one model call on an Apple M5 with 16 GB RAM. This sample is illustrative for comparing options on known scenarios; evaluating production traffic requires a fresh email set with independent labeling.

## How to Estimate Impact for Stakeholders

During the pilot, measure handling time for one non-standard email manually versus with the model (including quote confirmation), then isolate the AI contribution:

```text
Hours per month = invoice count × share of non-standard emails × minutes saved / 60
Dollar impact   = hours × hourly labor rate − additional operating costs
```

With 160 invoices per month, 25% non-standard emails, and 3 minutes saved per email, the AI contribution is 2 hours per month. This is an example calculation; the actual share and time saved must be measured on the live process. Final ROI must include hardware and maintenance costs, while time saved by deterministic rule automation is accounted for separately.
