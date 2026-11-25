import base64
import csv
import io
import json
import threading
import unittest
import zipfile
from http.server import HTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

from ai_extract import ModelUnavailable
from app import Case04RequestHandler, DEFAULT_XLSX, generate_csv_registry
from engine import analyze_all_emails, load_case_database
from test_engine import FIXTURES


class QuietHandler(Case04RequestHandler):
    def log_message(self, *args):
        pass


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(('127.0.0.1', 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}/api/analyze-custom'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, payload):
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        request = Request(self.url, data=body, headers={'Content-Type': 'application/json'})
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, json.load(response)
        except HTTPError as response:
            return response.code, json.load(response)

    def test_audit_cases_through_real_http(self):
        for case in FIXTURES:
            with self.subTest(case=case['id']):
                status, result = self.request({k: case[k] for k in ('sender', 'text', 'received_at')})
                self.assertEqual(status, 200)
                self.assertTrue(result['ok'])
                self.assertEqual(result['item']['status_code'], case['expected_status'])
                self.assertEqual(result['item']['payable_amount'], case['expected_payable'])

    def test_invalid_requests_return_json_400_and_server_survives(self):
        valid = {k: FIXTURES[8][k] for k in ('sender', 'text', 'received_at')}
        for invalid in (b'{', b'\xff', [], {}, dict(valid, text=123), dict(valid, received_at='32.11 14:30'), dict(valid, sender=' ')):
            with self.subTest(invalid=invalid):
                status, response = self.request(invalid)
                self.assertEqual(status, 400)
                self.assertFalse(response['ok'])
                self.assertTrue(response['error'])
        self.assertEqual(self.request(valid)[0], 200)

    def test_unexpected_engine_failure_returns_json_500(self):
        with patch('app.analyze_single_custom_email', side_effect=RuntimeError('simulated')), self.assertLogs(level='ERROR'):
            status, result = self.request({k: FIXTURES[8][k] for k in ('sender', 'text', 'received_at')})
        self.assertEqual(status, 500)
        self.assertFalse(result['ok'])
        self.assertNotIn('item', result)

    def test_csv_is_explicitly_a_draft_pending_treasury(self):
        data = generate_csv_registry(analyze_all_emails(load_case_database(DEFAULT_XLSX)))
        rows = list(csv.reader(io.StringIO(data.decode('utf-8-sig')), delimiter=';'))
        self.assertEqual(len(rows), 9)
        self.assertTrue(all('Verify' in row[-1] for row in rows[1:]))
        self.assertEqual(sum(float(row[8]) for row in rows[1:]), 245700)

    def _post_url(self, path, payload):
        url = f'http://127.0.0.1:{self.server.server_port}{path}'
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        request = Request(url, data=body, headers={'Content-Type': 'application/json'})
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, json.load(response)
        except HTTPError as response:
            return response.code, json.load(response)

    def test_upload_xlsx_endpoint_valid_and_invalid(self):
        raw_b64 = base64.b64encode(Path(DEFAULT_XLSX).read_bytes()).decode('ascii')
        status, result = self._post_url('/api/upload-xlsx', {'filename': 'my_case.xlsx', 'data_base64': raw_b64})
        self.assertEqual(status, 200)
        self.assertTrue(result['ok'])
        self.assertEqual(result['filename'], 'my_case.xlsx')
        self.assertEqual(len(result['data']['items']), 25)
        self.assertEqual(result['data']['summary']['total_payable_rub'], 245700)

        # Invalid base64 / non-xlsx bytes return 400
        for bad in ({'filename': 'bad.xlsx', 'data_base64': 'not-a-zip'}, {'filename': 'bad.xlsx', 'data_base64': base64.b64encode(b'plain text').decode()}):
            st, err = self._post_url('/api/upload-xlsx', bad)
            self.assertEqual(st, 400)
            self.assertFalse(err['ok'])

        # Empty workbook without email rows returns 400
        empty_xlsx = io.BytesIO()
        with zipfile.ZipFile(empty_xlsx, 'w') as z:
            z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/></Types>')
            z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
            z.writestr('xl/workbook.xml', '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets></workbook>')
            z.writestr('xl/_rels/workbook.xml.rels', '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
            z.writestr('xl/worksheets/sheet1.xml', '<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData/></worksheet>')
        st_empty, err_empty = self._post_url('/api/upload-xlsx', {'filename': 'empty.xlsx', 'data_base64': base64.b64encode(empty_xlsx.getvalue()).decode()})
        self.assertEqual(st_empty, 400)
        self.assertFalse(err_empty['ok'])

    def test_analyze_custom_uses_uploaded_xlsx_base64(self):
        raw_b64 = base64.b64encode(Path(DEFAULT_XLSX).read_bytes()).decode('ascii')
        case = FIXTURES[8]
        status, result = self._post_url('/api/analyze-custom', {
            'sender': case['sender'],
            'text': case['text'],
            'received_at': case['received_at'],
            'xlsx_base64': raw_b64,
        })
        self.assertEqual(status, 200)
        self.assertTrue(result['ok'])
        self.assertEqual(result['item']['status_code'], case['expected_status'])

    def test_upload_ai_maps_names_and_reconciles_whole_workbook_after_confirmation(self):
        workbook = load_case_database(DEFAULT_XLSX)
        tape = "Invoice 502 under order PO-08: adhesion tape 48 mm × 66 m, 10 rolls at 95 USD. Total 950 USD."
        bag = "Invoice 215 under order PO-13: berry pouch 500 g. Shipped 4000 peice. Each — 4 dollars. Amount due — 16,000 dollars."
        emails = [
            ("E-101", "16.11 13:00", "TapeWorks Inc.", tape),
            ("E-102", "16.11 13:10", "TapeWorks Inc.", tape.replace("502", "503").replace("48 mm", "50 mm")),
            ("E-103", "16.11 13:20", "PackLine Supply", bag),
            ("E-104", "16.11 13:30", "PackLine Supply",
             "Invoice 216 under order PO-13: berry pouch 500 g, 1,000 pcs at 4 USD. Total 4,000 USD."),
        ]
        workbook["emails"] = [
            {"id": key, "received_at": date, "sender": sender, "text": text}
            for key, date, sender, text in emails
        ]
        raw_b64 = base64.b64encode(Path(DEFAULT_XLSX).read_bytes()).decode("ascii")
        with patch("app.load_case_database", return_value=workbook):
            status, upload = self._post_url("/api/upload-xlsx", {"data_base64": raw_b64, "use_ai": True})
        self.assertEqual(status, 200)
        review = {"review_id": upload["review_id"]}
        self.assertEqual(upload["data"]["items"][0]["status_code"], "NEEDS_REVIEW")
        self.assertEqual(upload["data"]["items"][3]["payable_amount"], 4000)

        with patch("xlsx_review.suggest_material_word", side_effect=ModelUnavailable("Ollama is unavailable")):
            status, offline = self._post_url("/api/xlsx-review", review)
        self.assertEqual(status, 200)
        self.assertEqual(offline["ai_message"], "Ollama is unavailable")
        self.assertEqual(offline["data"], upload["data"])

        extraction = {
            "invoice": "215", "order": "PO-13", "material": "berry pouch 500 g",
            "quantity": "4000", "unit": "peice", "price": "4", "total": "16,000",
        }
        with patch("xlsx_review.suggest_material_word", return_value=("adhesion", "adhesive")) as matcher:
            with patch("ai_extract._model_response", return_value=extraction) as model:
                status, enriched = self._post_url("/api/xlsx-review", review)
        self.assertEqual(status, 200)
        matcher.assert_called_once()
        model.assert_called_once()
        items = enriched["data"]["items"]
        self.assertEqual(items[0]["material_mapping"], {"source": "adhesion", "target": "adhesive", "method": "ai"})
        self.assertEqual(items[0]["payable_amount"], 950)
        self.assertEqual(items[1]["status_code"], "NEEDS_REVIEW")
        self.assertIsNone(items[1]["material_mapping"])
        self.assertEqual(items[2]["payable_amount"], 0)
        self.assertEqual(set(enriched["proposals"]), {"E-103"})
        self.assertEqual(enriched["proposals"]["E-103"]["fields"]["unit"]["source"], "peice")

        request = {**review, "invoice_id": "E-103"}
        self.assertEqual(self._post_url("/api/xlsx-review", request)[0], 400)
        request["ai_confirmed"] = True
        self.assertEqual(self._post_url("/api/xlsx-review", {**request, "invoice_id": "E-104"})[0], 400)
        status, updated = self._post_url("/api/xlsx-review", request)
        self.assertEqual(status, 200)
        items = updated["data"]["items"]
        self.assertEqual(items[2]["payable_amount"], 16000)
        self.assertEqual(items[3]["status_code"], "DUPLICATE_OR_REPLACED")
        self.assertEqual(updated["proposals"], {})
        self.assertEqual(self._post_url("/api/xlsx-review", request), (200, updated))

        new_email = {
            **review, "sender": "PackLine Supply", "received_at": "16.11 14:00",
            "text": "Invoice 217 under order PO-13: berry pouch 500 g, 1,000 pcs at 4 USD. Total 4,000 USD.",
        }
        status, result = self._post_url("/api/analyze-custom", new_email)
        self.assertEqual(status, 200)
        self.assertEqual(result["item"]["status_code"], "DUPLICATE_OR_REPLACED")
        self.assertIn("E-103", result["item"]["primary_reason"])

    def test_ai_extraction_requires_confirmation_and_uses_case_rules(self):
        text = "Invoice 215 under order PO-13: berry pouch 500 g. Shipped 4000 peice. Each — 4 dollars. Amount due — 16,000 dollars."
        data = {"sender": "PackLine Supply", "received_at": "16.11 14:25", "text": text}
        model_output = {
            "invoice": "215", "order": "PO-13", "material": "berry pouch 500 g",
            "quantity": "4000", "unit": "peice", "price": "4", "total": "16,000",
        }
        status, baseline = self._post_url("/api/analyze-custom", data)
        self.assertEqual(status, 200)
        self.assertEqual(baseline["item"]["status_code"], "NEEDS_REVIEW")
        with patch("ai_extract._model_response", return_value=model_output):
            status, suggestion = self._post_url("/api/extract-ai", {"text": text})
        self.assertEqual(status, 200)
        self.assertEqual(suggestion["fields"]["unit"]["value"], "pcs")
        self.assertEqual(suggestion["fields"]["unit"]["source"], "peice")
        self.assertNotIn("item", suggestion)

        pending = dict(data, ai_token=suggestion["token"])
        self.assertEqual(self._post_url("/api/analyze-custom", pending)[0], 400)
        confirmed = dict(pending, ai_confirmed=True)
        self.assertEqual(self._post_url("/api/analyze-custom", dict(confirmed, text=text + " Modified."))[0], 400)
        self.assertEqual(self._post_url("/api/analyze-custom", dict(confirmed, ai_token=suggestion["token"] + "x"))[0], 400)
        status, result = self._post_url("/api/analyze-custom", confirmed)
        self.assertEqual(status, 200)
        self.assertEqual(result["item"]["status_code"], "READY_TO_PAY")
        self.assertEqual(result["item"]["payable_amount"], 16000)

        ambiguous = text + " Linkage to PO-06 is still being clarified."
        with patch("ai_extract._model_response", return_value=model_output):
            _, suggestion = self._post_url("/api/extract-ai", {"text": ambiguous})
        status, result = self._post_url(
            "/api/analyze-custom", dict(confirmed, text=ambiguous, ai_token=suggestion["token"]),
        )
        self.assertEqual(status, 200)
        self.assertEqual(result["item"]["status_code"], "NEEDS_REVIEW")
        self.assertIn("Multiple purchase orders", result["item"]["primary_reason"])

    def test_ai_normalizes_misspelled_unit_in_current_text_only(self):
        text = "Invoice 205 under order PO-818: Sintered nozzle 19×45 mm. Shipped 20 piecs. Each — 847.50 USD."
        old = "\nQuote from email: Total 99,999 USD."
        model_output = {
            "invoice": "205", "order": "PO-818", "material": "Sintered nozzle 19×45 mm",
            "quantity": "20", "unit": "piecs", "price": "847.50", "total": "99,999",
        }
        with patch("ai_extract._model_response", return_value=model_output) as model:
            status, result = self._post_url("/api/extract-ai", {"text": text + old})
        self.assertEqual(status, 200)
        self.assertEqual(model.call_args.args[0], text)
        self.assertEqual(result["fields"]["unit"]["source"], "piecs")
        self.assertEqual(result["fields"]["unit"]["value"], "pcs")
        self.assertNotIn("total", result["fields"])

    def test_ai_discards_unquoted_values_and_reports_outage(self):
        text = "Invoice 215 under order PO-13: berry pouch 500 g, 4 000 peice."
        model_output = {
            "invoice": "215", "order": "PO-13", "material": "berry pouch 500 g",
            "quantity": "4 000", "unit": "peice", "price": "4", "total": "16000",
        }
        with patch("ai_extract._model_response", return_value=model_output):
            status, proposal = self._post_url("/api/extract-ai", {"text": text})
        self.assertEqual(status, 200)
        self.assertEqual(proposal["fields"]["quantity"]["value"], "4000")
        self.assertNotIn("price", proposal["fields"])
        self.assertNotIn("total", proposal["fields"])
        with patch("ai_extract._model_response", return_value=dict(model_output, price="16,000", total="16,000")):
            _, proposal = self._post_url("/api/extract-ai", {"text": text + " Amount due — 16,000 dollars."})
        self.assertEqual(proposal["fields"]["total"]["value"], "16000")
        self.assertNotIn("price", proposal["fields"])
        with patch("ai_extract._model_response", side_effect=ModelUnavailable("Ollama is unavailable.")):
            status, result = self._post_url("/api/extract-ai", {"text": text})
        self.assertEqual(status, 503)
        self.assertIn("Ollama", result["error"])

    def test_ordinary_parser_accepts_full_piece_alias(self):
        data = {
            "sender": "PackLine Supply", "received_at": "16.11 14:25",
            "text": "Invoice 215 under order PO-13: berry pouch 500 g, 4,000 pieces at 4 USD. Total 16,000 USD.",
        }
        status, result = self._post_url("/api/analyze-custom", data)
        self.assertEqual(status, 200)
        self.assertEqual(result["item"]["converted_unit"], "pcs")
        self.assertEqual(result["item"]["payable_amount"], 16000)

    def test_automatic_name_normalization_is_grounded_and_preserves_checks(self):
        from app import JURY_PRESETS

        preset = JURY_PRESETS[0]
        text = preset["text"].replace("adhesive tape", "adhesion tape")
        data = {key: preset[key] for key in ("sender", "received_at")}
        data.update(text=text, use_ai=True)
        with patch("ai_extract._request_model", return_value={"source": "adhesion", "target": "adhesive"}) as model:
            status, result = self._post_url("/api/analyze-custom", data)
        self.assertEqual(status, 200)
        self.assertEqual(result["item"]["payable_amount"], 22800)
        self.assertEqual(result["item"]["material_mapping"], {"source": "adhesion", "target": "adhesive", "method": "ai"})
        self.assertIsNone(result["proposal"])
        self.assertEqual(model.call_count, 1)
        with patch("ai_extract._request_model") as model:
            _, wrong_size = self._post_url("/api/analyze-custom", dict(data, text=text.replace("48 mm", "50 mm")))
        model.assert_not_called()
        self.assertEqual(wrong_size["item"]["status_code"], "NEEDS_REVIEW")
        self.assertIsNone(wrong_size["item"]["material_mapping"])

        with patch("ai_extract._request_model", return_value={"source": "cable", "target": "adhesive"}):
            _, different = self._post_url("/api/analyze-custom", dict(data, text=text.replace("adhesion", "cable")))
        self.assertEqual(different["item"]["status_code"], "NEEDS_REVIEW")

    def test_one_click_only_proposes_fields_missing_from_regular_extraction(self):
        text = "Invoice 215 under order PO-13: berry pouch 500 g. Shipped 4000 peice. Each — 4 dollars. Amount due — 16,000 dollars."
        model_output = {
            "invoice": "215", "order": "PO-13", "material": "berry pouch 500 g",
            "quantity": "4000", "unit": "peice", "price": "4", "total": "16,000",
        }
        data = {"sender": "PackLine Supply", "received_at": "16.11 14:25", "text": text, "use_ai": True}
        with patch("ai_extract._model_response", return_value=model_output):
            status, result = self._post_url("/api/analyze-custom", data)
        self.assertEqual(status, 200)
        self.assertEqual(result["item"]["status_code"], "NEEDS_REVIEW")
        self.assertEqual(set(result["proposal"]["fields"]), {"quantity", "unit", "price", "total"})
        token = result["proposal"]["token"]
        status, confirmed = self._post_url("/api/analyze-custom", dict(data, ai_token=token, ai_confirmed=True))
        self.assertEqual(status, 200)
        self.assertEqual(confirmed["item"]["payable_amount"], 16000)
        self.assertEqual(confirmed["item"]["unit_mapping"]["source"], "peice")
        self.assertEqual(confirmed["item"]["unit_mapping"]["target"], "pcs")
        self.assertIsNone(confirmed["proposal"])
