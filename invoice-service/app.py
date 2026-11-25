#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web server and CLI interface for the "North Berry: Smart 3-Way Match" pilot (Case 04 Target AI Fest 2026).

Capabilities:
- Serves the web UI (static/index.html, styles.css, app.js, data_bundle.js)
- REST API:
  - GET  /api/data                -> full analysis of 25 emails, orders, approvals, and rules
  - POST /api/analyze-custom      -> live reconciliation of any custom email/invoice
  - GET  /api/export-registry.csv -> draft payment registry requiring treasury verification (UTF-8 BOM CSV)
  - GET  /api/export-audit.csv    -> full reconciliation audit report for all 25 emails in CSV
- CLI:
  - python3 app.py --bundle       -> refreshes static/data_bundle.js and results for 5 demo presets
  - python3 app.py                -> starts the HTTP server on http://127.0.0.1:8040
"""

from __future__ import annotations

import base64
import csv
import io
import json
import os
import sys
import logging
import unittest
from typing import Any, Dict
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, unquote

from ai_extract import ModelUnavailable, confirmed_fields, extract_invoice, suggest_material_word
from xlsx_review import WorkbookReviews

from engine import (
    load_case_database,
    analyze_all_emails,
    analyze_single_custom_email,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_XLSX = os.path.join(BASE_DIR, "data", "case04.xlsx")
STATIC_DIR = os.path.join(BASE_DIR, "static")
MAX_XLSX_BYTES = 10_000_000
MAX_WORKBOOK_JSON_BYTES = 4 * ((MAX_XLSX_BYTES + 2) // 3) + 100_000
WORKBOOK_REVIEWS = WorkbookReviews()


JURY_PRESETS = [
    {
        "title": "Demo #1: Corrected invoice 52 under PO-08 (after E-15 return per R-8)",
        "sender": "TapeWorks Inc., billing@tapeworks.example",
        "received_at": "16.11 14:10",
        "text": "Corrected invoice 52 under order PO-08, second batch: adhesive tape 48 mm × 66 m, 240 rolls at 95 USD. Total 22,800 USD. Previous version had a typo in the total amount.",
        "expected_note": "Supersedes erroneous invoice E-15 (R-3), passes arithmetic 240 × 95 = $22,800 (R-8) and split batch schedule AP-01 (R-6) → Payable $22,800.",
    },
    {
        "title": "Demo #2: Invoice without order ID + compound box packaging (R-1 + R-7)",
        "sender": "PackLine Supply, invoice@packline.example",
        "received_at": "16.11 14:25",
        "text": "Invoice 215: berry pouch 500 g, 8 boxes of 500 pcs, box price 2,000 USD. Total 16,000 USD. Reference: your order dated 06.11.",
        "expected_note": "Without an order ID, links to PO-13 by supplier, material, quantity, and date 06.11 (R-1); converts 8 boxes × 500 pcs = 4,000 pcs at $4.00 (R-7) → Payable $16,000.",
    },
    {
        "title": "Demo #3: Hidden duplicate with leading zeros and slash suffix (R-3)",
        "sender": "Timber Pallet Co., billing@timberpallet.example",
        "received_at": "16.11 14:40",
        "text": "Invoice No. 0091/2 for wooden pallets 1200x1000, 40 pcs at 1,100 USD. Total 44,000 USD. Reference: order dated 05.11.",
        "expected_note": "Normalizes invoice number 0091/2 → 91, detects duplicate of previously received invoice E-01 under PO-10 (R-3) → Blocks double payment of $44,000.",
    },
    {
        "title": "Demo #4: Unauthorized factoring bank-details switch without Directum RX (R-2)",
        "sender": "TapeWorks Factoring, pay@tapeworks-factor.example",
        "received_at": "16.11 15:00",
        "text": "Invoice 45 under order PO-08: adhesive tape 48 mm × 66 m, 360 rolls at 95 USD. Total 34,200 USD. Please pay using the new financial agent bank details.",
        "expected_note": "Blocks payment recipient change without a signed addendum in Directum RX (R-2) → Escalated to buyer Daniel Grant and CFO.",
    },
    {
        "title": "Demo #5: Hidden arithmetic error in roll packaging (R-7 + R-8)",
        "sender": "NordLabel Ltd., billing@nordlabel.example",
        "received_at": "16.11 15:15",
        "text": "Invoice 125 under PO-07, second batch: thermal label 100×150, 2 rolls of 1,000 pcs, roll price 1,500 USD. Total 3,500 USD.",
        "expected_note": "Detects arithmetic error: 2 rolls × $1,500 = $3,000 ≠ $3,500 (+$500, R-8) → Return to supplier for correction.",
    },
]


def generate_csv_registry(analysis: Dict[str, Any]) -> bytes:
    out = io.StringIO()
    writer = csv.writer(out, delimiter=";")
    writer.writerow([
        "Email",
        "Received",
        "Order (ERP)",
        "Supplier",
        "Invoice No.",
        "Material (ERP)",
        "Accepted at Warehouse",
        "Basis / Directum RX Approval",
        "Payable Amount (USD excl. tax)",
        "Buyer",
        "Treasurer Verification (R-9)",
    ])
    for item in analysis["items"]:
        if item["status_code"] == "READY_TO_PAY":
            ord_obj = item.get("order") or {}
            app_obj = item.get("approval") or {}
            writer.writerow([
                item["id"],
                item["received_at"],
                item["order_id"],
                item["supplier_name"],
                item["raw_invoice_no"],
                ord_obj.get("material", ""),
                f"{int(ord_obj.get('accepted_qty', 0))} {ord_obj.get('unit', '')}",
                app_obj.get("approval_id", "Per ERP order"),
                f"{item['payable_amount']:.2f}",
                ord_obj.get("buyer", ""),
                "Verify bank statement (R-9)",
            ])
    return ("\ufeff" + out.getvalue()).encode("utf-8")


def generate_csv_full_audit(analysis: Dict[str, Any]) -> bytes:
    out = io.StringIO()
    writer = csv.writer(out, delimiter=";")
    writer.writerow([
        "Email ID",
        "Received",
        "Sender",
        "Order",
        "Invoice No.",
        "Reconciliation Status",
        "Stated Amount (USD)",
        "Payable (USD)",
        "Flagged Risk (USD)",
        "Rules",
        "Reason / Reconciliation Details",
        "Next Step (R-9)",
    ])
    for item in analysis["items"]:
        writer.writerow([
            item["id"],
            item["received_at"],
            item["sender"],
            item["order_id"],
            item["raw_invoice_no"],
            item["status_label"],
            f"{item['stated_amount']:.2f}",
            f"{item['payable_amount']:.2f}",
            f"{item['prevented_risk']:.2f}",
            ", ".join(item["triggered_rules"]),
            item["primary_reason"],
            item["next_step"],
        ])
    return ("\ufeff" + out.getvalue()).encode("utf-8")


def build_static_bundle(write_file: bool = True) -> Dict[str, Any]:
    """Generate static/data_bundle.js with full dataset and demo presets for offline UI use."""
    db = load_case_database(DEFAULT_XLSX)
    analysis = analyze_all_emails(db)

    preset_results = []
    for preset in JURY_PRESETS:
        res = analyze_single_custom_email(
            DEFAULT_XLSX,
            sender=preset["sender"],
            text=preset["text"],
            received_at=preset["received_at"],
        )
        preset_results.append({
            **preset,
            "result": res,
        })

    payload = {
        **analysis,
        "jury_presets": preset_results,
    }

    if write_file:
        bundle_path = os.path.join(STATIC_DIR, "data_bundle.js")
        with open(bundle_path, "w", encoding="utf-8") as f:
            f.write("// Auto-generated data bundle for Case 04 (North Berry)\n")
            f.write("window.CASE04_DATA = ")
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write(";\n")
    return payload


class Case04RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/data":
            payload = build_static_bundle(write_file=False)
            self._send_json(payload)
            return
        if parsed.path == "/api/export-registry.csv":
            db = load_case_database(DEFAULT_XLSX)
            analysis = analyze_all_emails(db)
            csv_bytes = generate_csv_registry(analysis)
            self._send_bytes(
                csv_bytes,
                "text/csv; charset=utf-8",
                'attachment; filename="payment_registry_north_berry.csv"',
            )
            return
        if parsed.path == "/api/export-audit.csv":
            db = load_case_database(DEFAULT_XLSX)
            analysis = analyze_all_emails(db)
            csv_bytes = generate_csv_full_audit(analysis)
            self._send_bytes(
                csv_bytes,
                "text/csv; charset=utf-8",
                'attachment; filename="audit_25_emails_north_berry.csv"',
            )
            return
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/extract-ai":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 100_000:
                    raise ValueError("Invalid AI extraction request size.")
                req = json.loads(self.rfile.read(length).decode("utf-8"))
                text = req.get("text") if isinstance(req, dict) else None
                if not isinstance(text, str) or not text.strip():
                    raise ValueError("Enter email text for AI extraction.")
                extraction = extract_invoice(text.strip())
            except (ValueError, UnicodeError) as error:
                self._send_json({"ok": False, "error": str(error)}, status=400)
                return
            except ModelUnavailable as error:
                self._send_json({"ok": False, "error": str(error)}, status=503)
                return
            self._send_json({"ok": True, **extraction})
            return
        if parsed.path == "/api/analyze-custom":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= MAX_WORKBOOK_JSON_BYTES:
                    raise ValueError("Invalid reconciliation request size.")
                raw_body = self.rfile.read(length).decode("utf-8")
                req = json.loads(raw_body)
                if not isinstance(req, dict):
                    raise ValueError("Expected a JSON object with sender, text, and received_at")
                values = {}
                for field in ("sender", "text", "received_at"):
                    value = req.get(field)
                    if not isinstance(value, str) or not value.strip():
                        raise ValueError(f"Fill in the required field: {field}")
                    values[field] = value.strip()
                if "ai_token" in req:
                    if req.get("ai_confirmed") is not True:
                        raise ValueError("Confirm the AI-proposed fields before running reconciliation.")
                    values["ai_fields"] = confirmed_fields(values["text"], req["ai_token"])
                use_ai = req.get("use_ai") is True
                ai_message = None

                def advise_material(invoice_material, order_material):
                    nonlocal ai_message
                    try:
                        return suggest_material_word(invoice_material, order_material)
                    except ModelUnavailable as error:
                        ai_message = str(error)
                        return None

                if use_ai:
                    values["material_advisor"] = advise_material
                review_id = req.get("review_id")
                xlsx_b64 = req.get("xlsx_base64")
                if review_id is not None:
                    if not isinstance(review_id, str) or xlsx_b64 is not None:
                        raise ValueError("Specify only one data source for reconciliation.")
                    review = WORKBOOK_REVIEWS.get(review_id)
                    if review is None:
                        self._send_json({"ok": False, "error": "Review session expired. Upload the Excel workbook again."}, status=404)
                        return
                    result = review.check_email(**values)
                elif xlsx_b64 is not None:
                    if not isinstance(xlsx_b64, str) or not xlsx_b64.strip():
                        raise ValueError("Invalid Excel payload in request")
                    xlsx_bytes = base64.b64decode(xlsx_b64, validate=True)
                    if len(xlsx_bytes) > MAX_XLSX_BYTES:
                        raise ValueError("File size must not exceed 10 MB")
                    xlsx_source: Any = io.BytesIO(xlsx_bytes)
                    result = analyze_single_custom_email(xlsx_source, fallback_xlsx_path=DEFAULT_XLSX, **values)
                else:
                    result = analyze_single_custom_email(DEFAULT_XLSX, **values)
                proposal = None
                if use_ai and "ai_token" not in req and result["missing_extraction"]:
                    try:
                        extraction = extract_invoice(values["text"])
                    except (ModelUnavailable, ValueError) as error:
                        ai_message = str(error)
                    else:
                        proposed_fields = {
                            key: field for key, field in extraction["fields"].items()
                            if key in result["missing_extraction"]
                        }
                        if proposed_fields:
                            proposal = {"token": extraction["token"], "fields": proposed_fields}
            except (ValueError, UnicodeError) as error:
                self._send_json({"ok": False, "error": str(error)}, status=400)
                return
            except Exception:
                logging.exception("Reconciliation failed")
                self._send_json({"ok": False, "error": "Could not complete reconciliation. Retry the request; result is not confirmed."}, status=500)
                return
            self._send_json({"ok": True, "item": result, "proposal": proposal, "ai_message": ai_message})
            return
        if parsed.path == "/api/xlsx-review":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 100_000:
                    raise ValueError("Invalid Excel AI review request.")
                req = json.loads(self.rfile.read(length).decode("utf-8"))
                if not isinstance(req, dict) or not isinstance(req.get("review_id"), str):
                    raise ValueError("Missing upload review_id.")
                invoice_id = req.get("invoice_id")
                if invoice_id is not None and (not isinstance(invoice_id, str) or req.get("ai_confirmed") is not True):
                    raise ValueError("Explicitly confirm the proposed invoice fields.")
                review = WORKBOOK_REVIEWS.get(req["review_id"])
                if review is None:
                    self._send_json({"ok": False, "error": "Review session expired. Upload the Excel workbook again."}, status=404)
                    return
                result = review.run(invoice_id)
            except (ValueError, UnicodeError) as error:
                self._send_json({"ok": False, "error": str(error)}, status=400)
                return
            except Exception:
                logging.exception("Excel AI review failed")
                self._send_json({"ok": False, "error": "Could not complete AI review. Please try again."}, status=500)
                return
            self._send_json({"ok": True, **result})
            return
        if parsed.path == "/api/upload-xlsx":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                ctype = self.headers.get("Content-Type", "")
                is_json = "application/json" in ctype
                body_limit = MAX_WORKBOOK_JSON_BYTES if is_json else MAX_XLSX_BYTES
                if not 0 < length <= body_limit:
                    raise ValueError("File size must not exceed 10 MB")
                raw_bytes = self.rfile.read(length)
                filename = unquote(self.headers.get("X-Filename", "custom.xlsx"))
                use_ai = self.headers.get("X-Use-AI") == "true"
                if is_json:
                    req = json.loads(raw_bytes.decode("utf-8"))
                    if not isinstance(req, dict):
                        raise ValueError("Expected a JSON object containing the file payload")
                    filename = str(req.get("filename") or filename)
                    use_ai = req.get("use_ai") is True
                    b64_data = req.get("data_base64")
                    if not isinstance(b64_data, str) or not b64_data.strip():
                        raise ValueError("Missing Excel file content")
                    raw_bytes = base64.b64decode(b64_data, validate=True)
                if len(raw_bytes) > MAX_XLSX_BYTES:
                    raise ValueError("File size must not exceed 10 MB")
                db = load_case_database(io.BytesIO(raw_bytes), fallback_xlsx_path=DEFAULT_XLSX)
                if not db["emails"]:
                    raise ValueError("No email or invoice rows found in the selected Excel file")
                ids = {email["id"] for email in db["emails"]}
                if len(ids) != len(db["emails"]):
                    raise ValueError("Duplicate email IDs found in Excel. Assign a unique ID to each row.")
                analysis = analyze_all_emails(db)
            except (ValueError, UnicodeError) as error:
                self._send_json({"ok": False, "error": str(error)}, status=400)
                return
            except Exception:
                logging.exception("Failed to parse uploaded Excel file")
                self._send_json({"ok": False, "error": "Could not read Excel file (.xlsx). Check worksheet structure."}, status=500)
                return
            response = {"ok": True, "filename": filename, "data": analysis}
            if use_ai:
                response["review_id"] = WORKBOOK_REVIEWS.add(db, analysis)
            self._send_json(response)
            return
        self.send_error(404, "Endpoint not found")

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_bytes(self, body: bytes, content_type: str, disposition: str):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Disposition", disposition)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    if "--verify" in sys.argv:
        suite = unittest.defaultTestLoader.discover(os.path.join(BASE_DIR, "tests"))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        raise SystemExit(0 if result.wasSuccessful() else 1)
    payload = build_static_bundle()
    if "--bundle" in sys.argv:
        print("=== Data snapshot and 5 demo presets updated ===")
        for idx, p in enumerate(payload["jury_presets"], 1):
            r = p["result"]
            print(
                f"[{idx}] {p['title']}\n"
                f"    -> Order: {r['order_id']} | Status: {r['status_label']} | "
                f"Stated: ${r['stated_amount']:,.0f} | Payable: ${r['payable_amount']:,.0f} | "
                f"Risk: ${r['prevented_risk']:,.0f} | Rules: {','.join(r['triggered_rules'])}"
            )
        return

    port = int(os.environ.get("PORT", "8040"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Case04RequestHandler)
    print(f"North Berry: Smart 3-Way Match pilot running at http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
