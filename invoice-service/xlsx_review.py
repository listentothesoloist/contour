"""Session-local AI review of invoices from an imported workbook."""

from threading import Lock
from time import monotonic
from uuid import uuid4

from ai_extract import ModelUnavailable, confirmed_fields, extract_invoice, suggest_material_word
from engine import analyze_all_emails, analyze_new_email


class WorkbookReview:
    def __init__(self, db, analysis):
        self.db = db
        self.analysis = analysis
        self.confirmed = {}
        self.extractions = {}
        self.material_matches = {}
        self.model_error = None
        self.reviewed = False
        self.lock = Lock()

    def _advise_material(self, _email_id, invoice_material, order_material):
        key = (invoice_material, order_material)
        if key not in self.material_matches and not self.model_error:
            try:
                self.material_matches[key] = suggest_material_word(*key)
            except ModelUnavailable as error:
                self.model_error = str(error)
        return self.material_matches.get(key)

    def _pending_fields(self):
        proposals = {}
        for item in self.analysis["items"]:
            missing = set(item["missing_extraction"])
            extraction = self.extractions.get(item["id"])
            if not missing or not extraction:
                continue
            if "quantity" in missing:
                missing.update(("quantity", "unit", "price", "material"))
            fields = extraction["fields"]
            if missing <= fields.keys():
                proposals[item["id"]] = {
                    "model": extraction["model"],
                    "fields": {key: field for key, field in fields.items() if key in missing},
                }
        return proposals

    def run(self, invoice_id=None):
        with self.lock:
            if invoice_id is not None:
                self._confirm(invoice_id)
            elif not self.reviewed or self.model_error:
                self._review()
            return {
                "data": self.analysis,
                "proposals": self._pending_fields(),
                "ai_message": self.model_error,
            }

    def check_email(self, **values):
        with self.lock:
            confirmed = self.confirmed.copy()
            material_matches = self.material_matches.copy()

        def cached_advice(_email_id, invoice_material, order_material):
            return material_matches.get((invoice_material, order_material))

        return analyze_new_email(
            self.db, **values, workbook_fields=confirmed, workbook_advisor=cached_advice
        )

    def _review(self):
        self.model_error = None
        self.analysis = analyze_all_emails(self.db, self.confirmed, self._advise_material)
        for item in self.analysis["items"]:
            if self.model_error:
                break
            key = item["id"]
            if not item["missing_extraction"] or key in self.extractions:
                continue
            try:
                extraction = extract_invoice(item["text"])
                token = extraction.pop("token")
                extraction["values"] = confirmed_fields(item["text"], token) if token else {}
                self.extractions[key] = extraction
            except ModelUnavailable as error:
                self.model_error = str(error)
            except ValueError:
                # A row outside the model's supported input stays in manual review.
                self.extractions[key] = None
        self.reviewed = True

    def _confirm(self, invoice_id):
        if invoice_id in self.confirmed:
            return
        proposal = self._pending_fields().get(invoice_id)
        if not proposal:
            raise ValueError("There are no fields pending confirmation for this invoice. Refresh the AI review result.")
        extraction = self.extractions[invoice_id]
        allowed = set(proposal["fields"])
        if "unit" in allowed:
            allowed.add("unit_source")
        values = {key: value for key, value in extraction["values"].items() if key in allowed}
        confirmed = {**self.confirmed, invoice_id: values}

        self.analysis = analyze_all_emails(self.db, confirmed, self._advise_material)
        self.confirmed = confirmed


class WorkbookReviews:
    """Keep uploads and confirmations in memory for one hour of inactivity."""

    def __init__(self):
        self.entries = {}
        self.lock = Lock()

    def _prune(self, now):
        expired = [key for key, (last_used, _) in self.entries.items() if now - last_used >= 3600]
        for key in expired:
            del self.entries[key]

    def add(self, db, analysis):
        review_id = uuid4().hex
        with self.lock:
            now = monotonic()
            self._prune(now)
            self.entries[review_id] = (now, WorkbookReview(db, analysis))
        return review_id

    def get(self, review_id):
        with self.lock:
            now = monotonic()
            self._prune(now)
            if review_id not in self.entries:
                return None
            review = self.entries[review_id][1]
            self.entries[review_id] = (now, review)
            return review
