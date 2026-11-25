import copy
import io
import json
import zipfile
from pathlib import Path
import unittest
from unittest.mock import patch

from engine import analyze_all_emails, analyze_single_custom_email, load_case_database
from app import DEFAULT_XLSX, JURY_PRESETS

FIXTURES = json.loads((Path(__file__).parent / 'fixtures/audit_cases.json').read_text())


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.db = load_case_database(DEFAULT_XLSX)

    def custom(self, sender, text, received_at='16.11 14:30'):
        return analyze_single_custom_email(DEFAULT_XLSX, sender, text, received_at)

    def run_db(self, db=None):
        return analyze_all_emails(db or self.db)

    def test_source_documents_status_amounts_and_risks(self):
        groups = {
            'READY_TO_PAY': [1, 2, 4, 5, 6, 8, 9, 12],
            'DUPLICATE_OR_REPLACED': [3, 14, 18, 22, 23],
            'CRITICAL_REQUISITES': [16, 25],
            'PRICE_OR_QTY_UNAPPROVED': [10, 13, 21, 24],
            'MATH_ERROR': [15], 'NOT_ACCEPTED_YET': [7, 17], 'INFO_LETTER': [11, 19, 20],
        }
        statuses = {f'E-{n:02}': status for status, numbers in groups.items() for n in numbers}
        payable = {1: 44000, 2: 15000, 4: 34200, 5: 14000, 6: 36000, 8: 55000, 9: 32500, 12: 15000}
        risks = {3: 36000, 7: 8000, 10: 1200, 13: 4500, 14: 15000, 15: 1000, 16: 40000,
                 17: 72000, 18: 40000, 21: 1600, 22: 32500, 23: 8000, 24: 480, 25: 14000}
        result = self.run_db()
        self.assertEqual(len(result['items']), 25)
        for item in result['items']:
            with self.subTest(document=item['id']):
                n = int(item['id'][2:])
                self.assertEqual(item['status_code'], statuses[item['id']])
                self.assertEqual(item['payable_amount'], payable.get(n, 0))
                self.assertEqual(item['prevented_risk'], risks.get(n, 0))
        self.assertEqual(result['summary']['total_payable_rub'], 245700)
        self.assertEqual(result['summary']['total_prevented_risk_rub'], 274280)

    def test_demo_examples(self):
        for example, status in zip(JURY_PRESETS, ['READY_TO_PAY', 'READY_TO_PAY', 'DUPLICATE_OR_REPLACED', 'CRITICAL_REQUISITES', 'MATH_ERROR']):
            with self.subTest(example=example['title']):
                result = self.custom(example['sender'], example['text'], example['received_at'])
                self.assertEqual(result['status_code'], status)

    def test_audit_regressions(self):
        for case in FIXTURES:
            with self.subTest(case=case['id']):
                result = self.custom(case['sender'], case['text'], case['received_at'])
                self.assertEqual(result['status_code'], case['expected_status'])
                self.assertEqual(result['payable_amount'], case['expected_payable'])

    def test_only_latest_corrected_version_is_active_even_when_rows_shuffled(self):
        self.db['emails'].append(dict(self.db['emails'][5], id='LATEST', received_at='16.11 14:30'))
        self.db['emails'].reverse()
        results = {r['id']: r for r in self.run_db()['items']}
        self.assertEqual(results['LATEST']['payable_amount'], 36000)
        for previous in ('E-03', 'E-06'):
            self.assertEqual(results[previous]['status_code'], 'DUPLICATE_OR_REPLACED')
            self.assertEqual(results[previous]['payable_amount'], 0)
        self.assertEqual(sum(r['payable_amount'] for r in results.values() if r['order_id'] == 'PO-03'), 36000)

    def test_correction_does_not_consume_receipt_twice(self):
        example = JURY_PRESETS[0]
        self.db['emails'].append(dict(id='FIRST', sender=example['sender'], text=example['text'], received_at='16.11 14:30'))
        self.db['emails'].append(dict(id='LATEST', sender=example['sender'], text=example['text'], received_at='16.11 15:30'))
        result = self.run_db()
        ready = [r for r in result['items'] if r['order_id'] == 'PO-08' and r['status_code'] == 'READY_TO_PAY']
        self.assertEqual({r['id'] for r in ready}, {'E-04', 'LATEST'})
        self.assertEqual(sum(r['payable_amount'] for r in ready), 57000)

    def test_new_corrected_number_cannot_bypass_order_limit(self):
        r = self.custom('NordLabel Ltd., billing@nordlabel.example', 'Corrected invoice 999 under PO-12: ribbon 110 mm × 300 m, 50 rolls at 650 USD. Total 32,500 USD.')
        self.assertEqual(r['status_code'], 'DUPLICATE_OR_REPLACED')
        self.assertEqual(r['payable_amount'], 0)

    def test_signed_price_replaces_old_erp_price(self):
        example = FIXTURES[4]
        r = self.custom(example['sender'], example['text'].replace('at 6 USD', 'at 5 USD').replace('60,000', '50,000'))
        self.assertEqual(r['status_code'], 'PRICE_OR_QTY_UNAPPROVED')
        self.assertIn('5.5', r['primary_reason'])
        self.assertEqual(r['payable_amount'], 0)
        self.assertEqual(r['prevented_risk'], 0)

    def test_quantity_only_approval_does_not_authorize_other_price(self):
        r = self.custom('NordLabel Ltd.', 'Corrected invoice 117 under PO-12: ribbon 110 mm × 300 m, 50 rolls at 700 USD. Total 35,000 USD.')
        self.assertEqual(r['status_code'], 'PRICE_OR_QTY_UNAPPROVED')

    def test_approval_effective_date_uses_the_year_of_the_receipt(self):
        order = self.db["orders"]["PO-09"]
        order["last_acceptance_date"] = "13.11.2027"
        email = next(row for row in self.db["emails"] if row["id"] == "E-13")
        email["received_at"] = "16.11.2027 10:00"
        result = self.run_db()
        item = next(row for row in result["items"] if row["id"] == "E-13")
        self.assertEqual(item["status_code"], "READY_TO_PAY")
        self.assertEqual(item["payable_amount"], 67500)
        self.assertTrue(any("$225/kg" in check["detail"] for check in item["rule_checks"]))

    def test_empty_order_sheet_does_not_import_sample_orders_into_the_book(self):
        sheets = {
            "Invoices and Emails": [[
                "E-01", "16.11 10:00", "PackLine Supply",
                "Invoice 901 under order PO-06: pouch 300 g, 5,000 pcs at 3.00 USD. Total 15,000 USD.",
            ]],
            "Orders and Receipts": [],
            "Approvals": [],
            "Rules": [["R-1", "Matching", "Find purchase order in the export."]],
        }
        with patch("engine.read_xlsx_sheets", return_value=sheets):
            db = load_case_database("custom.xlsx", fallback_xlsx_path=DEFAULT_XLSX)
        self.assertEqual(db["orders"], {})
        item = analyze_all_emails(db)["items"][0]
        self.assertEqual(item["status_code"], "NEEDS_REVIEW")
        self.assertEqual(item["payable_amount"], 0)

    def test_receipt_can_cover_a_new_batch_after_actual_acceptance(self):
        self.db['orders']['PO-07']['accepted_qty'] = 12000
        case = FIXTURES[5]
        self.db['emails'].append(dict(id='NEW', sender=case['sender'], text=case['text'], received_at=case['received_at']))
        self.assertEqual(self.run_db()['items'][-1]['payable_amount'], 3000)

    def test_unknown_explicit_order_never_falls_back_to_similar_known_order(self):
        example = JURY_PRESETS[0]
        r = self.custom(example['sender'], example['text'].replace('PO-08', 'PO-99'))
        self.assertEqual(r['status_code'], 'NEEDS_REVIEW')
        self.assertEqual(r['order_id'], '—')

    def test_multiple_order_numbers_require_review_in_bulk(self):
        sample = JURY_PRESETS[0]
        text = sample["text"] + " Also discussed PO–07."
        self.db["emails"].append({
            "id": "E-90", "text": text, "sender": sample["sender"], "received_at": sample["received_at"],
        })
        item = self.run_db()["items"][-1]
        self.assertEqual((item["status_code"], item["payable_amount"]), ("NEEDS_REVIEW", 0))
        self.assertIn("Multiple purchase orders", item["primary_reason"])

    def test_current_invoice_does_not_use_quoted_prices_or_orders(self):
        sample = JURY_PRESETS[0]
        old = "Invoice 52 under order PO-08: adhesive tape 48 mm × 66 m, 240 rolls at 97 USD. Total 23,280 USD."
        for prefix in ("Previous version from quote: ", "Quote from email: ", "> "):
            with self.subTest(prefix=prefix):
                item = self.custom(sample["sender"], sample["text"] + "\n" + prefix + old + " PO-07.", sample["received_at"])
                self.assertEqual((item["status_code"], item["payable_amount"]), ("READY_TO_PAY", 22800))
        ambiguous = self.custom(sample["sender"], sample["text"] + "\n" + old, sample["received_at"])
        self.assertEqual((ambiguous["status_code"], ambiguous["payable_amount"]), ("NEEDS_REVIEW", 0))
        self.assertIn("Multiple line items", ambiguous["primary_reason"])

    def test_microlitres_are_distinct_from_millilitres(self):
        self.db["orders"]["PO-80"] = {
            "order_id": "PO-80", "supplier": "LabSupply Inc.", "supplier_clean": "labsupply",
            "material": "Glass pipette 250 ul", "unit": "pcs", "buyer": "Buyer",
            "ordered_qty": 30.0, "accepted_qty": 30.0, "order_price": 100.0,
            "approval_id": "", "last_acceptance_date": "15.11.2026",
        }
        self.db["emails"] = [
            {"id": f"E-{i}", "received_at": "16.11 12:00", "sender": "LabSupply Inc.",
             "text": f"Invoice {i} under PO-80: Glass pipette {volume}, 1 pcs at 100 USD. Total 100 USD."}
            for i, volume in enumerate(("250 ml", "0.25 ml"), 91)
        ]
        mismatch, equivalent = self.run_db()["items"]
        self.assertEqual(mismatch["status_code"], "NEEDS_REVIEW")
        self.assertIn("specification mismatch", mismatch["primary_reason"])
        self.assertEqual((equivalent["status_code"], equivalent["payable_amount"]), ("READY_TO_PAY", 100))

    def test_ambiguous_order_requires_review(self):
        self.db['orders']['PO-98'] = dict(self.db['orders']['PO-10'], order_id='PO-98')
        r = self.run_db()['items'][0]
        self.assertEqual(r['status_code'], 'NEEDS_REVIEW')

    def test_drafts_contain_current_facts(self):
        case = FIXTURES[9]
        r = self.custom(case['sender'], case['text'])
        body = r['actions'][0]['body']
        self.assertIn('125', body)
        self.assertIn('16.11 14:30', body)
        self.assertNotIn('adhesive tape', body)
        self.assertNotIn('14.11', body)
        case = FIXTURES[5]
        r = self.custom(case['sender'], case['text'])
        self.assertNotIn('800 pcs', r['next_step'])
        self.assertNotIn('AP-03', r['actions'][0]['body'])

    def test_requisites_variants_need_manual_confirmation(self):
        case = FIXTURES[8]
        for phrase in ('Payment recipient is now Factor LLC.', 'Wire funds to Acct No. 40702810000000000555.', 'Pay using the new financial agent bank details.'):
            with self.subTest(phrase=phrase):
                r = self.custom(case['sender'], case['text'] + ' ' + phrase)
                self.assertEqual(r['status_code'], 'CRITICAL_REQUISITES')

    def test_zero_negative_and_missing_values_are_not_payable(self):
        case = FIXTURES[8]
        for text in (case['text'].replace('240 rolls', '0 rolls').replace('22,800', '0'),
                     case['text'].replace('240 rolls', '-240 rolls'),
                     case['text'].replace('Total 22,800 USD.', ''),
                     'Invoice 999 under PO-08.'):
            with self.subTest(text=text):
                r = self.custom(case['sender'], text)
                self.assertEqual(r['status_code'], 'NEEDS_REVIEW')
                self.assertEqual(r['payable_amount'], 0)

    def test_same_dimensions_do_not_identify_another_material(self):
        r = self.custom('Timber Pallet Co.', 'Corrected invoice 91 under PO-10: cable 1200x1000, 40 pcs at 1,100 USD. Total 44,000 USD.')
        self.assertEqual(r['status_code'], 'NEEDS_REVIEW')

    def test_material_spelling_variants_and_typos_are_recognized(self):
        r = self.custom(
            'Ladoga Film Corp., sales@ladogafilm.example',
            'Corrected invoice 48: strech film 17 um, 15 bags of 20 kg, bag price 4,200 USD. Total 63,000 USD. Reference: your order dated 05.11.',
            '16.11 16:20',
        )
        self.assertEqual(r['order_id'], 'PO-09')
        self.assertEqual(r['status_code'], 'READY_TO_PAY')
        self.assertEqual(r['payable_amount'], 63000)

        r_typo = self.custom(
            'NordLabel Ltd., billing@nordlabel.example',
            'Corrected invoice 117 under PO-12: ribon 110 mm × 300 m, 50 rolls at 650 USD. Total 32,500 USD.',
            '16.11 16:25',
        )
        self.assertEqual(r_typo['status_code'], 'READY_TO_PAY')
        self.assertEqual(r_typo['payable_amount'], 32500)

    def test_typo_in_multiword_material_requires_matching_dimensions(self):
        preset = JURY_PRESETS[0]
        text = preset['text'].replace('adhesive', 'adhesve')
        result = self.custom(preset['sender'], text, preset['received_at'])
        self.assertEqual(result['status_code'], 'READY_TO_PAY')
        self.assertEqual(result['payable_amount'], 22800)
        self.assertTrue(any('"adhesve" → "adhesive"' in check['detail'] for check in result['rule_checks']))

        for size in ('50 mm × 66 m', '48 cm × 66 m', '48 mm × 55 m'):
            with self.subTest(size=size):
                wrong = self.custom(preset['sender'], text.replace('48 mm × 66 m', size), preset['received_at'])
                self.assertEqual(wrong['status_code'], 'NEEDS_REVIEW')
                self.assertEqual(wrong['payable_amount'], 0)
                self.assertIn('Dimension mismatch', wrong['primary_reason'])

    def test_arbitrary_new_materials_in_custom_db(self):
        custom_db = copy.deepcopy(self.db)
        custom_db['orders']['PO-90'] = {
            'order_id': 'PO-90',
            'order_date': '15.11.2026',
            'supplier': 'ContainerPro LLC',
            'supplier_clean': 'containerpro',
            'buyer': 'Owen Miller',
            'material': 'Plastic barrel 200 L',
            'unit': 'pcs',
            'ordered_qty': 10.0,
            'accepted_qty': 10.0,
            'last_acceptance_date': '16.11.2026',
            'order_price': 1500.0,
            'approval_id': '',
        }
        custom_db['emails'] = [
            {
                'id': 'E-01',
                'received_at': '16.11 12:00',
                'sender': 'ContainerPro LLC, info@containerpro.example',
                'text': 'Invoice 501 under order PO-90: plastic barrels 200 L, 10 pcs at 1,500 USD. Total 15,000 USD.',
            },
            {
                'id': 'E-02',
                'received_at': '16.11 12:30',
                'sender': 'ContainerPro LLC, info@containerpro.example',
                'text': 'Invoice 502 under order PO-90: plastic barrel 50 L, 10 pcs at 1,500 USD. Total 15,000 USD.',
            },
        ]
        res = analyze_all_emails(custom_db)
        self.assertEqual(res['items'][0]['status_code'], 'READY_TO_PAY')
        self.assertEqual(res['items'][0]['payable_amount'], 15000)
        self.assertEqual(res['items'][1]['status_code'], 'NEEDS_REVIEW')

        first = custom_db['emails'][0]
        correct_text = first['text'].replace('plastic barrels', 'plastic barrel')
        for material in ('plastic barerl', 'plstic barrel'):
            with self.subTest(material=material):
                first['text'] = correct_text.replace('plastic barrel', material)
                result = analyze_all_emails(custom_db)['items'][0]
                self.assertEqual(result['status_code'], 'READY_TO_PAY')
                self.assertTrue(any('Typo recognized' in check['detail'] for check in result['rule_checks']))

        first['text'] = correct_text.replace('plastic', 'metallic')
        result = analyze_all_emails(custom_db)['items'][0]
        self.assertEqual(result['status_code'], 'NEEDS_REVIEW')

    def test_new_analysis_does_not_mutate_workbook_queue(self):
        self.custom(FIXTURES[8]['sender'], FIXTURES[8]['text'])
        self.assertEqual(len(load_case_database(DEFAULT_XLSX)['emails']), 25)

    def test_ready_results_include_mandatory_checks_and_pending_treasury(self):
        for r in self.run_db()['items']:
            if r['status_code'] != 'READY_TO_PAY':
                continue
            self.assertEqual(set(r['triggered_rules']), {f'R-{i}' for i in range(1, 10)})
            self.assertFalse(any(c['status'] == 'error' for c in r['rule_checks']))
            self.assertEqual(r['rule_checks'][-1]['status'], 'warn')

    def test_custom_xlsx_with_sparse_cells_and_fallback_orders(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as z:
            z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/></Types>')
            z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
            z.writestr('xl/workbook.xml', '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Emails" sheetId="1" r:id="rId1"/></sheets></workbook>')
            z.writestr('xl/_rels/workbook.xml.rels', '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
            z.writestr(
                'xl/worksheets/sheet1.xml',
                '<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
                '<row r="1"><c r="A1" t="inlineStr"><is><t>ID</t></is></c><c r="B1" t="inlineStr"><is><t>Received</t></is></c><c r="C1" t="inlineStr"><is><t>Sender</t></is></c><c r="D1" t="inlineStr"><is><t>Email Text</t></is></c></row>'
                '<row r="2"><c r="B2" t="inlineStr"><is><t>16.11 10:00</t></is></c><c r="C2" t="inlineStr"><is><t>PackLine Supply</t></is></c><c r="D2" t="inlineStr"><is><t>Invoice 901 under order PO-06: pouch 300 g, 5,000 pcs at 3.00 USD. Total 15,000 USD.</t></is></c></row>'
                '</sheetData></worksheet>'
            )
        buf.seek(0)
        db = load_case_database(buf, fallback_xlsx_path=DEFAULT_XLSX)
        self.assertEqual(len(db['emails']), 1)
        self.assertEqual(db['emails'][0]['id'], 'E-01')
        self.assertEqual(db['emails'][0]['received_at'], '16.11 10:00')
        self.assertEqual(len(db['orders']), 14)
        res = analyze_all_emails(db)
        self.assertEqual(res['items'][0]['status_code'], 'READY_TO_PAY')
        self.assertEqual(res['items'][0]['payable_amount'], 15000)
