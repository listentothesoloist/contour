// Auto-generated data bundle for Case 04 (North Berry)
window.CASE04_DATA = {
  "items": [
    {
      "id": "E-01",
      "received_at": "09.11 15:40",
      "sender": "Timber Pallet Co., billing@timberpallet.example",
      "text": "Invoice 91 for pallets 1200x1000, 40 pcs at 1,100 USD. Total 44,000 USD. Reference: your order dated 05.11.",
      "supplier_name": "Timber Pallet Co.",
      "raw_invoice_no": "91",
      "canonical_invoice_no": "91",
      "order_id": "PO-10",
      "order": {
        "order_id": "PO-10",
        "order_date": "05.11.2026",
        "supplier": "Timber Pallet Co.",
        "supplier_clean": "timber pallet",
        "buyer": "Owen Miller",
        "material": "Wooden pallet 1200×1000",
        "unit": "pcs",
        "ordered_qty": 40.0,
        "accepted_qty": 40.0,
        "last_acceptance_date": "09.11.2026",
        "order_price": 1100.0,
        "approval_id": ""
      },
      "approval": null,
      "match_confidence": 1.0,
      "p1_reason": "Auto-linked without order ID to PO-10 by attributes (R-1): supplier Timber Pallet Co., material \"Wooden pallet 1200×1000\" (Synonym recognized (\"pallet\")), quantity 40 pcs, order date 05.11.2026",
      "raw_qty": 40.0,
      "raw_unit": "pcs",
      "raw_price": 1100.0,
      "converted_qty": 40.0,
      "converted_unit": "pcs",
      "converted_unit_price": 1100.0,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": 40.0,
      "stated_amount": 44000.0,
      "payable_amount": 44000.0,
      "prevented_risk": 0.0,
      "status_code": "READY_TO_PAY",
      "status_label": "Ready for draft registry",
      "status_color": "emerald",
      "risk_category": "none",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-6",
        "R-4",
        "R-5",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Auto-linked without order ID to PO-10 by attributes (R-1): supplier Timber Pallet Co., material \"Wooden pallet 1200×1000\" (Synonym recognized (\"pallet\")), quantity 40 pcs, order date 05.11.2026"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches Timber Pallet Co.. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"pallet\"). Invoice unit matches order unit: pcs."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "ok",
          "detail": "40 × 1100 = $44,000.00."
        },
        {
          "rule": "R-6 (Price & Quantity)",
          "status": "ok",
          "detail": "Price $1100/pcs, order limit 40 pcs. ERP purchase order terms apply."
        },
        {
          "rule": "R-4, R-5 (Receipt)",
          "status": "ok",
          "detail": "Available for this invoice: 40 pcs, required 40; previously billed 0. Prepayment not required."
        },
        {
          "rule": "R-9 (Payment Control)",
          "status": "warn",
          "detail": "Bank statement is not included in the export; explicit treasurer verification is required before payment."
        }
      ],
      "primary_reason": "Order, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $44,000.00. Bank statement and contract bank details check required.",
      "next_step": "Ask the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval.",
      "actions": [
        {
          "recipient_role": "Treasurer and CFO",
          "recipient_name": "Treasury / CFO",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-4, R-5, R-9",
          "subject": "Ready for draft registry: invoice No. 91, order PO-10",
          "body": "Hello team,\n\nEmail E-01 from Timber Pallet Co., received 09.11 15:40.\nInvoice No. 91, order PO-10.\nOrder, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $44,000.00. Bank statement and contract bank details check required.\n\nAsk the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval."
        }
      ]
    },
    {
      "id": "E-02",
      "received_at": "10.11 09:05",
      "sender": "PackLine Supply, invoice@packline.example",
      "text": "Invoice 202 under order PO-06: pouch 300 g, 5,000 pcs at 3.00 USD. Total 15,000 USD.",
      "supplier_name": "PackLine Supply",
      "raw_invoice_no": "202",
      "canonical_invoice_no": "202",
      "order_id": "PO-06",
      "order": {
        "order_id": "PO-06",
        "order_date": "02.11.2026",
        "supplier": "PackLine Supply",
        "supplier_clean": "packline supply",
        "buyer": "Anna Carter",
        "material": "Berry pouch 300 g",
        "unit": "pcs",
        "ordered_qty": 5000.0,
        "accepted_qty": 5000.0,
        "last_acceptance_date": "10.11.2026",
        "order_price": 3.0,
        "approval_id": ""
      },
      "approval": null,
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-06 in email text (R-1)",
      "raw_qty": 5000.0,
      "raw_unit": "pcs",
      "raw_price": 3.0,
      "converted_qty": 5000.0,
      "converted_unit": "pcs",
      "converted_unit_price": 3.0,
      "conversion_formula": null,
      "material_mapping": {
        "source": "pouch 300 g",
        "target": "berry pouch 300 g",
        "method": "rules"
      },
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": 5000.0,
      "stated_amount": 15000.0,
      "payable_amount": 15000.0,
      "prevented_risk": 0.0,
      "status_code": "READY_TO_PAY",
      "status_label": "Ready for draft registry",
      "status_color": "emerald",
      "risk_category": "none",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-6",
        "R-4",
        "R-5",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-06 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches PackLine Supply. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"berry pouch 300 g\"). Invoice unit matches order unit: pcs."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "ok",
          "detail": "5000 × 3 = $15,000.00."
        },
        {
          "rule": "R-6 (Price & Quantity)",
          "status": "ok",
          "detail": "Price $3/pcs, order limit 5000 pcs. ERP purchase order terms apply."
        },
        {
          "rule": "R-4, R-5 (Receipt)",
          "status": "ok",
          "detail": "Available for this invoice: 5000 pcs, required 5000; previously billed 0. Prepayment not required."
        },
        {
          "rule": "R-9 (Payment Control)",
          "status": "warn",
          "detail": "Bank statement is not included in the export; explicit treasurer verification is required before payment."
        }
      ],
      "primary_reason": "Order, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $15,000.00. Bank statement and contract bank details check required.",
      "next_step": "Ask the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval.",
      "actions": [
        {
          "recipient_role": "Treasurer and CFO",
          "recipient_name": "Treasury / CFO",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-4, R-5, R-9",
          "subject": "Ready for draft registry: invoice No. 202, order PO-06",
          "body": "Hello team,\n\nEmail E-02 from PackLine Supply, received 10.11 09:05.\nInvoice No. 202, order PO-06.\nOrder, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $15,000.00. Bank statement and contract bank details check required.\n\nAsk the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval."
        }
      ]
    },
    {
      "id": "E-03",
      "received_at": "10.11 11:30",
      "sender": "Ladoga Film Corp., sales@ladogafilm.example",
      "text": "Invoice 45 under PO-03: PE film 60 um, 10 kg, price 3,600 USD. Total 36,000 USD.",
      "supplier_name": "Ladoga Film Corp.",
      "raw_invoice_no": "45",
      "canonical_invoice_no": "45",
      "order_id": "PO-03",
      "order": {
        "order_id": "PO-03",
        "order_date": "02.11.2026",
        "supplier": "Ladoga Film Corp.",
        "supplier_clean": "ladoga film",
        "buyer": "Daniel Grant",
        "material": "PE film 60 um",
        "unit": "kg",
        "ordered_qty": 200.0,
        "accepted_qty": 200.0,
        "last_acceptance_date": "10.11.2026",
        "order_price": 180.0,
        "approval_id": ""
      },
      "approval": null,
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-03 in email text (R-1)",
      "raw_qty": 10.0,
      "raw_unit": "kg",
      "raw_price": 3600.0,
      "converted_qty": 10.0,
      "converted_unit": "kg",
      "converted_unit_price": 3600.0,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": null,
      "stated_amount": 36000.0,
      "payable_amount": 0.0,
      "prevented_risk": 36000.0,
      "status_code": "DUPLICATE_OR_REPLACED",
      "status_label": "Superseded by corrected (E-06)",
      "status_color": "amber",
      "risk_category": "duplicate",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-03 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches Ladoga Film Corp.. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Invoice Versions)",
          "status": "error",
          "detail": "Invoice No. 45 was superseded by a later corrected version E-06 (R-3)."
        }
      ],
      "primary_reason": "Invoice No. 45 was superseded by a later corrected version E-06 (R-3).",
      "next_step": "Archive this version. Reconcile the active revision E-06 separately.",
      "actions": []
    },
    {
      "id": "E-04",
      "received_at": "10.11 16:20",
      "sender": "TapeWorks Inc., billing@tapeworks.example",
      "text": "Invoice 45 under order PO-08, first batch: adhesive tape 48 mm × 66 m, 360 rolls at 95 USD. Total 34,200 USD.",
      "supplier_name": "TapeWorks Inc.",
      "raw_invoice_no": "45",
      "canonical_invoice_no": "45",
      "order_id": "PO-08",
      "order": {
        "order_id": "PO-08",
        "order_date": "03.11.2026",
        "supplier": "TapeWorks Inc.",
        "supplier_clean": "tapeworks",
        "buyer": "Daniel Grant",
        "material": "Packing adhesive tape 48 mm × 66 m",
        "unit": "roll",
        "ordered_qty": 600.0,
        "accepted_qty": 600.0,
        "last_acceptance_date": "14.11.2026",
        "order_price": 95.0,
        "approval_id": "AP-01"
      },
      "approval": {
        "exists": true,
        "approval_id": "AP-01",
        "order_id": "PO-08",
        "date": "06.11.2026",
        "summary": "Delivery in two batches: 360 rolls by 10.11, 240 rolls by 15.11. Price unchanged.",
        "status": "Signed",
        "signed_by": "Steven Parker",
        "is_signed": true,
        "new_price": null,
        "new_qty": null,
        "effective_from_str": null,
        "effective_from_ddmm": null,
        "is_split_batches": true,
        "batches": [
          360.0,
          240.0
        ],
        "is_delayed_rest": false
      },
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-08 in email text (R-1)",
      "raw_qty": 360.0,
      "raw_unit": "roll",
      "raw_price": 95.0,
      "converted_qty": 360.0,
      "converted_unit": "roll",
      "converted_unit_price": 95.0,
      "conversion_formula": null,
      "material_mapping": {
        "source": "adhesive tape",
        "target": "packing adhesive tape",
        "method": "rules"
      },
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": 600.0,
      "stated_amount": 34200.0,
      "payable_amount": 34200.0,
      "prevented_risk": 0.0,
      "status_code": "READY_TO_PAY",
      "status_label": "Ready for draft registry",
      "status_color": "emerald",
      "risk_category": "none",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-6",
        "R-4",
        "R-5",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-08 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches TapeWorks Inc.. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"adhesive tape\"). Invoice unit matches order unit: roll."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "ok",
          "detail": "360 × 95 = $34,200.00."
        },
        {
          "rule": "R-6 (Price & Quantity)",
          "status": "ok",
          "detail": "Price $95/roll, order limit 600 roll. AP-01: Signed."
        },
        {
          "rule": "R-4, R-5 (Receipt)",
          "status": "ok",
          "detail": "Available for this invoice: 600 roll, required 360; previously billed 0. Prepayment not required."
        },
        {
          "rule": "R-9 (Payment Control)",
          "status": "warn",
          "detail": "Bank statement is not included in the export; explicit treasurer verification is required before payment."
        }
      ],
      "primary_reason": "Order, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $34,200.00. Bank statement and contract bank details check required.",
      "next_step": "Ask the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval.",
      "actions": [
        {
          "recipient_role": "Treasurer and CFO",
          "recipient_name": "Treasury / CFO",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-4, R-5, R-9",
          "subject": "Ready for draft registry: invoice No. 45, order PO-08",
          "body": "Hello team,\n\nEmail E-04 from TapeWorks Inc., received 10.11 16:20.\nInvoice No. 45, order PO-08.\nOrder, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $34,200.00. Bank statement and contract bank details check required.\n\nAsk the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval."
        }
      ]
    },
    {
      "id": "E-05",
      "received_at": "11.11 10:00",
      "sender": "PackLine Supply, invoice@packline.example",
      "text": "Invoice 205 under PO-11: liner bag 600×800 mm, 2,000 pcs at 7.00 USD. Total 14,000 USD.",
      "supplier_name": "PackLine Supply",
      "raw_invoice_no": "205",
      "canonical_invoice_no": "205",
      "order_id": "PO-11",
      "order": {
        "order_id": "PO-11",
        "order_date": "04.11.2026",
        "supplier": "PackLine Supply",
        "supplier_clean": "packline supply",
        "buyer": "Anna Carter",
        "material": "PE liner bag 600×800 mm",
        "unit": "pcs",
        "ordered_qty": 2000.0,
        "accepted_qty": 2000.0,
        "last_acceptance_date": "11.11.2026",
        "order_price": 7.0,
        "approval_id": ""
      },
      "approval": null,
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-11 in email text (R-1)",
      "raw_qty": 2000.0,
      "raw_unit": "pcs",
      "raw_price": 7.0,
      "converted_qty": 2000.0,
      "converted_unit": "pcs",
      "converted_unit_price": 7.0,
      "conversion_formula": null,
      "material_mapping": {
        "source": "liner bag",
        "target": "pe liner bag",
        "method": "rules"
      },
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": 2000.0,
      "stated_amount": 14000.0,
      "payable_amount": 14000.0,
      "prevented_risk": 0.0,
      "status_code": "READY_TO_PAY",
      "status_label": "Ready for draft registry",
      "status_color": "emerald",
      "risk_category": "none",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-6",
        "R-4",
        "R-5",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-11 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches PackLine Supply. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"liner bag\"). Invoice unit matches order unit: pcs."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "ok",
          "detail": "2000 × 7 = $14,000.00."
        },
        {
          "rule": "R-6 (Price & Quantity)",
          "status": "ok",
          "detail": "Price $7/pcs, order limit 2000 pcs. ERP purchase order terms apply."
        },
        {
          "rule": "R-4, R-5 (Receipt)",
          "status": "ok",
          "detail": "Available for this invoice: 2000 pcs, required 2000; previously billed 0. Prepayment not required."
        },
        {
          "rule": "R-9 (Payment Control)",
          "status": "warn",
          "detail": "Bank statement is not included in the export; explicit treasurer verification is required before payment."
        }
      ],
      "primary_reason": "Order, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $14,000.00. Bank statement and contract bank details check required.",
      "next_step": "Ask the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval.",
      "actions": [
        {
          "recipient_role": "Treasurer and CFO",
          "recipient_name": "Treasury / CFO",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-4, R-5, R-9",
          "subject": "Ready for draft registry: invoice No. 205, order PO-11",
          "body": "Hello team,\n\nEmail E-05 from PackLine Supply, received 11.11 10:00.\nInvoice No. 205, order PO-11.\nOrder, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $14,000.00. Bank statement and contract bank details check required.\n\nAsk the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval."
        }
      ]
    },
    {
      "id": "E-06",
      "received_at": "11.11 14:45",
      "sender": "Ladoga Film Corp., sales@ladogafilm.example",
      "text": "Corrected invoice 45 under PO-03: PE film 60 um, 10 bags of 20 kg, bag price 3,600 USD. Total 36,000 USD. Previous version mistakenly printed 10 kg instead of 10 bags.",
      "supplier_name": "Ladoga Film Corp.",
      "raw_invoice_no": "45",
      "canonical_invoice_no": "45",
      "order_id": "PO-03",
      "order": {
        "order_id": "PO-03",
        "order_date": "02.11.2026",
        "supplier": "Ladoga Film Corp.",
        "supplier_clean": "ladoga film",
        "buyer": "Daniel Grant",
        "material": "PE film 60 um",
        "unit": "kg",
        "ordered_qty": 200.0,
        "accepted_qty": 200.0,
        "last_acceptance_date": "10.11.2026",
        "order_price": 180.0,
        "approval_id": ""
      },
      "approval": null,
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-03 in email text (R-1)",
      "raw_qty": 10.0,
      "raw_unit": "bags",
      "raw_price": 3600.0,
      "converted_qty": 200.0,
      "converted_unit": "kg",
      "converted_unit_price": 180.0,
      "conversion_formula": "10 bags × 20 kg = 200 kg; $3,600 / 20 = $180.00/kg",
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": 200.0,
      "stated_amount": 36000.0,
      "payable_amount": 36000.0,
      "prevented_risk": 0.0,
      "status_code": "READY_TO_PAY",
      "status_label": "Ready for draft registry",
      "status_color": "emerald",
      "risk_category": "none",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-6",
        "R-4",
        "R-5",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-03 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches Ladoga Film Corp.. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"pe film\"). 10 bags × 20 kg = 200 kg; $3,600 / 20 = $180.00/kg."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "ok",
          "detail": "10 × 3600 = $36,000.00."
        },
        {
          "rule": "R-6 (Price & Quantity)",
          "status": "ok",
          "detail": "Price $180/kg, order limit 200 kg. ERP purchase order terms apply."
        },
        {
          "rule": "R-4, R-5 (Receipt)",
          "status": "ok",
          "detail": "Available for this invoice: 200 kg, required 200; previously billed 0. Prepayment not required."
        },
        {
          "rule": "R-9 (Payment Control)",
          "status": "warn",
          "detail": "Bank statement is not included in the export; explicit treasurer verification is required before payment."
        }
      ],
      "primary_reason": "Order, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $36,000.00. Bank statement and contract bank details check required.",
      "next_step": "Ask the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval.",
      "actions": [
        {
          "recipient_role": "Treasurer and CFO",
          "recipient_name": "Treasury / CFO",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-4, R-5, R-9",
          "subject": "Ready for draft registry: invoice No. 45, order PO-03",
          "body": "Hello team,\n\nEmail E-06 from Ladoga Film Corp., received 11.11 14:45.\nInvoice No. 45, order PO-03.\nOrder, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $36,000.00. Bank statement and contract bank details check required.\n\nAsk the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval."
        }
      ]
    },
    {
      "id": "E-07",
      "received_at": "12.11 09:15",
      "sender": "Corrugated Box Center, sales@boxcenter.example",
      "text": "Invoice 116 under PO-01: 4-flap corrugated carton 400x300x250, 1,000 pcs at 40 USD. Total 40,000 USD.",
      "supplier_name": "Corrugated Box Center",
      "raw_invoice_no": "116",
      "canonical_invoice_no": "116",
      "order_id": "PO-01",
      "order": {
        "order_id": "PO-01",
        "order_date": "03.11.2026",
        "supplier": "Corrugated Box Center",
        "supplier_clean": "corrugated box center",
        "buyer": "Owen Miller",
        "material": "Shipping carton 400×300×250",
        "unit": "pcs",
        "ordered_qty": 1000.0,
        "accepted_qty": 800.0,
        "last_acceptance_date": "12.11.2026",
        "order_price": 40.0,
        "approval_id": "AP-03"
      },
      "approval": {
        "exists": true,
        "approval_id": "AP-03",
        "order_id": "PO-01",
        "date": "11.11.2026",
        "summary": "Supplier will deliver the remaining 200 cartons by 20.11.2026.",
        "status": "Signed",
        "signed_by": "Steven Parker",
        "is_signed": true,
        "new_price": null,
        "new_qty": null,
        "effective_from_str": null,
        "effective_from_ddmm": null,
        "is_split_batches": false,
        "batches": [],
        "is_delayed_rest": true
      },
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-01 in email text (R-1)",
      "raw_qty": 1000.0,
      "raw_unit": "pcs",
      "raw_price": 40.0,
      "converted_qty": 1000.0,
      "converted_unit": "pcs",
      "converted_unit_price": 40.0,
      "conversion_formula": null,
      "material_mapping": {
        "source": "corrugated carton",
        "target": "shipping carton",
        "method": "rules"
      },
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": 800.0,
      "stated_amount": 40000.0,
      "payable_amount": 0.0,
      "prevented_risk": 8000.0,
      "status_code": "NOT_ACCEPTED_YET",
      "status_label": "Insufficient confirmed receipt",
      "status_color": "blue",
      "risk_category": "unaccepted_goods",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-6",
        "R-4",
        "R-5",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-01 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches Corrugated Box Center. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"shipping carton\"). Invoice unit matches order unit: pcs."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "ok",
          "detail": "1000 × 40 = $40,000.00."
        },
        {
          "rule": "R-6 (Price & Quantity)",
          "status": "ok",
          "detail": "Price $40/pcs, order limit 1000 pcs. AP-03: Signed."
        },
        {
          "rule": "R-4, R-5 (Receipt & Prepayment)",
          "status": "warn",
          "detail": "Accepted on PO-01: 800 pcs; previously billed in active invoices 0 pcs. Available for invoice No. 116: 800 of 1000 pcs. Uncovered by receipt: 200 pcs ($8,000.00). Contract prepayment terms are absent from the export; neither payment nor final rejection can be prepared without them (R-4, R-5)."
        }
      ],
      "primary_reason": "Accepted on PO-01: 800 pcs; previously billed in active invoices 0 pcs. Available for invoice No. 116: 800 of 1000 pcs. Uncovered by receipt: 200 pcs ($8,000.00). Contract prepayment terms are absent from the export; neither payment nor final rejection can be prepared without them (R-4, R-5).",
      "next_step": "Request contract prepayment terms from the buyer and batch status from the warehouse. If post-receipt payment applies, confirm an invoice for the available 800 pcs ($32,000.00).",
      "actions": [
        {
          "recipient_role": "Buyer and Warehouse Manager",
          "recipient_name": "Owen Miller / Warehouse Manager",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-4, R-5, R-9",
          "subject": "Insufficient confirmed receipt: invoice No. 116, order PO-01",
          "body": "Hello team,\n\nEmail E-07 from Corrugated Box Center, received 12.11 09:15.\nInvoice No. 116, order PO-01.\nAccepted on PO-01: 800 pcs; previously billed in active invoices 0 pcs. Available for invoice No. 116: 800 of 1000 pcs. Uncovered by receipt: 200 pcs ($8,000.00). Contract prepayment terms are absent from the export; neither payment nor final rejection can be prepared without them (R-4, R-5).\n\nRequest contract prepayment terms from the buyer and batch status from the warehouse. If post-receipt payment applies, confirm an invoice for the available 800 pcs ($32,000.00)."
        }
      ]
    },
    {
      "id": "E-08",
      "received_at": "12.11 13:10",
      "sender": "PackLine Supply, invoice@packline.example",
      "text": "Invoice 201 under PO-02: berry pouch 1 kg, 10,000 pcs at 5.50 USD. Total 55,000 USD. Price per addendum dated 12.11.",
      "supplier_name": "PackLine Supply",
      "raw_invoice_no": "201",
      "canonical_invoice_no": "201",
      "order_id": "PO-02",
      "order": {
        "order_id": "PO-02",
        "order_date": "02.11.2026",
        "supplier": "PackLine Supply",
        "supplier_clean": "packline supply",
        "buyer": "Anna Carter",
        "material": "Berry pouch 1 kg",
        "unit": "pcs",
        "ordered_qty": 10000.0,
        "accepted_qty": 10000.0,
        "last_acceptance_date": "11.11.2026",
        "order_price": 5.0,
        "approval_id": "AP-04"
      },
      "approval": {
        "exists": true,
        "approval_id": "AP-04",
        "order_id": "PO-02",
        "date": "12.11.2026",
        "summary": "Berry pouch 1 kg price — 5.50 USD per piece instead of 5.00 USD for the entire order. Contract addendum dated 12.11.2026.",
        "status": "Signed",
        "signed_by": "Steven Parker",
        "is_signed": true,
        "new_price": 5.5,
        "new_qty": null,
        "effective_from_str": null,
        "effective_from_ddmm": null,
        "is_split_batches": false,
        "batches": [],
        "is_delayed_rest": false
      },
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-02 in email text (R-1)",
      "raw_qty": 10000.0,
      "raw_unit": "pcs",
      "raw_price": 5.5,
      "converted_qty": 10000.0,
      "converted_unit": "pcs",
      "converted_unit_price": 5.5,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": 10000.0,
      "stated_amount": 55000.0,
      "payable_amount": 55000.0,
      "prevented_risk": 0.0,
      "status_code": "READY_TO_PAY",
      "status_label": "Ready for draft registry",
      "status_color": "emerald",
      "risk_category": "none",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-6",
        "R-4",
        "R-5",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-02 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches PackLine Supply. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"berry pouch 1 kg\"). Invoice unit matches order unit: pcs."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "ok",
          "detail": "10000 × 5.5 = $55,000.00."
        },
        {
          "rule": "R-6 (Price & Quantity)",
          "status": "ok",
          "detail": "Price $5.5/pcs, order limit 10000 pcs. AP-04: Signed."
        },
        {
          "rule": "R-4, R-5 (Receipt)",
          "status": "ok",
          "detail": "Available for this invoice: 10000 pcs, required 10000; previously billed 0. Prepayment not required."
        },
        {
          "rule": "R-9 (Payment Control)",
          "status": "warn",
          "detail": "Bank statement is not included in the export; explicit treasurer verification is required before payment."
        }
      ],
      "primary_reason": "Order, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $55,000.00. Bank statement and contract bank details check required.",
      "next_step": "Ask the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval.",
      "actions": [
        {
          "recipient_role": "Treasurer and CFO",
          "recipient_name": "Treasury / CFO",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-4, R-5, R-9",
          "subject": "Ready for draft registry: invoice No. 201, order PO-02",
          "body": "Hello team,\n\nEmail E-08 from PackLine Supply, received 12.11 13:10.\nInvoice No. 201, order PO-02.\nOrder, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $55,000.00. Bank statement and contract bank details check required.\n\nAsk the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval."
        }
      ]
    },
    {
      "id": "E-09",
      "received_at": "12.11 16:05",
      "sender": "NordLabel Ltd., billing@nordlabel.example",
      "text": "Invoice 117 under PO-12: ribbon 110 mm × 300 m, 50 rolls at 650 USD. Total 32,500 USD.",
      "supplier_name": "NordLabel Ltd.",
      "raw_invoice_no": "117",
      "canonical_invoice_no": "117",
      "order_id": "PO-12",
      "order": {
        "order_id": "PO-12",
        "order_date": "03.11.2026",
        "supplier": "NordLabel Ltd.",
        "supplier_clean": "nordlabel",
        "buyer": "Anna Carter",
        "material": "Thermal transfer ribbon 110 mm × 300 m",
        "unit": "roll",
        "ordered_qty": 40.0,
        "accepted_qty": 50.0,
        "last_acceptance_date": "12.11.2026",
        "order_price": 650.0,
        "approval_id": "AP-02"
      },
      "approval": {
        "exists": true,
        "approval_id": "AP-02",
        "order_id": "PO-12",
        "date": "09.11.2026",
        "summary": "Quantity increased from 40 to 50 rolls, price 650 USD per roll unchanged.",
        "status": "Signed",
        "signed_by": "Steven Parker",
        "is_signed": true,
        "new_price": null,
        "new_qty": 50.0,
        "effective_from_str": null,
        "effective_from_ddmm": null,
        "is_split_batches": false,
        "batches": [],
        "is_delayed_rest": false
      },
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-12 in email text (R-1)",
      "raw_qty": 50.0,
      "raw_unit": "roll",
      "raw_price": 650.0,
      "converted_qty": 50.0,
      "converted_unit": "roll",
      "converted_unit_price": 650.0,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": 50.0,
      "stated_amount": 32500.0,
      "payable_amount": 32500.0,
      "prevented_risk": 0.0,
      "status_code": "READY_TO_PAY",
      "status_label": "Ready for draft registry",
      "status_color": "emerald",
      "risk_category": "none",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-6",
        "R-4",
        "R-5",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-12 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches NordLabel Ltd.. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"thermal transfer ribbon\"). Invoice unit matches order unit: roll."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "ok",
          "detail": "50 × 650 = $32,500.00."
        },
        {
          "rule": "R-6 (Price & Quantity)",
          "status": "ok",
          "detail": "Price $650/roll, order limit 50 roll. AP-02: Signed."
        },
        {
          "rule": "R-4, R-5 (Receipt)",
          "status": "ok",
          "detail": "Available for this invoice: 50 roll, required 50; previously billed 0. Prepayment not required."
        },
        {
          "rule": "R-9 (Payment Control)",
          "status": "warn",
          "detail": "Bank statement is not included in the export; explicit treasurer verification is required before payment."
        }
      ],
      "primary_reason": "Order, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $32,500.00. Bank statement and contract bank details check required.",
      "next_step": "Ask the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval.",
      "actions": [
        {
          "recipient_role": "Treasurer and CFO",
          "recipient_name": "Treasury / CFO",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-4, R-5, R-9",
          "subject": "Ready for draft registry: invoice No. 117, order PO-12",
          "body": "Hello team,\n\nEmail E-09 from NordLabel Ltd., received 12.11 16:05.\nInvoice No. 117, order PO-12.\nOrder, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $32,500.00. Bank statement and contract bank details check required.\n\nAsk the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval."
        }
      ]
    },
    {
      "id": "E-10",
      "received_at": "13.11 09:40",
      "sender": "Corrugated Box Center, sales@boxcenter.example",
      "text": "Invoice 117 under PO-04: cold-resistant label 58×40, 6,000 pcs at 2.20 USD. Total 13,200 USD. New price as discussed.",
      "supplier_name": "Corrugated Box Center",
      "raw_invoice_no": "117",
      "canonical_invoice_no": "117",
      "order_id": "PO-04",
      "order": {
        "order_id": "PO-04",
        "order_date": "04.11.2026",
        "supplier": "Corrugated Box Center",
        "supplier_clean": "corrugated box center",
        "buyer": "Owen Miller",
        "material": "Cold-resistant label 58×40 mm",
        "unit": "pcs",
        "ordered_qty": 6000.0,
        "accepted_qty": 6000.0,
        "last_acceptance_date": "12.11.2026",
        "order_price": 2.0,
        "approval_id": "AP-05"
      },
      "approval": {
        "exists": true,
        "approval_id": "AP-05",
        "order_id": "PO-04",
        "date": "13.11.2026",
        "summary": "Label price — 2.20 USD per piece instead of 2.00 USD.",
        "status": "Pending Signature",
        "signed_by": "",
        "is_signed": false,
        "new_price": 2.2,
        "new_qty": null,
        "effective_from_str": null,
        "effective_from_ddmm": null,
        "is_split_batches": false,
        "batches": [],
        "is_delayed_rest": false
      },
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-04 in email text (R-1)",
      "raw_qty": 6000.0,
      "raw_unit": "pcs",
      "raw_price": 2.2,
      "converted_qty": 6000.0,
      "converted_unit": "pcs",
      "converted_unit_price": 2.2,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": null,
      "stated_amount": 13200.0,
      "payable_amount": 0.0,
      "prevented_risk": 1200.0,
      "status_code": "PRICE_OR_QTY_UNAPPROVED",
      "status_label": "Unapproved price",
      "status_color": "orange",
      "risk_category": "unapproved_change",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-6",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-04 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches Corrugated Box Center. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"cold-resistant label\"). Invoice unit matches order unit: pcs."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "ok",
          "detail": "6000 × 2.2 = $13,200.00."
        },
        {
          "rule": "R-6 (Effective Price)",
          "status": "error",
          "detail": "Invoice price $2.2/pcs differs from effective price $2/pcs. AP-05: Pending Signature."
        }
      ],
      "primary_reason": "Invoice price $2.2/pcs differs from effective price $2/pcs. AP-05: Pending Signature.",
      "next_step": "Confirm price basis with buyer Owen Miller; request correction to $12,000.00 or a signed approval.",
      "actions": [
        {
          "recipient_role": "Buyer",
          "recipient_name": "Owen Miller",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-9",
          "subject": "Unapproved price: invoice No. 117, order PO-04",
          "body": "Hello team,\n\nEmail E-10 from Corrugated Box Center, received 13.11 09:40.\nInvoice No. 117, order PO-04.\nInvoice price $2.2/pcs differs from effective price $2/pcs. AP-05: Pending Signature.\n\nConfirm price basis with buyer Owen Miller; request correction to $12,000.00 or a signed approval."
        }
      ]
    },
    {
      "id": "E-11",
      "received_at": "13.11 11:25",
      "sender": "Owen Miller, buyer, o.miller@northberry.example",
      "text": "Regarding PO-04: we discussed raising the label price to 2.20 in chat with the supplier. The addendum is drafted in Directum, still awaiting the Supply Director's signature.",
      "supplier_name": "Owen Miller",
      "raw_invoice_no": "—",
      "canonical_invoice_no": "—",
      "order_id": "PO-04",
      "order": {
        "order_id": "PO-04",
        "order_date": "04.11.2026",
        "supplier": "Corrugated Box Center",
        "supplier_clean": "corrugated box center",
        "buyer": "Owen Miller",
        "material": "Cold-resistant label 58×40 mm",
        "unit": "pcs",
        "ordered_qty": 6000.0,
        "accepted_qty": 6000.0,
        "last_acceptance_date": "12.11.2026",
        "order_price": 2.0,
        "approval_id": "AP-05"
      },
      "approval": {
        "exists": true,
        "approval_id": "AP-05",
        "order_id": "PO-04",
        "date": "13.11.2026",
        "summary": "Label price — 2.20 USD per piece instead of 2.00 USD.",
        "status": "Pending Signature",
        "signed_by": "",
        "is_signed": false,
        "new_price": 2.2,
        "new_qty": null,
        "effective_from_str": null,
        "effective_from_ddmm": null,
        "is_split_batches": false,
        "batches": [],
        "is_delayed_rest": false
      },
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-04 in email text (R-1)",
      "raw_qty": null,
      "raw_unit": "",
      "raw_price": null,
      "converted_qty": null,
      "converted_unit": "",
      "converted_unit_price": null,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": null,
      "stated_amount": 0.0,
      "payable_amount": 0.0,
      "prevented_risk": 0.0,
      "status_code": "INFO_LETTER",
      "status_label": "Order information",
      "status_color": "slate",
      "risk_category": "none",
      "triggered_rules": [
        "R-1",
        "R-6"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-04 in email text (R-1)"
        },
        {
          "rule": "R-6 (Order Terms)",
          "status": "ok",
          "detail": "Approval AP-05: Pending Signature. Email correspondence does not modify order terms."
        }
      ],
      "primary_reason": "Informational email regarding PO-04. No new payable invoice created. Approval AP-05: Pending Signature. Email correspondence does not modify order terms.",
      "next_step": "Archive email under PO-04; confirm details with buyer Owen Miller.",
      "actions": []
    },
    {
      "id": "E-12",
      "received_at": "13.11 15:50",
      "sender": "NordLabel Ltd., billing@nordlabel.example",
      "text": "Invoice 118 under PO-07: thermal label 100×150, 10 rolls of 1,000 pcs, roll price 1,500 USD. Total 15,000 USD.",
      "supplier_name": "NordLabel Ltd.",
      "raw_invoice_no": "118",
      "canonical_invoice_no": "118",
      "order_id": "PO-07",
      "order": {
        "order_id": "PO-07",
        "order_date": "05.11.2026",
        "supplier": "NordLabel Ltd.",
        "supplier_clean": "nordlabel",
        "buyer": "Anna Carter",
        "material": "Thermal label 100×150 mm",
        "unit": "pcs",
        "ordered_qty": 12000.0,
        "accepted_qty": 10000.0,
        "last_acceptance_date": "13.11.2026",
        "order_price": 1.5,
        "approval_id": ""
      },
      "approval": null,
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-07 in email text (R-1)",
      "raw_qty": 10.0,
      "raw_unit": "rolls",
      "raw_price": 1500.0,
      "converted_qty": 10000.0,
      "converted_unit": "pcs",
      "converted_unit_price": 1.5,
      "conversion_formula": "10 rolls × 1000 pcs = 10000 pcs; $1,500 / 1000 = $1.50/pcs",
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": 10000.0,
      "stated_amount": 15000.0,
      "payable_amount": 15000.0,
      "prevented_risk": 0.0,
      "status_code": "READY_TO_PAY",
      "status_label": "Ready for draft registry",
      "status_color": "emerald",
      "risk_category": "none",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-6",
        "R-4",
        "R-5",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-07 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches NordLabel Ltd.. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"thermal label\"). 10 rolls × 1000 pcs = 10000 pcs; $1,500 / 1000 = $1.50/pcs."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "ok",
          "detail": "10 × 1500 = $15,000.00."
        },
        {
          "rule": "R-6 (Price & Quantity)",
          "status": "ok",
          "detail": "Price $1.5/pcs, order limit 12000 pcs. ERP purchase order terms apply."
        },
        {
          "rule": "R-4, R-5 (Receipt)",
          "status": "ok",
          "detail": "Available for this invoice: 10000 pcs, required 10000; previously billed 0. Prepayment not required."
        },
        {
          "rule": "R-9 (Payment Control)",
          "status": "warn",
          "detail": "Bank statement is not included in the export; explicit treasurer verification is required before payment."
        }
      ],
      "primary_reason": "Order, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $15,000.00. Bank statement and contract bank details check required.",
      "next_step": "Ask the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval.",
      "actions": [
        {
          "recipient_role": "Treasurer and CFO",
          "recipient_name": "Treasury / CFO",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-4, R-5, R-9",
          "subject": "Ready for draft registry: invoice No. 118, order PO-07",
          "body": "Hello team,\n\nEmail E-12 from NordLabel Ltd., received 13.11 15:50.\nInvoice No. 118, order PO-07.\nOrder, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $15,000.00. Bank statement and contract bank details check required.\n\nAsk the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval."
        }
      ]
    },
    {
      "id": "E-13",
      "received_at": "14.11 10:05",
      "sender": "Ladoga Film Corp., sales@ladogafilm.example",
      "text": "Invoice 48 under PO-09: stretch film 17 um, 300 kg at 225 USD. Total 67,500 USD. Price per new price list.",
      "supplier_name": "Ladoga Film Corp.",
      "raw_invoice_no": "48",
      "canonical_invoice_no": "48",
      "order_id": "PO-09",
      "order": {
        "order_id": "PO-09",
        "order_date": "05.11.2026",
        "supplier": "Ladoga Film Corp.",
        "supplier_clean": "ladoga film",
        "buyer": "Daniel Grant",
        "material": "Stretch film 17 um, 500 mm",
        "unit": "kg",
        "ordered_qty": 300.0,
        "accepted_qty": 300.0,
        "last_acceptance_date": "13.11.2026",
        "order_price": 210.0,
        "approval_id": "AP-06"
      },
      "approval": {
        "exists": true,
        "approval_id": "AP-06",
        "order_id": "PO-09",
        "date": "14.11.2026",
        "summary": "Stretch film price — 225 USD per kg instead of 210 USD for deliveries from 18.11.2026.",
        "status": "Signed",
        "signed_by": "Steven Parker",
        "is_signed": true,
        "new_price": 225.0,
        "new_qty": null,
        "effective_from_str": "18.11.2026",
        "effective_from_ddmm": [
          18,
          11
        ],
        "is_split_batches": false,
        "batches": [],
        "is_delayed_rest": false
      },
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-09 in email text (R-1)",
      "raw_qty": 300.0,
      "raw_unit": "kg",
      "raw_price": 225.0,
      "converted_qty": 300.0,
      "converted_unit": "kg",
      "converted_unit_price": 225.0,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": null,
      "stated_amount": 67500.0,
      "payable_amount": 0.0,
      "prevented_risk": 4500.0,
      "status_code": "PRICE_OR_QTY_UNAPPROVED",
      "status_label": "Unapproved price",
      "status_color": "orange",
      "risk_category": "unapproved_change",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-6",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-09 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches Ladoga Film Corp.. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"stretch film\"). Invoice unit matches order unit: kg."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "ok",
          "detail": "300 × 225 = $67,500.00."
        },
        {
          "rule": "R-6 (Effective Price)",
          "status": "error",
          "detail": "Invoice price $225/kg differs from effective price $210/kg. AP-06: Signed. Effective from 18.11.2026; receipt date 13.11.2026. Prior ERP terms apply to this delivery."
        }
      ],
      "primary_reason": "Invoice price $225/kg differs from effective price $210/kg. AP-06: Signed. Effective from 18.11.2026; receipt date 13.11.2026. Prior ERP terms apply to this delivery.",
      "next_step": "Confirm price basis with buyer Daniel Grant; request correction to $63,000.00 or a signed approval.",
      "actions": [
        {
          "recipient_role": "Buyer",
          "recipient_name": "Daniel Grant",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-9",
          "subject": "Unapproved price: invoice No. 48, order PO-09",
          "body": "Hello team,\n\nEmail E-13 from Ladoga Film Corp., received 14.11 10:05.\nInvoice No. 48, order PO-09.\nInvoice price $225/kg differs from effective price $210/kg. AP-06: Signed. Effective from 18.11.2026; receipt date 13.11.2026. Prior ERP terms apply to this delivery.\n\nConfirm price basis with buyer Daniel Grant; request correction to $63,000.00 or a signed approval."
        }
      ]
    },
    {
      "id": "E-14",
      "received_at": "14.11 12:30",
      "sender": "PackLine Supply, invoice@packline.example",
      "text": "Invoice No. 0202 under order PO-06: berry pouch 300 g, 5,000 pcs at 3 USD. Total 15,000 USD. Please pay by 18.11.",
      "supplier_name": "PackLine Supply",
      "raw_invoice_no": "0202",
      "canonical_invoice_no": "202",
      "order_id": "PO-06",
      "order": {
        "order_id": "PO-06",
        "order_date": "02.11.2026",
        "supplier": "PackLine Supply",
        "supplier_clean": "packline supply",
        "buyer": "Anna Carter",
        "material": "Berry pouch 300 g",
        "unit": "pcs",
        "ordered_qty": 5000.0,
        "accepted_qty": 5000.0,
        "last_acceptance_date": "10.11.2026",
        "order_price": 3.0,
        "approval_id": ""
      },
      "approval": null,
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-06 in email text (R-1)",
      "raw_qty": 5000.0,
      "raw_unit": "pcs",
      "raw_price": 3.0,
      "converted_qty": 5000.0,
      "converted_unit": "pcs",
      "converted_unit_price": 3.0,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": null,
      "stated_amount": 15000.0,
      "payable_amount": 0.0,
      "prevented_risk": 15000.0,
      "status_code": "DUPLICATE_OR_REPLACED",
      "status_label": "Duplicate invoice (E-02)",
      "status_color": "amber",
      "risk_category": "duplicate",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-06 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches PackLine Supply. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Duplicates)",
          "status": "error",
          "detail": "Invoice No. 0202 (normalized 202) duplicates document E-02 from the same supplier (R-3)."
        }
      ],
      "primary_reason": "Invoice No. 0202 (normalized 202) duplicates document E-02 from the same supplier (R-3).",
      "next_step": "Exclude duplicate from payment registry. Check bank statement for payment status of E-02.",
      "actions": [
        {
          "recipient_role": "Treasurer",
          "recipient_name": "Treasury",
          "rule_ref": "R-1, R-2, R-3, R-9",
          "subject": "Duplicate invoice (E-02): invoice No. 0202, order PO-06",
          "body": "Hello team,\n\nEmail E-14 from PackLine Supply, received 14.11 12:30.\nInvoice No. 0202, order PO-06.\nInvoice No. 0202 (normalized 202) duplicates document E-02 from the same supplier (R-3).\n\nExclude duplicate from payment registry. Check bank statement for payment status of E-02."
        }
      ]
    },
    {
      "id": "E-15",
      "received_at": "14.11 17:10",
      "sender": "TapeWorks Inc., billing@tapeworks.example",
      "text": "Invoice 52 under PO-08, second batch: adhesive tape 48 mm × 66 m, 240 rolls at 95 USD. Total 23,800 USD.",
      "supplier_name": "TapeWorks Inc.",
      "raw_invoice_no": "52",
      "canonical_invoice_no": "52",
      "order_id": "PO-08",
      "order": {
        "order_id": "PO-08",
        "order_date": "03.11.2026",
        "supplier": "TapeWorks Inc.",
        "supplier_clean": "tapeworks",
        "buyer": "Daniel Grant",
        "material": "Packing adhesive tape 48 mm × 66 m",
        "unit": "roll",
        "ordered_qty": 600.0,
        "accepted_qty": 600.0,
        "last_acceptance_date": "14.11.2026",
        "order_price": 95.0,
        "approval_id": "AP-01"
      },
      "approval": {
        "exists": true,
        "approval_id": "AP-01",
        "order_id": "PO-08",
        "date": "06.11.2026",
        "summary": "Delivery in two batches: 360 rolls by 10.11, 240 rolls by 15.11. Price unchanged.",
        "status": "Signed",
        "signed_by": "Steven Parker",
        "is_signed": true,
        "new_price": null,
        "new_qty": null,
        "effective_from_str": null,
        "effective_from_ddmm": null,
        "is_split_batches": true,
        "batches": [
          360.0,
          240.0
        ],
        "is_delayed_rest": false
      },
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-08 in email text (R-1)",
      "raw_qty": 240.0,
      "raw_unit": "roll",
      "raw_price": 95.0,
      "converted_qty": 240.0,
      "converted_unit": "roll",
      "converted_unit_price": 95.0,
      "conversion_formula": null,
      "material_mapping": {
        "source": "adhesive tape",
        "target": "packing adhesive tape",
        "method": "rules"
      },
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": null,
      "stated_amount": 23800.0,
      "payable_amount": 0.0,
      "prevented_risk": 1000.0,
      "status_code": "MATH_ERROR",
      "status_label": "Invoice arithmetic error",
      "status_color": "purple",
      "risk_category": "math_error",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-08 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches TapeWorks Inc.. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"adhesive tape\"). Invoice unit matches order unit: roll."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "error",
          "detail": "Invoice No. 52: 240 × 95 = $22,800.00; stated $23,800.00. Variance +1,000.00 USD."
        }
      ],
      "primary_reason": "Invoice No. 52: 240 × 95 = $22,800.00; stated $23,800.00. Variance +1,000.00 USD.",
      "next_step": "Request a corrected invoice No. 52 from the supplier for $22,800.00.",
      "actions": [
        {
          "recipient_role": "Supplier",
          "recipient_name": "TapeWorks Inc.",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-9",
          "subject": "Invoice arithmetic error: invoice No. 52, order PO-08",
          "body": "Hello team,\n\nEmail E-15 from TapeWorks Inc., received 14.11 17:10.\nInvoice No. 52, order PO-08.\nInvoice No. 52: 240 × 95 = $22,800.00; stated $23,800.00. Variance +1,000.00 USD.\n\nRequest a corrected invoice No. 52 from the supplier for $22,800.00."
        }
      ]
    },
    {
      "id": "E-16",
      "received_at": "15.11 10:30",
      "sender": "Corrugated Box Center Plus, billing@boxcenter-plus.example",
      "text": "Invoice 116: cartons 1,000 pcs at 40 USD. Total 40,000 USD. We now invoice from another company, please pay using the new bank details.",
      "supplier_name": "Corrugated Box Center Plus",
      "raw_invoice_no": "116",
      "canonical_invoice_no": "116",
      "order_id": "PO-01",
      "order": {
        "order_id": "PO-01",
        "order_date": "03.11.2026",
        "supplier": "Corrugated Box Center",
        "supplier_clean": "corrugated box center",
        "buyer": "Owen Miller",
        "material": "Shipping carton 400×300×250",
        "unit": "pcs",
        "ordered_qty": 1000.0,
        "accepted_qty": 800.0,
        "last_acceptance_date": "12.11.2026",
        "order_price": 40.0,
        "approval_id": "AP-03"
      },
      "approval": {
        "exists": true,
        "approval_id": "AP-03",
        "order_id": "PO-01",
        "date": "11.11.2026",
        "summary": "Supplier will deliver the remaining 200 cartons by 20.11.2026.",
        "status": "Signed",
        "signed_by": "Steven Parker",
        "is_signed": true,
        "new_price": null,
        "new_qty": null,
        "effective_from_str": null,
        "effective_from_ddmm": null,
        "is_split_batches": false,
        "batches": [],
        "is_delayed_rest": true
      },
      "match_confidence": 0.92,
      "p1_reason": "Linked to PO-01 by base supplier match, invoice No. 116, material, and quantity (R-1, R-2)",
      "raw_qty": 1000.0,
      "raw_unit": "pcs",
      "raw_price": 40.0,
      "converted_qty": 1000.0,
      "converted_unit": "pcs",
      "converted_unit_price": 40.0,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": null,
      "stated_amount": 40000.0,
      "payable_amount": 0.0,
      "prevented_risk": 40000.0,
      "status_code": "CRITICAL_REQUISITES",
      "status_label": "Verify recipient and bank details",
      "status_color": "rose",
      "risk_category": "requisites",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Linked to PO-01 by base supplier match, invoice No. 116, material, and quantity (R-1, R-2)"
        },
        {
          "rule": "R-2 (Supplier & Bank Details)",
          "status": "error",
          "detail": "Order PO-01 lists supplier Corrugated Box Center; email sender is Corrugated Box Center Plus. Payment recipient and bank details in the email cannot be verified from the provided export. No signed amendment authorizing this change was found (R-2)."
        }
      ],
      "primary_reason": "Order PO-01 lists supplier Corrugated Box Center; email sender is Corrugated Box Center Plus. Payment recipient and bank details in the email cannot be verified from the provided export. No signed amendment authorizing this change was found (R-2).",
      "next_step": "Hold payment preparation; verify the contract and signed addendum in Directum RX.",
      "actions": [
        {
          "recipient_role": "Buyer and CFO",
          "recipient_name": "Owen Miller / CFO",
          "rule_ref": "R-1, R-2, R-9",
          "subject": "Verify recipient and bank details: invoice No. 116, order PO-01",
          "body": "Hello team,\n\nEmail E-16 from Corrugated Box Center Plus, received 15.11 10:30.\nInvoice No. 116, order PO-01.\nOrder PO-01 lists supplier Corrugated Box Center; email sender is Corrugated Box Center Plus. Payment recipient and bank details in the email cannot be verified from the provided export. No signed amendment authorizing this change was found (R-2).\n\nHold payment preparation; verify the contract and signed addendum in Directum RX."
        }
      ]
    },
    {
      "id": "E-17",
      "received_at": "15.11 12:00",
      "sender": "Timber Pallet Co., billing@timberpallet.example",
      "text": "Invoice 88 under PO-05: pallets 1200x800, 80 pcs at 900 USD. Total 72,000 USD.",
      "supplier_name": "Timber Pallet Co.",
      "raw_invoice_no": "88",
      "canonical_invoice_no": "88",
      "order_id": "PO-05",
      "order": {
        "order_id": "PO-05",
        "order_date": "06.11.2026",
        "supplier": "Timber Pallet Co.",
        "supplier_clean": "timber pallet",
        "buyer": "Owen Miller",
        "material": "Wooden pallet 1200×800",
        "unit": "pcs",
        "ordered_qty": 80.0,
        "accepted_qty": 0.0,
        "last_acceptance_date": "",
        "order_price": 900.0,
        "approval_id": ""
      },
      "approval": null,
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-05 in email text (R-1)",
      "raw_qty": 80.0,
      "raw_unit": "pcs",
      "raw_price": 900.0,
      "converted_qty": 80.0,
      "converted_unit": "pcs",
      "converted_unit_price": 900.0,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": 0.0,
      "stated_amount": 72000.0,
      "payable_amount": 0.0,
      "prevented_risk": 72000.0,
      "status_code": "NOT_ACCEPTED_YET",
      "status_label": "Insufficient confirmed receipt",
      "status_color": "blue",
      "risk_category": "unaccepted_goods",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-6",
        "R-4",
        "R-5",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-05 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches Timber Pallet Co.. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"pallet\"). Invoice unit matches order unit: pcs."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "ok",
          "detail": "80 × 900 = $72,000.00."
        },
        {
          "rule": "R-6 (Price & Quantity)",
          "status": "ok",
          "detail": "Price $900/pcs, order limit 80 pcs. ERP purchase order terms apply."
        },
        {
          "rule": "R-4, R-5 (Receipt & Prepayment)",
          "status": "warn",
          "detail": "Accepted on PO-05: 0 pcs; previously billed in active invoices 0 pcs. Available for invoice No. 88: 0 of 80 pcs. Uncovered by receipt: 80 pcs ($72,000.00). Contract prepayment terms are absent from the export; neither payment nor final rejection can be prepared without them (R-4, R-5)."
        }
      ],
      "primary_reason": "Accepted on PO-05: 0 pcs; previously billed in active invoices 0 pcs. Available for invoice No. 88: 0 of 80 pcs. Uncovered by receipt: 80 pcs ($72,000.00). Contract prepayment terms are absent from the export; neither payment nor final rejection can be prepared without them (R-4, R-5).",
      "next_step": "Request contract prepayment terms from the buyer and batch status from the warehouse. If prepayment is not stipulated, wait for the new batch receipt to be posted.",
      "actions": [
        {
          "recipient_role": "Buyer and Warehouse Manager",
          "recipient_name": "Owen Miller / Warehouse Manager",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-4, R-5, R-9",
          "subject": "Insufficient confirmed receipt: invoice No. 88, order PO-05",
          "body": "Hello team,\n\nEmail E-17 from Timber Pallet Co., received 15.11 12:00.\nInvoice No. 88, order PO-05.\nAccepted on PO-05: 0 pcs; previously billed in active invoices 0 pcs. Available for invoice No. 88: 0 of 80 pcs. Uncovered by receipt: 80 pcs ($72,000.00). Contract prepayment terms are absent from the export; neither payment nor final rejection can be prepared without them (R-4, R-5).\n\nRequest contract prepayment terms from the buyer and batch status from the warehouse. If prepayment is not stipulated, wait for the new batch receipt to be posted."
        }
      ]
    },
    {
      "id": "E-18",
      "received_at": "16.11 09:20",
      "sender": "Corrugated Box Center, sales@boxcenter.example",
      "text": "Resending invoice 116 under PO-01 for 40,000 USD. Please confirm the payment date.",
      "supplier_name": "Corrugated Box Center",
      "raw_invoice_no": "116",
      "canonical_invoice_no": "116",
      "order_id": "PO-01",
      "order": {
        "order_id": "PO-01",
        "order_date": "03.11.2026",
        "supplier": "Corrugated Box Center",
        "supplier_clean": "corrugated box center",
        "buyer": "Owen Miller",
        "material": "Shipping carton 400×300×250",
        "unit": "pcs",
        "ordered_qty": 1000.0,
        "accepted_qty": 800.0,
        "last_acceptance_date": "12.11.2026",
        "order_price": 40.0,
        "approval_id": "AP-03"
      },
      "approval": {
        "exists": true,
        "approval_id": "AP-03",
        "order_id": "PO-01",
        "date": "11.11.2026",
        "summary": "Supplier will deliver the remaining 200 cartons by 20.11.2026.",
        "status": "Signed",
        "signed_by": "Steven Parker",
        "is_signed": true,
        "new_price": null,
        "new_qty": null,
        "effective_from_str": null,
        "effective_from_ddmm": null,
        "is_split_batches": false,
        "batches": [],
        "is_delayed_rest": true
      },
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-01 in email text (R-1)",
      "raw_qty": null,
      "raw_unit": "",
      "raw_price": null,
      "converted_qty": null,
      "converted_unit": "",
      "converted_unit_price": null,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": null,
      "stated_amount": 40000.0,
      "payable_amount": 0.0,
      "prevented_risk": 40000.0,
      "status_code": "DUPLICATE_OR_REPLACED",
      "status_label": "Duplicate invoice (E-07)",
      "status_color": "amber",
      "risk_category": "duplicate",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-01 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches Corrugated Box Center. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Duplicates)",
          "status": "error",
          "detail": "Invoice No. 116 (normalized 116) duplicates document E-07 from the same supplier (R-3)."
        }
      ],
      "primary_reason": "Invoice No. 116 (normalized 116) duplicates document E-07 from the same supplier (R-3).",
      "next_step": "Exclude duplicate from payment registry. Check bank statement for payment status of E-07.",
      "actions": [
        {
          "recipient_role": "Treasurer",
          "recipient_name": "Treasury",
          "rule_ref": "R-1, R-2, R-3, R-9",
          "subject": "Duplicate invoice (E-07): invoice No. 116, order PO-01",
          "body": "Hello team,\n\nEmail E-18 from Corrugated Box Center, received 16.11 09:20.\nInvoice No. 116, order PO-01.\nInvoice No. 116 (normalized 116) duplicates document E-07 from the same supplier (R-3).\n\nExclude duplicate from payment registry. Check bank statement for payment status of E-07."
        }
      ]
    },
    {
      "id": "E-19",
      "received_at": "16.11 10:15",
      "sender": "Timber Pallet Co., billing@timberpallet.example",
      "text": "Regarding invoice 88: we will deliver the pallets today after 17:00. Please include the invoice in the next payment registry.",
      "supplier_name": "Timber Pallet Co.",
      "raw_invoice_no": "88",
      "canonical_invoice_no": "88",
      "order_id": "PO-05",
      "order": {
        "order_id": "PO-05",
        "order_date": "06.11.2026",
        "supplier": "Timber Pallet Co.",
        "supplier_clean": "timber pallet",
        "buyer": "Owen Miller",
        "material": "Wooden pallet 1200×800",
        "unit": "pcs",
        "ordered_qty": 80.0,
        "accepted_qty": 0.0,
        "last_acceptance_date": "",
        "order_price": 900.0,
        "approval_id": ""
      },
      "approval": null,
      "match_confidence": 0.98,
      "p1_reason": "Linked to PO-05 via previously recorded invoice No. 88 from Timber Pallet Co. (R-1)",
      "raw_qty": null,
      "raw_unit": "",
      "raw_price": null,
      "converted_qty": null,
      "converted_unit": "",
      "converted_unit_price": null,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": null,
      "stated_amount": 0.0,
      "payable_amount": 0.0,
      "prevented_risk": 0.0,
      "status_code": "INFO_LETTER",
      "status_label": "Order information",
      "status_color": "slate",
      "risk_category": "none",
      "triggered_rules": [
        "R-1",
        "R-6"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Linked to PO-05 via previously recorded invoice No. 88 from Timber Pallet Co. (R-1)"
        },
        {
          "rule": "R-6 (Order Terms)",
          "status": "ok",
          "detail": "No signed order amendments in the export. Correspondence does not confirm warehouse receipt."
        }
      ],
      "primary_reason": "Informational email regarding PO-05. No new payable invoice created. No signed order amendments in the export. Correspondence does not confirm warehouse receipt.",
      "next_step": "Archive email under PO-05; confirm details with buyer Owen Miller.",
      "actions": []
    },
    {
      "id": "E-20",
      "received_at": "16.11 11:05",
      "sender": "NordLabel Ltd., billing@nordlabel.example",
      "text": "Regarding PO-07: we will ship the remaining 2 rolls of thermal labels on 19.11 and issue the invoice after dispatch.",
      "supplier_name": "NordLabel Ltd.",
      "raw_invoice_no": "—",
      "canonical_invoice_no": "—",
      "order_id": "PO-07",
      "order": {
        "order_id": "PO-07",
        "order_date": "05.11.2026",
        "supplier": "NordLabel Ltd.",
        "supplier_clean": "nordlabel",
        "buyer": "Anna Carter",
        "material": "Thermal label 100×150 mm",
        "unit": "pcs",
        "ordered_qty": 12000.0,
        "accepted_qty": 10000.0,
        "last_acceptance_date": "13.11.2026",
        "order_price": 1.5,
        "approval_id": ""
      },
      "approval": null,
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-07 in email text (R-1)",
      "raw_qty": null,
      "raw_unit": "",
      "raw_price": null,
      "converted_qty": null,
      "converted_unit": "",
      "converted_unit_price": null,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": null,
      "stated_amount": 0.0,
      "payable_amount": 0.0,
      "prevented_risk": 0.0,
      "status_code": "INFO_LETTER",
      "status_label": "Order information",
      "status_color": "slate",
      "risk_category": "none",
      "triggered_rules": [
        "R-1",
        "R-6"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-07 in email text (R-1)"
        },
        {
          "rule": "R-6 (Order Terms)",
          "status": "ok",
          "detail": "No signed order amendments in the export. Correspondence does not confirm warehouse receipt."
        }
      ],
      "primary_reason": "Informational email regarding PO-07. No new payable invoice created. No signed order amendments in the export. Correspondence does not confirm warehouse receipt.",
      "next_step": "Archive email under PO-07; confirm details with buyer Anna Carter.",
      "actions": []
    },
    {
      "id": "E-21",
      "received_at": "16.11 11:15",
      "sender": "PackLine Supply, invoice@packline.example",
      "text": "Invoice 210 under PO-13: berry pouch 500 g, 4,000 pcs at 4.40 USD. Total 17,600 USD. Price per addendum dated 12.11.",
      "supplier_name": "PackLine Supply",
      "raw_invoice_no": "210",
      "canonical_invoice_no": "210",
      "order_id": "PO-13",
      "order": {
        "order_id": "PO-13",
        "order_date": "06.11.2026",
        "supplier": "PackLine Supply",
        "supplier_clean": "packline supply",
        "buyer": "Anna Carter",
        "material": "Berry pouch 500 g",
        "unit": "pcs",
        "ordered_qty": 4000.0,
        "accepted_qty": 4000.0,
        "last_acceptance_date": "13.11.2026",
        "order_price": 4.0,
        "approval_id": ""
      },
      "approval": null,
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-13 in email text (R-1)",
      "raw_qty": 4000.0,
      "raw_unit": "pcs",
      "raw_price": 4.4,
      "converted_qty": 4000.0,
      "converted_unit": "pcs",
      "converted_unit_price": 4.4,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": null,
      "stated_amount": 17600.0,
      "payable_amount": 0.0,
      "prevented_risk": 1600.0,
      "status_code": "PRICE_OR_QTY_UNAPPROVED",
      "status_label": "Unapproved price",
      "status_color": "orange",
      "risk_category": "unapproved_change",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-6",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-13 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches PackLine Supply. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"berry pouch 500 g\"). Invoice unit matches order unit: pcs."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "ok",
          "detail": "4000 × 4.4 = $17,600.00."
        },
        {
          "rule": "R-6 (Effective Price)",
          "status": "error",
          "detail": "Invoice price $4.4/pcs differs from effective price $4/pcs. ERP purchase order terms apply."
        }
      ],
      "primary_reason": "Invoice price $4.4/pcs differs from effective price $4/pcs. ERP purchase order terms apply.",
      "next_step": "Confirm price basis with buyer Anna Carter; request correction to $16,000.00 or a signed approval.",
      "actions": [
        {
          "recipient_role": "Buyer",
          "recipient_name": "Anna Carter",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-9",
          "subject": "Unapproved price: invoice No. 210, order PO-13",
          "body": "Hello team,\n\nEmail E-21 from PackLine Supply, received 16.11 11:15.\nInvoice No. 210, order PO-13.\nInvoice price $4.4/pcs differs from effective price $4/pcs. ERP purchase order terms apply.\n\nConfirm price basis with buyer Anna Carter; request correction to $16,000.00 or a signed approval."
        }
      ]
    },
    {
      "id": "E-22",
      "received_at": "16.11 11:25",
      "sender": "NordLabel Ltd., billing@nordlabel.example",
      "text": "Invoice 117/1 under PO-12: ribbon 110 mm × 300 m, 50 rolls at 650 USD. Total 32,500 USD.",
      "supplier_name": "NordLabel Ltd.",
      "raw_invoice_no": "117/1",
      "canonical_invoice_no": "117",
      "order_id": "PO-12",
      "order": {
        "order_id": "PO-12",
        "order_date": "03.11.2026",
        "supplier": "NordLabel Ltd.",
        "supplier_clean": "nordlabel",
        "buyer": "Anna Carter",
        "material": "Thermal transfer ribbon 110 mm × 300 m",
        "unit": "roll",
        "ordered_qty": 40.0,
        "accepted_qty": 50.0,
        "last_acceptance_date": "12.11.2026",
        "order_price": 650.0,
        "approval_id": "AP-02"
      },
      "approval": {
        "exists": true,
        "approval_id": "AP-02",
        "order_id": "PO-12",
        "date": "09.11.2026",
        "summary": "Quantity increased from 40 to 50 rolls, price 650 USD per roll unchanged.",
        "status": "Signed",
        "signed_by": "Steven Parker",
        "is_signed": true,
        "new_price": null,
        "new_qty": 50.0,
        "effective_from_str": null,
        "effective_from_ddmm": null,
        "is_split_batches": false,
        "batches": [],
        "is_delayed_rest": false
      },
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-12 in email text (R-1)",
      "raw_qty": 50.0,
      "raw_unit": "roll",
      "raw_price": 650.0,
      "converted_qty": 50.0,
      "converted_unit": "roll",
      "converted_unit_price": 650.0,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": null,
      "stated_amount": 32500.0,
      "payable_amount": 0.0,
      "prevented_risk": 32500.0,
      "status_code": "DUPLICATE_OR_REPLACED",
      "status_label": "Duplicate invoice (E-09)",
      "status_color": "amber",
      "risk_category": "duplicate",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-12 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches NordLabel Ltd.. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Duplicates)",
          "status": "error",
          "detail": "Invoice No. 117/1 (normalized 117) duplicates document E-09 from the same supplier (R-3)."
        }
      ],
      "primary_reason": "Invoice No. 117/1 (normalized 117) duplicates document E-09 from the same supplier (R-3).",
      "next_step": "Exclude duplicate from payment registry. Check bank statement for payment status of E-09.",
      "actions": [
        {
          "recipient_role": "Treasurer",
          "recipient_name": "Treasury",
          "rule_ref": "R-1, R-2, R-3, R-9",
          "subject": "Duplicate invoice (E-09): invoice No. 117/1, order PO-12",
          "body": "Hello team,\n\nEmail E-22 from NordLabel Ltd., received 16.11 11:25.\nInvoice No. 117/1, order PO-12.\nInvoice No. 117/1 (normalized 117) duplicates document E-09 from the same supplier (R-3).\n\nExclude duplicate from payment registry. Check bank statement for payment status of E-09."
        }
      ]
    },
    {
      "id": "E-23",
      "received_at": "16.11 11:35",
      "sender": "Corrugated Box Center, sales@boxcenter.example",
      "text": "Invoice 121 under PO-01: 4-flap corrugated carton 400x300x250, remaining 200 pcs at 40 USD. Total 8,000 USD. Will deliver by 20.11.",
      "supplier_name": "Corrugated Box Center",
      "raw_invoice_no": "121",
      "canonical_invoice_no": "121",
      "order_id": "PO-01",
      "order": {
        "order_id": "PO-01",
        "order_date": "03.11.2026",
        "supplier": "Corrugated Box Center",
        "supplier_clean": "corrugated box center",
        "buyer": "Owen Miller",
        "material": "Shipping carton 400×300×250",
        "unit": "pcs",
        "ordered_qty": 1000.0,
        "accepted_qty": 800.0,
        "last_acceptance_date": "12.11.2026",
        "order_price": 40.0,
        "approval_id": "AP-03"
      },
      "approval": {
        "exists": true,
        "approval_id": "AP-03",
        "order_id": "PO-01",
        "date": "11.11.2026",
        "summary": "Supplier will deliver the remaining 200 cartons by 20.11.2026.",
        "status": "Signed",
        "signed_by": "Steven Parker",
        "is_signed": true,
        "new_price": null,
        "new_qty": null,
        "effective_from_str": null,
        "effective_from_ddmm": null,
        "is_split_batches": false,
        "batches": [],
        "is_delayed_rest": true
      },
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-01 in email text (R-1)",
      "raw_qty": 200.0,
      "raw_unit": "pcs",
      "raw_price": 40.0,
      "converted_qty": 200.0,
      "converted_unit": "pcs",
      "converted_unit_price": 40.0,
      "conversion_formula": null,
      "material_mapping": {
        "source": "corrugated carton",
        "target": "shipping carton",
        "method": "rules"
      },
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": null,
      "stated_amount": 8000.0,
      "payable_amount": 0.0,
      "prevented_risk": 8000.0,
      "status_code": "DUPLICATE_OR_REPLACED",
      "status_label": "Order volume billed twice",
      "status_color": "amber",
      "risk_category": "duplicate",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-6",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-01 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches Corrugated Box Center. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"shipping carton\"). Invoice unit matches order unit: pcs."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "ok",
          "detail": "200 × 40 = $8,000.00."
        },
        {
          "rule": "R-6 (Price & Quantity)",
          "status": "ok",
          "detail": "Price $40/pcs, order limit 1000 pcs. AP-03: Signed."
        },
        {
          "rule": "R-3 (Duplicate Order Volume)",
          "status": "error",
          "detail": "Order PO-01 already has 1000 pcs billed in active invoices E-07. Invoice No. 121 adds 200 pcs: 1200 total vs 1000 pcs approved."
        }
      ],
      "primary_reason": "Order PO-01 already has 1000 pcs billed in active invoices E-07. Invoice No. 121 adds 200 pcs: 1200 total vs 1000 pcs approved.",
      "next_step": "Confirm with the supplier which invoices are superseded and which batches they cover; do not include duplicate volume in the registry.",
      "actions": [
        {
          "recipient_role": "Supplier and Buyer",
          "recipient_name": "Corrugated Box Center / Owen Miller",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-9",
          "subject": "Order volume billed twice: invoice No. 121, order PO-01",
          "body": "Hello team,\n\nEmail E-23 from Corrugated Box Center, received 16.11 11:35.\nInvoice No. 121, order PO-01.\nOrder PO-01 already has 1000 pcs billed in active invoices E-07. Invoice No. 121 adds 200 pcs: 1200 total vs 1000 pcs approved.\n\nConfirm with the supplier which invoices are superseded and which batches they cover; do not include duplicate volume in the registry."
        }
      ]
    },
    {
      "id": "E-24",
      "received_at": "16.11 11:45",
      "sender": "Cardboard Service LLC, billing@cardboardservice.example",
      "text": "Invoice 33 under PO-14: cardboard pad 1200x800, 540 pcs at 12 USD. Total 6,480 USD. Shipped extra quantity as buffer.",
      "supplier_name": "Cardboard Service LLC",
      "raw_invoice_no": "33",
      "canonical_invoice_no": "33",
      "order_id": "PO-14",
      "order": {
        "order_id": "PO-14",
        "order_date": "05.11.2026",
        "supplier": "Cardboard Service LLC",
        "supplier_clean": "cardboard service",
        "buyer": "Owen Miller",
        "material": "Cardboard pad 1200×800",
        "unit": "pcs",
        "ordered_qty": 500.0,
        "accepted_qty": 540.0,
        "last_acceptance_date": "12.11.2026",
        "order_price": 12.0,
        "approval_id": ""
      },
      "approval": null,
      "match_confidence": 1.0,
      "p1_reason": "Direct link via purchase order PO-14 in email text (R-1)",
      "raw_qty": 540.0,
      "raw_unit": "pcs",
      "raw_price": 12.0,
      "converted_qty": 540.0,
      "converted_unit": "pcs",
      "converted_unit_price": 12.0,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": null,
      "stated_amount": 6480.0,
      "payable_amount": 0.0,
      "prevented_risk": 480.0,
      "status_code": "PRICE_OR_QTY_UNAPPROVED",
      "status_label": "Order quantity exceeded",
      "status_color": "orange",
      "risk_category": "unapproved_change",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-3",
        "R-7",
        "R-8",
        "R-6",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Direct link via purchase order PO-14 in email text (R-1)"
        },
        {
          "rule": "R-2 (Supplier)",
          "status": "ok",
          "detail": "Supplier matches Cardboard Service LLC. Use verified contract bank details for payment."
        },
        {
          "rule": "R-3 (Active Version)",
          "status": "ok",
          "detail": "Single active invoice version verified for this supplier."
        },
        {
          "rule": "R-7 (Material & Units)",
          "status": "ok",
          "detail": "Synonym recognized (\"cardboard pad\"). Invoice unit matches order unit: pcs."
        },
        {
          "rule": "R-8 (Invoice Total)",
          "status": "ok",
          "detail": "540 × 12 = $6,480.00."
        },
        {
          "rule": "R-6 (Order Quantity)",
          "status": "error",
          "detail": "Invoice No. 33 bills 540 pcs ($6,480.00), while approved limit is 500 pcs ($6,000.00). Accepted 540 pcs; warehouse receipt does not authorize the 40 pcs overrun. ERP purchase order terms apply."
        }
      ],
      "primary_reason": "Invoice No. 33 bills 540 pcs ($6,480.00), while approved limit is 500 pcs ($6,000.00). Accepted 540 pcs; warehouse receipt does not authorize the 40 pcs overrun. ERP purchase order terms apply.",
      "next_step": "Request overrun approval for 40 pcs from the buyer and receipt justification from the warehouse, or a corrected invoice for $6,000.00.",
      "actions": [
        {
          "recipient_role": "Buyer and Warehouse Manager",
          "recipient_name": "Owen Miller / Warehouse Manager",
          "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-9",
          "subject": "Order quantity exceeded: invoice No. 33, order PO-14",
          "body": "Hello team,\n\nEmail E-24 from Cardboard Service LLC, received 16.11 11:45.\nInvoice No. 33, order PO-14.\nInvoice No. 33 bills 540 pcs ($6,480.00), while approved limit is 500 pcs ($6,000.00). Accepted 540 pcs; warehouse receipt does not authorize the 40 pcs overrun. ERP purchase order terms apply.\n\nRequest overrun approval for 40 pcs from the buyer and receipt justification from the warehouse, or a corrected invoice for $6,000.00."
        }
      ]
    },
    {
      "id": "E-25",
      "received_at": "16.11 11:55",
      "sender": "PackLine Supply, invoice@packline.example",
      "text": "Regarding invoice 205: we changed banks, please pay to our new bank account. New bank details: Example Bank Corp., Acct No. 40702810000000000205.",
      "supplier_name": "PackLine Supply",
      "raw_invoice_no": "205",
      "canonical_invoice_no": "205",
      "order_id": "PO-11",
      "order": {
        "order_id": "PO-11",
        "order_date": "04.11.2026",
        "supplier": "PackLine Supply",
        "supplier_clean": "packline supply",
        "buyer": "Anna Carter",
        "material": "PE liner bag 600×800 mm",
        "unit": "pcs",
        "ordered_qty": 2000.0,
        "accepted_qty": 2000.0,
        "last_acceptance_date": "11.11.2026",
        "order_price": 7.0,
        "approval_id": ""
      },
      "approval": null,
      "match_confidence": 0.98,
      "p1_reason": "Linked to PO-11 via previously recorded invoice No. 205 from PackLine Supply (R-1)",
      "raw_qty": null,
      "raw_unit": "",
      "raw_price": null,
      "converted_qty": null,
      "converted_unit": "",
      "converted_unit_price": null,
      "conversion_formula": null,
      "material_mapping": null,
      "unit_mapping": null,
      "missing_extraction": [],
      "available_accepted_qty": null,
      "stated_amount": 14000.0,
      "payable_amount": 0.0,
      "prevented_risk": 14000.0,
      "status_code": "CRITICAL_REQUISITES",
      "status_label": "Verify recipient and bank details",
      "status_color": "rose",
      "risk_category": "requisites",
      "triggered_rules": [
        "R-1",
        "R-2",
        "R-9"
      ],
      "rule_checks": [
        {
          "rule": "R-1 (Order Matching)",
          "status": "ok",
          "detail": "Linked to PO-11 via previously recorded invoice No. 205 from PackLine Supply (R-1)"
        },
        {
          "rule": "R-2 (Supplier & Bank Details)",
          "status": "error",
          "detail": "Order PO-11 lists supplier PackLine Supply; email sender is PackLine Supply. Payment recipient and bank details in the email cannot be verified from the provided export. No signed amendment authorizing this change was found (R-2)."
        }
      ],
      "primary_reason": "Order PO-11 lists supplier PackLine Supply; email sender is PackLine Supply. Payment recipient and bank details in the email cannot be verified from the provided export. No signed amendment authorizing this change was found (R-2).",
      "next_step": "Hold payment preparation; verify the contract and signed addendum in Directum RX.",
      "actions": [
        {
          "recipient_role": "Buyer and CFO",
          "recipient_name": "Anna Carter / CFO",
          "rule_ref": "R-1, R-2, R-9",
          "subject": "Verify recipient and bank details: invoice No. 205, order PO-11",
          "body": "Hello team,\n\nEmail E-25 from PackLine Supply, received 16.11 11:55.\nInvoice No. 205, order PO-11.\nOrder PO-11 lists supplier PackLine Supply; email sender is PackLine Supply. Payment recipient and bank details in the email cannot be verified from the provided export. No signed amendment authorizing this change was found (R-2).\n\nHold payment preparation; verify the contract and signed addendum in Directum RX."
        }
      ]
    }
  ],
  "summary": {
    "total_emails": 25,
    "ready_to_pay_count": 8,
    "blocked_or_disputed_count": 14,
    "info_letters_count": 3,
    "total_payable_rub": 245700.0,
    "total_prevented_risk_rub": 274280.0,
    "risk_breakdown_rub": {
      "duplicate": 131500.0,
      "requisites": 54000.0,
      "math_error": 1000.0,
      "unapproved_change": 7780.0,
      "unaccepted_goods": 80000.0
    },
    "counts_by_status": {
      "READY_TO_PAY": 8,
      "DUPLICATE_OR_REPLACED": 5,
      "NOT_ACCEPTED_YET": 2,
      "PRICE_OR_QTY_UNAPPROVED": 4,
      "INFO_LETTER": 3,
      "MATH_ERROR": 1,
      "CRITICAL_REQUISITES": 2
    },
    "orders_count": 14,
    "approvals_count": 6,
    "rules_count": 9
  },
  "orders": [
    {
      "order_id": "PO-01",
      "order_date": "03.11.2026",
      "supplier": "Corrugated Box Center",
      "supplier_clean": "corrugated box center",
      "buyer": "Owen Miller",
      "material": "Shipping carton 400×300×250",
      "unit": "pcs",
      "ordered_qty": 1000.0,
      "accepted_qty": 800.0,
      "last_acceptance_date": "12.11.2026",
      "order_price": 40.0,
      "approval_id": "AP-03"
    },
    {
      "order_id": "PO-02",
      "order_date": "02.11.2026",
      "supplier": "PackLine Supply",
      "supplier_clean": "packline supply",
      "buyer": "Anna Carter",
      "material": "Berry pouch 1 kg",
      "unit": "pcs",
      "ordered_qty": 10000.0,
      "accepted_qty": 10000.0,
      "last_acceptance_date": "11.11.2026",
      "order_price": 5.0,
      "approval_id": "AP-04"
    },
    {
      "order_id": "PO-03",
      "order_date": "02.11.2026",
      "supplier": "Ladoga Film Corp.",
      "supplier_clean": "ladoga film",
      "buyer": "Daniel Grant",
      "material": "PE film 60 um",
      "unit": "kg",
      "ordered_qty": 200.0,
      "accepted_qty": 200.0,
      "last_acceptance_date": "10.11.2026",
      "order_price": 180.0,
      "approval_id": ""
    },
    {
      "order_id": "PO-04",
      "order_date": "04.11.2026",
      "supplier": "Corrugated Box Center",
      "supplier_clean": "corrugated box center",
      "buyer": "Owen Miller",
      "material": "Cold-resistant label 58×40 mm",
      "unit": "pcs",
      "ordered_qty": 6000.0,
      "accepted_qty": 6000.0,
      "last_acceptance_date": "12.11.2026",
      "order_price": 2.0,
      "approval_id": "AP-05"
    },
    {
      "order_id": "PO-05",
      "order_date": "06.11.2026",
      "supplier": "Timber Pallet Co.",
      "supplier_clean": "timber pallet",
      "buyer": "Owen Miller",
      "material": "Wooden pallet 1200×800",
      "unit": "pcs",
      "ordered_qty": 80.0,
      "accepted_qty": 0.0,
      "last_acceptance_date": "",
      "order_price": 900.0,
      "approval_id": ""
    },
    {
      "order_id": "PO-06",
      "order_date": "02.11.2026",
      "supplier": "PackLine Supply",
      "supplier_clean": "packline supply",
      "buyer": "Anna Carter",
      "material": "Berry pouch 300 g",
      "unit": "pcs",
      "ordered_qty": 5000.0,
      "accepted_qty": 5000.0,
      "last_acceptance_date": "10.11.2026",
      "order_price": 3.0,
      "approval_id": ""
    },
    {
      "order_id": "PO-07",
      "order_date": "05.11.2026",
      "supplier": "NordLabel Ltd.",
      "supplier_clean": "nordlabel",
      "buyer": "Anna Carter",
      "material": "Thermal label 100×150 mm",
      "unit": "pcs",
      "ordered_qty": 12000.0,
      "accepted_qty": 10000.0,
      "last_acceptance_date": "13.11.2026",
      "order_price": 1.5,
      "approval_id": ""
    },
    {
      "order_id": "PO-08",
      "order_date": "03.11.2026",
      "supplier": "TapeWorks Inc.",
      "supplier_clean": "tapeworks",
      "buyer": "Daniel Grant",
      "material": "Packing adhesive tape 48 mm × 66 m",
      "unit": "roll",
      "ordered_qty": 600.0,
      "accepted_qty": 600.0,
      "last_acceptance_date": "14.11.2026",
      "order_price": 95.0,
      "approval_id": "AP-01"
    },
    {
      "order_id": "PO-09",
      "order_date": "05.11.2026",
      "supplier": "Ladoga Film Corp.",
      "supplier_clean": "ladoga film",
      "buyer": "Daniel Grant",
      "material": "Stretch film 17 um, 500 mm",
      "unit": "kg",
      "ordered_qty": 300.0,
      "accepted_qty": 300.0,
      "last_acceptance_date": "13.11.2026",
      "order_price": 210.0,
      "approval_id": "AP-06"
    },
    {
      "order_id": "PO-10",
      "order_date": "05.11.2026",
      "supplier": "Timber Pallet Co.",
      "supplier_clean": "timber pallet",
      "buyer": "Owen Miller",
      "material": "Wooden pallet 1200×1000",
      "unit": "pcs",
      "ordered_qty": 40.0,
      "accepted_qty": 40.0,
      "last_acceptance_date": "09.11.2026",
      "order_price": 1100.0,
      "approval_id": ""
    },
    {
      "order_id": "PO-11",
      "order_date": "04.11.2026",
      "supplier": "PackLine Supply",
      "supplier_clean": "packline supply",
      "buyer": "Anna Carter",
      "material": "PE liner bag 600×800 mm",
      "unit": "pcs",
      "ordered_qty": 2000.0,
      "accepted_qty": 2000.0,
      "last_acceptance_date": "11.11.2026",
      "order_price": 7.0,
      "approval_id": ""
    },
    {
      "order_id": "PO-12",
      "order_date": "03.11.2026",
      "supplier": "NordLabel Ltd.",
      "supplier_clean": "nordlabel",
      "buyer": "Anna Carter",
      "material": "Thermal transfer ribbon 110 mm × 300 m",
      "unit": "roll",
      "ordered_qty": 40.0,
      "accepted_qty": 50.0,
      "last_acceptance_date": "12.11.2026",
      "order_price": 650.0,
      "approval_id": "AP-02"
    },
    {
      "order_id": "PO-13",
      "order_date": "06.11.2026",
      "supplier": "PackLine Supply",
      "supplier_clean": "packline supply",
      "buyer": "Anna Carter",
      "material": "Berry pouch 500 g",
      "unit": "pcs",
      "ordered_qty": 4000.0,
      "accepted_qty": 4000.0,
      "last_acceptance_date": "13.11.2026",
      "order_price": 4.0,
      "approval_id": ""
    },
    {
      "order_id": "PO-14",
      "order_date": "05.11.2026",
      "supplier": "Cardboard Service LLC",
      "supplier_clean": "cardboard service",
      "buyer": "Owen Miller",
      "material": "Cardboard pad 1200×800",
      "unit": "pcs",
      "ordered_qty": 500.0,
      "accepted_qty": 540.0,
      "last_acceptance_date": "12.11.2026",
      "order_price": 12.0,
      "approval_id": ""
    }
  ],
  "approvals": [
    {
      "approval_id": "AP-01",
      "date": "06.11.2026",
      "order_id": "PO-08",
      "change_summary": "Delivery in two batches: 360 rolls by 10.11, 240 rolls by 15.11. Price unchanged.",
      "status": "Signed",
      "signed_by": "Steven Parker"
    },
    {
      "approval_id": "AP-02",
      "date": "09.11.2026",
      "order_id": "PO-12",
      "change_summary": "Quantity increased from 40 to 50 rolls, price 650 USD per roll unchanged.",
      "status": "Signed",
      "signed_by": "Steven Parker"
    },
    {
      "approval_id": "AP-03",
      "date": "11.11.2026",
      "order_id": "PO-01",
      "change_summary": "Supplier will deliver the remaining 200 cartons by 20.11.2026.",
      "status": "Signed",
      "signed_by": "Steven Parker"
    },
    {
      "approval_id": "AP-04",
      "date": "12.11.2026",
      "order_id": "PO-02",
      "change_summary": "Berry pouch 1 kg price — 5.50 USD per piece instead of 5.00 USD for the entire order. Contract addendum dated 12.11.2026.",
      "status": "Signed",
      "signed_by": "Steven Parker"
    },
    {
      "approval_id": "AP-05",
      "date": "13.11.2026",
      "order_id": "PO-04",
      "change_summary": "Label price — 2.20 USD per piece instead of 2.00 USD.",
      "status": "Pending Signature",
      "signed_by": ""
    },
    {
      "approval_id": "AP-06",
      "date": "14.11.2026",
      "order_id": "PO-09",
      "change_summary": "Stretch film price — 225 USD per kg instead of 210 USD for deliveries from 18.11.2026.",
      "status": "Signed",
      "signed_by": "Steven Parker"
    }
  ],
  "rules": [
    {
      "rule_id": "R-1",
      "topic": "Invoice Matching",
      "text": "An invoice number is unique only within a single supplier. Invoices are matched by supplier and number, and linked to a purchase order by order ID—or, if omitted, by supplier, material, quantity, and order date."
    },
    {
      "rule_id": "R-2",
      "topic": "Supplier and Bank Details",
      "text": "Invoices are accepted only from the supplier listed on the purchase order. Any change in payment recipient or bank details requires a signed addendum in Directum RX. An email requesting new bank details without a signed addendum is escalated to the buyer and CFO."
    },
    {
      "rule_id": "R-3",
      "topic": "Invoice Versions and Duplicates",
      "text": "A corrected invoice with the same number supersedes the previous version. A re-sent invoice is a duplicate of an already received document, even if formatted with leading zeros or a slash suffix. A new invoice against the same order is allowed only for a new delivery batch or after an approved change."
    },
    {
      "rule_id": "R-4",
      "topic": "Accepted Quantity",
      "text": "Unless the contract specifies prepayment, payment is prepared only for the quantity accepted at the warehouse. Only posted warehouse receipts count as accepted; deliveries promised by the supplier do not count."
    },
    {
      "rule_id": "R-5",
      "topic": "Payment Terms",
      "text": "Prepayment and payment terms are specified in contracts and are not included in the export. If an invoice exceeds the accepted quantity, the accountant requests contract terms from the buyer and prepares neither payment nor final rejection until confirmed."
    },
    {
      "rule_id": "R-6",
      "topic": "Order Amendments",
      "text": "ERP purchase order price and quantity remain in effect unless a signed approval exists. A signed Directum RX approval takes precedence even if ERP has not been updated yet, strictly within its scope (order ID and effective date). Emails, calls, or chats with suppliers are not valid approvals."
    },
    {
      "rule_id": "R-7",
      "topic": "Units and Packaging",
      "text": "Order quantity and price are expressed in the order unit. When a supplier bills in bags, rolls, packs, or boxes, the invoice is converted into the order unit using the packaging ratio stated on the invoice. Suppliers may use alternate material names."
    },
    {
      "rule_id": "R-8",
      "topic": "Invoice Arithmetic",
      "text": "Amounts are in USD excluding tax, with one line item per invoice. The invoice total must equal quantity multiplied by unit price. An invoice with an arithmetic error is returned to the supplier for correction."
    },
    {
      "rule_id": "R-9",
      "topic": "Escalation and Sign-Off",
      "text": "Price, quantity, and schedule questions go to the order buyer; receipt questions go to the warehouse manager; payment confirmation goes to the treasurer because bank statements are not in the export. The accountant prepares payments and the CFO approves the payment registry."
    }
  ],
  "jury_presets": [
    {
      "title": "Demo #1: Corrected invoice 52 under PO-08 (after E-15 return per R-8)",
      "sender": "TapeWorks Inc., billing@tapeworks.example",
      "received_at": "16.11 14:10",
      "text": "Corrected invoice 52 under order PO-08, second batch: adhesive tape 48 mm × 66 m, 240 rolls at 95 USD. Total 22,800 USD. Previous version had a typo in the total amount.",
      "expected_note": "Supersedes erroneous invoice E-15 (R-3), passes arithmetic 240 × 95 = $22,800 (R-8) and split batch schedule AP-01 (R-6) → Payable $22,800.",
      "result": {
        "id": "CHECK-26",
        "received_at": "16.11 14:10",
        "sender": "TapeWorks Inc., billing@tapeworks.example",
        "text": "Corrected invoice 52 under order PO-08, second batch: adhesive tape 48 mm × 66 m, 240 rolls at 95 USD. Total 22,800 USD. Previous version had a typo in the total amount.",
        "supplier_name": "TapeWorks Inc.",
        "raw_invoice_no": "52",
        "canonical_invoice_no": "52",
        "order_id": "PO-08",
        "order": {
          "order_id": "PO-08",
          "order_date": "03.11.2026",
          "supplier": "TapeWorks Inc.",
          "supplier_clean": "tapeworks",
          "buyer": "Daniel Grant",
          "material": "Packing adhesive tape 48 mm × 66 m",
          "unit": "roll",
          "ordered_qty": 600.0,
          "accepted_qty": 600.0,
          "last_acceptance_date": "14.11.2026",
          "order_price": 95.0,
          "approval_id": "AP-01"
        },
        "approval": {
          "exists": true,
          "approval_id": "AP-01",
          "order_id": "PO-08",
          "date": "06.11.2026",
          "summary": "Delivery in two batches: 360 rolls by 10.11, 240 rolls by 15.11. Price unchanged.",
          "status": "Signed",
          "signed_by": "Steven Parker",
          "is_signed": true,
          "new_price": null,
          "new_qty": null,
          "effective_from_str": null,
          "effective_from_ddmm": null,
          "is_split_batches": true,
          "batches": [
            360.0,
            240.0
          ],
          "is_delayed_rest": false
        },
        "match_confidence": 1.0,
        "p1_reason": "Direct link via purchase order PO-08 in email text (R-1)",
        "raw_qty": 240.0,
        "raw_unit": "roll",
        "raw_price": 95.0,
        "converted_qty": 240.0,
        "converted_unit": "roll",
        "converted_unit_price": 95.0,
        "conversion_formula": null,
        "material_mapping": {
          "source": "adhesive tape",
          "target": "packing adhesive tape",
          "method": "rules"
        },
        "unit_mapping": null,
        "missing_extraction": [],
        "available_accepted_qty": 240.0,
        "stated_amount": 22800.0,
        "payable_amount": 22800.0,
        "prevented_risk": 0.0,
        "status_code": "READY_TO_PAY",
        "status_label": "Ready for draft registry",
        "status_color": "emerald",
        "risk_category": "none",
        "triggered_rules": [
          "R-1",
          "R-2",
          "R-3",
          "R-7",
          "R-8",
          "R-6",
          "R-4",
          "R-5",
          "R-9"
        ],
        "rule_checks": [
          {
            "rule": "R-1 (Order Matching)",
            "status": "ok",
            "detail": "Direct link via purchase order PO-08 in email text (R-1)"
          },
          {
            "rule": "R-2 (Supplier)",
            "status": "ok",
            "detail": "Supplier matches TapeWorks Inc.. Use verified contract bank details for payment."
          },
          {
            "rule": "R-3 (Active Version)",
            "status": "ok",
            "detail": "Single active invoice version verified for this supplier."
          },
          {
            "rule": "R-7 (Material & Units)",
            "status": "ok",
            "detail": "Synonym recognized (\"adhesive tape\"). Invoice unit matches order unit: roll."
          },
          {
            "rule": "R-8 (Invoice Total)",
            "status": "ok",
            "detail": "240 × 95 = $22,800.00."
          },
          {
            "rule": "R-6 (Price & Quantity)",
            "status": "ok",
            "detail": "Price $95/roll, order limit 600 roll. AP-01: Signed."
          },
          {
            "rule": "R-4, R-5 (Receipt)",
            "status": "ok",
            "detail": "Available for this invoice: 240 roll, required 240; previously billed 360. Prepayment not required."
          },
          {
            "rule": "R-9 (Payment Control)",
            "status": "warn",
            "detail": "Bank statement is not included in the export; explicit treasurer verification is required before payment."
          }
        ],
        "primary_reason": "Order, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $22,800.00. Bank statement and contract bank details check required.",
        "next_step": "Ask the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval.",
        "actions": [
          {
            "recipient_role": "Treasurer and CFO",
            "recipient_name": "Treasury / CFO",
            "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-4, R-5, R-9",
            "subject": "Ready for draft registry: invoice No. 52, order PO-08",
            "body": "Hello team,\n\nEmail CHECK-26 from TapeWorks Inc., received 16.11 14:10.\nInvoice No. 52, order PO-08.\nOrder, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $22,800.00. Bank statement and contract bank details check required.\n\nAsk the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval."
          }
        ]
      }
    },
    {
      "title": "Demo #2: Invoice without order ID + compound box packaging (R-1 + R-7)",
      "sender": "PackLine Supply, invoice@packline.example",
      "received_at": "16.11 14:25",
      "text": "Invoice 215: berry pouch 500 g, 8 boxes of 500 pcs, box price 2,000 USD. Total 16,000 USD. Reference: your order dated 06.11.",
      "expected_note": "Without an order ID, links to PO-13 by supplier, material, quantity, and date 06.11 (R-1); converts 8 boxes × 500 pcs = 4,000 pcs at $4.00 (R-7) → Payable $16,000.",
      "result": {
        "id": "CHECK-26",
        "received_at": "16.11 14:25",
        "sender": "PackLine Supply, invoice@packline.example",
        "text": "Invoice 215: berry pouch 500 g, 8 boxes of 500 pcs, box price 2,000 USD. Total 16,000 USD. Reference: your order dated 06.11.",
        "supplier_name": "PackLine Supply",
        "raw_invoice_no": "215",
        "canonical_invoice_no": "215",
        "order_id": "PO-13",
        "order": {
          "order_id": "PO-13",
          "order_date": "06.11.2026",
          "supplier": "PackLine Supply",
          "supplier_clean": "packline supply",
          "buyer": "Anna Carter",
          "material": "Berry pouch 500 g",
          "unit": "pcs",
          "ordered_qty": 4000.0,
          "accepted_qty": 4000.0,
          "last_acceptance_date": "13.11.2026",
          "order_price": 4.0,
          "approval_id": ""
        },
        "approval": null,
        "match_confidence": 1.0,
        "p1_reason": "Auto-linked without order ID to PO-13 by attributes (R-1): supplier PackLine Supply, material \"Berry pouch 500 g\" (Synonym recognized (\"berry pouch 500 g\")), quantity 4000 pcs, order date 06.11.2026",
        "raw_qty": 8.0,
        "raw_unit": "boxes",
        "raw_price": 2000.0,
        "converted_qty": 4000.0,
        "converted_unit": "pcs",
        "converted_unit_price": 4.0,
        "conversion_formula": "8 boxes × 500 pcs = 4000 pcs; $2,000 / 500 = $4.00/pcs",
        "material_mapping": null,
        "unit_mapping": null,
        "missing_extraction": [],
        "available_accepted_qty": 4000.0,
        "stated_amount": 16000.0,
        "payable_amount": 16000.0,
        "prevented_risk": 0.0,
        "status_code": "READY_TO_PAY",
        "status_label": "Ready for draft registry",
        "status_color": "emerald",
        "risk_category": "none",
        "triggered_rules": [
          "R-1",
          "R-2",
          "R-3",
          "R-7",
          "R-8",
          "R-6",
          "R-4",
          "R-5",
          "R-9"
        ],
        "rule_checks": [
          {
            "rule": "R-1 (Order Matching)",
            "status": "ok",
            "detail": "Auto-linked without order ID to PO-13 by attributes (R-1): supplier PackLine Supply, material \"Berry pouch 500 g\" (Synonym recognized (\"berry pouch 500 g\")), quantity 4000 pcs, order date 06.11.2026"
          },
          {
            "rule": "R-2 (Supplier)",
            "status": "ok",
            "detail": "Supplier matches PackLine Supply. Use verified contract bank details for payment."
          },
          {
            "rule": "R-3 (Active Version)",
            "status": "ok",
            "detail": "Single active invoice version verified for this supplier."
          },
          {
            "rule": "R-7 (Material & Units)",
            "status": "ok",
            "detail": "Synonym recognized (\"berry pouch 500 g\"). 8 boxes × 500 pcs = 4000 pcs; $2,000 / 500 = $4.00/pcs."
          },
          {
            "rule": "R-8 (Invoice Total)",
            "status": "ok",
            "detail": "8 × 2000 = $16,000.00."
          },
          {
            "rule": "R-6 (Price & Quantity)",
            "status": "ok",
            "detail": "Price $4/pcs, order limit 4000 pcs. ERP purchase order terms apply."
          },
          {
            "rule": "R-4, R-5 (Receipt)",
            "status": "ok",
            "detail": "Available for this invoice: 4000 pcs, required 4000; previously billed 0. Prepayment not required."
          },
          {
            "rule": "R-9 (Payment Control)",
            "status": "warn",
            "detail": "Bank statement is not included in the export; explicit treasurer verification is required before payment."
          }
        ],
        "primary_reason": "Order, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $16,000.00. Bank statement and contract bank details check required.",
        "next_step": "Ask the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval.",
        "actions": [
          {
            "recipient_role": "Treasurer and CFO",
            "recipient_name": "Treasury / CFO",
            "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-6, R-4, R-5, R-9",
            "subject": "Ready for draft registry: invoice No. 215, order PO-13",
            "body": "Hello team,\n\nEmail CHECK-26 from PackLine Supply, received 16.11 14:25.\nInvoice No. 215, order PO-13.\nOrder, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount $16,000.00. Bank statement and contract bank details check required.\n\nAsk the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval."
          }
        ]
      }
    },
    {
      "title": "Demo #3: Hidden duplicate with leading zeros and slash suffix (R-3)",
      "sender": "Timber Pallet Co., billing@timberpallet.example",
      "received_at": "16.11 14:40",
      "text": "Invoice No. 0091/2 for wooden pallets 1200x1000, 40 pcs at 1,100 USD. Total 44,000 USD. Reference: order dated 05.11.",
      "expected_note": "Normalizes invoice number 0091/2 → 91, detects duplicate of previously received invoice E-01 under PO-10 (R-3) → Blocks double payment of $44,000.",
      "result": {
        "id": "CHECK-26",
        "received_at": "16.11 14:40",
        "sender": "Timber Pallet Co., billing@timberpallet.example",
        "text": "Invoice No. 0091/2 for wooden pallets 1200x1000, 40 pcs at 1,100 USD. Total 44,000 USD. Reference: order dated 05.11.",
        "supplier_name": "Timber Pallet Co.",
        "raw_invoice_no": "0091/2",
        "canonical_invoice_no": "91",
        "order_id": "PO-10",
        "order": {
          "order_id": "PO-10",
          "order_date": "05.11.2026",
          "supplier": "Timber Pallet Co.",
          "supplier_clean": "timber pallet",
          "buyer": "Owen Miller",
          "material": "Wooden pallet 1200×1000",
          "unit": "pcs",
          "ordered_qty": 40.0,
          "accepted_qty": 40.0,
          "last_acceptance_date": "09.11.2026",
          "order_price": 1100.0,
          "approval_id": ""
        },
        "approval": null,
        "match_confidence": 0.98,
        "p1_reason": "Linked to PO-10 via previously recorded invoice No. 91 from Timber Pallet Co. (R-1)",
        "raw_qty": 40.0,
        "raw_unit": "pcs",
        "raw_price": 1100.0,
        "converted_qty": 40.0,
        "converted_unit": "pcs",
        "converted_unit_price": 1100.0,
        "conversion_formula": null,
        "material_mapping": null,
        "unit_mapping": null,
        "missing_extraction": [],
        "available_accepted_qty": null,
        "stated_amount": 44000.0,
        "payable_amount": 0.0,
        "prevented_risk": 44000.0,
        "status_code": "DUPLICATE_OR_REPLACED",
        "status_label": "Duplicate invoice (E-01)",
        "status_color": "amber",
        "risk_category": "duplicate",
        "triggered_rules": [
          "R-1",
          "R-2",
          "R-3",
          "R-9"
        ],
        "rule_checks": [
          {
            "rule": "R-1 (Order Matching)",
            "status": "ok",
            "detail": "Linked to PO-10 via previously recorded invoice No. 91 from Timber Pallet Co. (R-1)"
          },
          {
            "rule": "R-2 (Supplier)",
            "status": "ok",
            "detail": "Supplier matches Timber Pallet Co.. Use verified contract bank details for payment."
          },
          {
            "rule": "R-3 (Duplicates)",
            "status": "error",
            "detail": "Invoice No. 0091/2 (normalized 91) duplicates document E-01 from the same supplier (R-3)."
          }
        ],
        "primary_reason": "Invoice No. 0091/2 (normalized 91) duplicates document E-01 from the same supplier (R-3).",
        "next_step": "Exclude duplicate from payment registry. Check bank statement for payment status of E-01.",
        "actions": [
          {
            "recipient_role": "Treasurer",
            "recipient_name": "Treasury",
            "rule_ref": "R-1, R-2, R-3, R-9",
            "subject": "Duplicate invoice (E-01): invoice No. 0091/2, order PO-10",
            "body": "Hello team,\n\nEmail CHECK-26 from Timber Pallet Co., received 16.11 14:40.\nInvoice No. 0091/2, order PO-10.\nInvoice No. 0091/2 (normalized 91) duplicates document E-01 from the same supplier (R-3).\n\nExclude duplicate from payment registry. Check bank statement for payment status of E-01."
          }
        ]
      }
    },
    {
      "title": "Demo #4: Unauthorized factoring bank-details switch without Directum RX (R-2)",
      "sender": "TapeWorks Factoring, pay@tapeworks-factor.example",
      "received_at": "16.11 15:00",
      "text": "Invoice 45 under order PO-08: adhesive tape 48 mm × 66 m, 360 rolls at 95 USD. Total 34,200 USD. Please pay using the new financial agent bank details.",
      "expected_note": "Blocks payment recipient change without a signed addendum in Directum RX (R-2) → Escalated to buyer Daniel Grant and CFO.",
      "result": {
        "id": "CHECK-26",
        "received_at": "16.11 15:00",
        "sender": "TapeWorks Factoring, pay@tapeworks-factor.example",
        "text": "Invoice 45 under order PO-08: adhesive tape 48 mm × 66 m, 360 rolls at 95 USD. Total 34,200 USD. Please pay using the new financial agent bank details.",
        "supplier_name": "TapeWorks Factoring",
        "raw_invoice_no": "45",
        "canonical_invoice_no": "45",
        "order_id": "PO-08",
        "order": {
          "order_id": "PO-08",
          "order_date": "03.11.2026",
          "supplier": "TapeWorks Inc.",
          "supplier_clean": "tapeworks",
          "buyer": "Daniel Grant",
          "material": "Packing adhesive tape 48 mm × 66 m",
          "unit": "roll",
          "ordered_qty": 600.0,
          "accepted_qty": 600.0,
          "last_acceptance_date": "14.11.2026",
          "order_price": 95.0,
          "approval_id": "AP-01"
        },
        "approval": {
          "exists": true,
          "approval_id": "AP-01",
          "order_id": "PO-08",
          "date": "06.11.2026",
          "summary": "Delivery in two batches: 360 rolls by 10.11, 240 rolls by 15.11. Price unchanged.",
          "status": "Signed",
          "signed_by": "Steven Parker",
          "is_signed": true,
          "new_price": null,
          "new_qty": null,
          "effective_from_str": null,
          "effective_from_ddmm": null,
          "is_split_batches": true,
          "batches": [
            360.0,
            240.0
          ],
          "is_delayed_rest": false
        },
        "match_confidence": 1.0,
        "p1_reason": "Direct link via purchase order PO-08 in email text (R-1)",
        "raw_qty": 360.0,
        "raw_unit": "roll",
        "raw_price": 95.0,
        "converted_qty": 360.0,
        "converted_unit": "roll",
        "converted_unit_price": 95.0,
        "conversion_formula": null,
        "material_mapping": null,
        "unit_mapping": null,
        "missing_extraction": [],
        "available_accepted_qty": null,
        "stated_amount": 34200.0,
        "payable_amount": 0.0,
        "prevented_risk": 34200.0,
        "status_code": "CRITICAL_REQUISITES",
        "status_label": "Verify recipient and bank details",
        "status_color": "rose",
        "risk_category": "requisites",
        "triggered_rules": [
          "R-1",
          "R-2",
          "R-9"
        ],
        "rule_checks": [
          {
            "rule": "R-1 (Order Matching)",
            "status": "ok",
            "detail": "Direct link via purchase order PO-08 in email text (R-1)"
          },
          {
            "rule": "R-2 (Supplier & Bank Details)",
            "status": "error",
            "detail": "Order PO-08 lists supplier TapeWorks Inc.; email sender is TapeWorks Factoring. Payment recipient and bank details in the email cannot be verified from the provided export. No signed amendment authorizing this change was found (R-2)."
          }
        ],
        "primary_reason": "Order PO-08 lists supplier TapeWorks Inc.; email sender is TapeWorks Factoring. Payment recipient and bank details in the email cannot be verified from the provided export. No signed amendment authorizing this change was found (R-2).",
        "next_step": "Hold payment preparation; verify the contract and signed addendum in Directum RX.",
        "actions": [
          {
            "recipient_role": "Buyer and CFO",
            "recipient_name": "Daniel Grant / CFO",
            "rule_ref": "R-1, R-2, R-9",
            "subject": "Verify recipient and bank details: invoice No. 45, order PO-08",
            "body": "Hello team,\n\nEmail CHECK-26 from TapeWorks Factoring, received 16.11 15:00.\nInvoice No. 45, order PO-08.\nOrder PO-08 lists supplier TapeWorks Inc.; email sender is TapeWorks Factoring. Payment recipient and bank details in the email cannot be verified from the provided export. No signed amendment authorizing this change was found (R-2).\n\nHold payment preparation; verify the contract and signed addendum in Directum RX."
          }
        ]
      }
    },
    {
      "title": "Demo #5: Hidden arithmetic error in roll packaging (R-7 + R-8)",
      "sender": "NordLabel Ltd., billing@nordlabel.example",
      "received_at": "16.11 15:15",
      "text": "Invoice 125 under PO-07, second batch: thermal label 100×150, 2 rolls of 1,000 pcs, roll price 1,500 USD. Total 3,500 USD.",
      "expected_note": "Detects arithmetic error: 2 rolls × $1,500 = $3,000 ≠ $3,500 (+$500, R-8) → Return to supplier for correction.",
      "result": {
        "id": "CHECK-26",
        "received_at": "16.11 15:15",
        "sender": "NordLabel Ltd., billing@nordlabel.example",
        "text": "Invoice 125 under PO-07, second batch: thermal label 100×150, 2 rolls of 1,000 pcs, roll price 1,500 USD. Total 3,500 USD.",
        "supplier_name": "NordLabel Ltd.",
        "raw_invoice_no": "125",
        "canonical_invoice_no": "125",
        "order_id": "PO-07",
        "order": {
          "order_id": "PO-07",
          "order_date": "05.11.2026",
          "supplier": "NordLabel Ltd.",
          "supplier_clean": "nordlabel",
          "buyer": "Anna Carter",
          "material": "Thermal label 100×150 mm",
          "unit": "pcs",
          "ordered_qty": 12000.0,
          "accepted_qty": 10000.0,
          "last_acceptance_date": "13.11.2026",
          "order_price": 1.5,
          "approval_id": ""
        },
        "approval": null,
        "match_confidence": 1.0,
        "p1_reason": "Direct link via purchase order PO-07 in email text (R-1)",
        "raw_qty": 2.0,
        "raw_unit": "rolls",
        "raw_price": 1500.0,
        "converted_qty": 2000.0,
        "converted_unit": "pcs",
        "converted_unit_price": 1.5,
        "conversion_formula": "2 rolls × 1000 pcs = 2000 pcs; $1,500 / 1000 = $1.50/pcs",
        "material_mapping": null,
        "unit_mapping": null,
        "missing_extraction": [],
        "available_accepted_qty": null,
        "stated_amount": 3500.0,
        "payable_amount": 0.0,
        "prevented_risk": 500.0,
        "status_code": "MATH_ERROR",
        "status_label": "Invoice arithmetic error",
        "status_color": "purple",
        "risk_category": "math_error",
        "triggered_rules": [
          "R-1",
          "R-2",
          "R-3",
          "R-7",
          "R-8",
          "R-9"
        ],
        "rule_checks": [
          {
            "rule": "R-1 (Order Matching)",
            "status": "ok",
            "detail": "Direct link via purchase order PO-07 in email text (R-1)"
          },
          {
            "rule": "R-2 (Supplier)",
            "status": "ok",
            "detail": "Supplier matches NordLabel Ltd.. Use verified contract bank details for payment."
          },
          {
            "rule": "R-3 (Active Version)",
            "status": "ok",
            "detail": "Single active invoice version verified for this supplier."
          },
          {
            "rule": "R-7 (Material & Units)",
            "status": "ok",
            "detail": "Synonym recognized (\"thermal label\"). 2 rolls × 1000 pcs = 2000 pcs; $1,500 / 1000 = $1.50/pcs."
          },
          {
            "rule": "R-8 (Invoice Total)",
            "status": "error",
            "detail": "Invoice No. 125: 2 × 1500 = $3,000.00; stated $3,500.00. Variance +500.00 USD."
          }
        ],
        "primary_reason": "Invoice No. 125: 2 × 1500 = $3,000.00; stated $3,500.00. Variance +500.00 USD.",
        "next_step": "Request a corrected invoice No. 125 from the supplier for $3,000.00.",
        "actions": [
          {
            "recipient_role": "Supplier",
            "recipient_name": "NordLabel Ltd.",
            "rule_ref": "R-1, R-2, R-3, R-7, R-8, R-9",
            "subject": "Invoice arithmetic error: invoice No. 125, order PO-07",
            "body": "Hello team,\n\nEmail CHECK-26 from NordLabel Ltd., received 16.11 15:15.\nInvoice No. 125, order PO-07.\nInvoice No. 125: 2 × 1500 = $3,000.00; stated $3,500.00. Variance +500.00 USD.\n\nRequest a corrected invoice No. 125 from the supplier for $3,000.00."
          }
        ]
      }
    }
  ]
};
