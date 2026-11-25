#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core invoice reconciliation engine for North Berry: Smart 3-Way Match (Case 04 Target AI Fest 2026).

Combines:
1. NLP parser for incoming emails and invoices (entity extraction, material synonym normalization,
   compound packaging detection, and unit conversion per R-7).
2. Deterministic rule engine enforcing all 9 accounting reconciliation rules (R-1 ... R-9)
   against ERP exports ("Orders and Receipts") and Directum RX ("Approvals").
3. Automatic issue routing and draft inquiry generation per R-9.
"""

from __future__ import annotations

import json
import os
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import date, datetime
from decimal import Decimal
from difflib import SequenceMatcher
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple


# ---------------------------------------------------------------------------
# 1. Dependency-free .xlsx reader (Python standard library only)
# ---------------------------------------------------------------------------

NS_MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
NS_REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def _col_ref_to_idx(ref: str) -> Optional[int]:
    """Convert an Excel cell coordinate (e.g. 'C12') to a 0-based column index."""
    m = re.match(r"^([A-Za-z]+)\d+$", (ref or "").strip())
    if not m:
        return None
    idx = 0
    for ch in m.group(1).upper():
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx - 1


def read_xlsx_sheets(xlsx_path: Any) -> Dict[str, List[List[str]]]:
    """Read all worksheets of an Excel workbook (.xlsx) into {sheet_name: rows}."""
    sheets_data: Dict[str, List[List[str]]] = {}
    with zipfile.ZipFile(xlsx_path, "r") as z:
        shared_strings: List[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            ss_root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in ss_root.findall(f"{NS_MAIN}si"):
                texts = [t.text or "" for t in si.iter(f"{NS_MAIN}t")]
                shared_strings.append("".join(texts))

        wb_root = ET.fromstring(z.read("xl/workbook.xml"))
        rels_root = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rel_map = {r.attrib["Id"]: r.attrib["Target"] for r in rels_root}

        for sh in wb_root.iter(f"{NS_MAIN}sheet"):
            name = sh.attrib.get("name", "")
            rid = sh.attrib.get(f"{NS_REL}id", "")
            target = rel_map.get(rid, "").lstrip("/")
            if not target:
                continue
            if not target.startswith("xl/"):
                target = "xl/" + target
            if target not in z.namelist():
                continue
            sroot = ET.fromstring(z.read(target))
            rows: List[List[str]] = []
            for row in sroot.iter(f"{NS_MAIN}row"):
                vals: List[str] = []
                for c in row:
                    col_idx = _col_ref_to_idx(c.attrib.get("r", ""))
                    t = c.attrib.get("t")
                    v = c.find(f"{NS_MAIN}v")
                    is_el = c.find(f"{NS_MAIN}is")
                    if t == "s" and v is not None and v.text is not None:
                        cell_val = shared_strings[int(v.text)].strip()
                    elif t == "inlineStr" and is_el is not None:
                        texts = [x.text or "" for x in is_el.iter(f"{NS_MAIN}t")]
                        cell_val = "".join(texts).strip()
                    elif v is not None and v.text is not None:
                        cell_val = v.text.strip()
                    else:
                        cell_val = ""
                    if col_idx is not None:
                        while len(vals) < col_idx:
                            vals.append("")
                        if col_idx < len(vals):
                            vals[col_idx] = cell_val
                        else:
                            vals.append(cell_val)
                    else:
                        vals.append(cell_val)
                if any(vals):
                    rows.append(vals)
            sheets_data[name] = rows
    return sheets_data


# ---------------------------------------------------------------------------
# 2. North Berry domain helpers
# ---------------------------------------------------------------------------

def parse_float(val: str) -> float:
    if not val:
        return 0.0
    cleaned = val.replace("\xa0", "").replace("\u202f", "").replace(" ", "")
    cleaned = re.sub(r"[^\d.,\-]", "", cleaned)
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        if re.fullmatch(r"-?\d{1,3}(?:,\d{3})+", cleaned):
            cleaned = cleaned.replace(",", "")
        else:
            cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def format_amount(value: float) -> str:
    return f"{value:,.2f}"


def parse_date_ddmm(date_str: str) -> Optional[Tuple[int, int]]:
    """Extract (day, month) from strings such as '13.11.2026' or '09.11 15:40'."""
    m = re.search(r"\b(\d{2})\.(\d{2})(?:\.2026)?\b", date_str or "")
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def parse_case_date(value: str) -> Optional[date]:
    """Use the year of the case only for dates supplied without a year."""
    match = re.fullmatch(r"(\d{2})\.(\d{2})(?:\.(\d{4}))?", value.strip())
    if not match:
        return None
    day, month, year = match.groups()
    try:
        return date(int(year or "2026"), int(month), int(day))
    except ValueError:
        return None


def clean_company_name(raw: str) -> str:
    """Normalize a company name for comparison (strip quotes, emails, and legal suffixes)."""
    s = raw.strip()
    s = re.sub(r'["\'«»]', "", s).split(",")[0].strip().lower()
    s = re.sub(r"\b(?:llc|inc|ltd|corp|co)\.?$", "", s).strip()
    return s


MATERIAL_SYNONYMS = [
    ("shipping carton", ["shipping carton", "corrugated carton", "corrugated box", "carton"]),
    ("berry pouch 1 kg", ["berry pouch 1 kg", "berry bag 1 kg", "pouch 1 kg", "bag 1 kg"]),
    ("berry pouch 300 g", ["berry pouch 300 g", "berry bag 300 g", "pouch 300 g", "bag 300 g"]),
    ("berry pouch 500 g", ["berry pouch 500 g", "berry bag 500 g", "pouch 500 g", "bag 500 g"]),
    ("liner bag", ["pe liner bag", "liner bag", "liner"]),
    ("pe film", ["pe film", "polyethylene film"]),
    ("stretch film", ["stretch film", "stretch", "strech"]),
    ("cold-resistant label", ["cold-resistant label", "freezer label"]),
    ("thermal label", ["thermal label", "thermo label"]),
    ("adhesive tape", ["packing adhesive tape", "adhesive tape", "packing tape", "scotch tape"]),
    ("thermal transfer ribbon", ["ribbon", "thermal transfer ribbon"]),
    ("pallet", ["wooden pallet", "pallet"]),
    ("cardboard pad", ["cardboard pad", "corrugated pad", "pad"]),
]


_LENGTH_IN_MM = {"mm": 1, "cm": 10, "m": 1000}
_DIMENSION_AXIS = r"(\d+(?:\.\d+)?)(?:\s*(mm|cm|m)\b)?"
_DIMENSION_GROUP = re.compile(rf"(?<![\d.,]){_DIMENSION_AXIS}(?:\s*[x×]\s*{_DIMENSION_AXIS}){{1,2}}", re.I)


def extract_dimensions(text: str) -> set:
    dimensions = set()
    for group in _DIMENSION_GROUP.finditer(text.lower()):
        axes = re.findall(_DIMENSION_AXIS, group.group())
        common_unit = axes[-1][1] if all(not unit for _, unit in axes[:-1]) else ""
        dimensions.add(tuple((Decimal(value), unit or common_unit) for value, unit in axes))
    return dimensions


def _dimensions_agree(first, second) -> bool:
    if len(first) != len(second):
        return False
    return all(
        value_a * _LENGTH_IN_MM[unit_a] == value_b * _LENGTH_IN_MM[unit_b] if unit_a and unit_b else value_a == value_b
        for (value_a, unit_a), (value_b, unit_b) in zip(first, second)
    )


_SPEC_UNITS = {
    "kg": ("mass", 1000), "g": ("mass", 1),
    "l": ("volume", 1_000_000), "ml": ("volume", 1000), "ul": ("volume", 1),
    "um": ("thickness", 1), "micron": ("thickness", 1), "microns": ("thickness", 1),
}


def _extract_unit_specs(text: str) -> Dict[str, set]:
    """Compare explicitly stated weight, volume, and thickness in common units."""
    specs: Dict[str, set] = {}
    for value, unit in re.findall(r"(\d+(?:\.\d+)?)\s*(kg|g|um|microns?|ul|ml|l|liters?|litres?)\b", text.lower()):
        key = "l" if unit.startswith("lit") else unit
        kind, scale = _SPEC_UNITS[key]
        specs.setdefault(kind, set()).add(Decimal(value) * scale)
    return specs


def _en_stem(word: str) -> str:
    """Lightweight normalization of English suffixes for matching arbitrary materials."""
    w = word.lower()
    if len(w) <= 3:
        return w
    if w.endswith("ies") and len(w) >= 5:
        return w[:-3] + "y"
    if re.search(r"(?:ch|sh|x|z)es$", w):
        stripped = w[:-2]
    elif w.endswith("s") and not w.endswith(("ss", "us", "is")):
        stripped = w[:-1]
    else:
        stripped = w
    return stripped if len(stripped) >= 3 else w


_MATERIAL_STOPWORDS = {
    "invoice", "order", "under", "batch", "first", "second", "total", "price",
    "usd", "dollar", "dollars", "reference", "delivery", "item", "material",
    "corrected", "revised", "remaining", "your", "dated", "from", "with",
    "amount", "please", "shipped", "each", "packing",
}


def is_one_letter_typo(actual: str, expected: str, min_length: int = 5) -> bool:
    if min(len(actual), len(expected)) < min_length or abs(len(actual) - len(expected)) > 1:
        return False
    if len(actual) == len(expected):
        different = [i for i, (a, b) in enumerate(zip(actual, expected)) if a != b]
        if len(different) == 1:
            return True
        if len(different) == 2:
            left, right = different
            return right == left + 1 and actual[left] == expected[right] and actual[right] == expected[left]
        return False
    shorter, longer = sorted((actual, expected), key=len)
    first_difference = next((i for i, (a, b) in enumerate(zip(shorter, longer)) if a != b), len(shorter))
    return shorter[first_difference:] == longer[first_difference + 1:]


def _material_words(text: str) -> List[str]:
    return [w for w in re.findall(r"[a-z]{4,}", text) if w not in _MATERIAL_STOPWORDS]


def _material_typo(actual_words: List[str], order_words: List[str], specs_match: bool) -> Optional[Tuple[str, str]]:
    actual_stems = [_en_stem(word) for word in actual_words]
    missing = []
    for word in order_words:
        stem = _en_stem(word)
        if stem in actual_stems:
            i = actual_stems.index(stem)
            actual_stems.pop(i)
            actual_words.pop(i)
        else:
            missing.append(word)
    exact = len(order_words) - len(missing)
    if (not exact and not specs_match) or (exact + 1) * 3 < len(order_words) * 2:
        return None
    candidates = {(actual, expected) for expected in missing for actual in actual_words if is_one_letter_typo(actual, expected)}
    return next(iter(candidates)) if len(candidates) == 1 else None


class MaterialMatch(NamedTuple):
    score: float
    note: str
    words: Optional[Tuple[str, str]] = None
    conflict: bool = False


def match_material_similarity(text_a: str, text_b: str) -> MaterialMatch:
    """Evaluate semantic proximity between invoice material description and ERP item (R-7)."""
    a, b = text_a.lower(), text_b.lower()
    dims_a = set(extract_dimensions(a))
    dims_b = set(extract_dimensions(b))
    dim_match = bool(dims_a and dims_b and all(
        any(_dimensions_agree(a_dim, b_dim) for b_dim in dims_b) for a_dim in dims_a
    ) and all(
        any(_dimensions_agree(a_dim, b_dim) for a_dim in dims_a) for b_dim in dims_b
    ))
    if dims_a and dims_b and not dim_match:
        return MaterialMatch(0.0, "Dimension mismatch", conflict=True)

    specs_a, specs_b = _extract_unit_specs(a), _extract_unit_specs(b)
    if any(specs_a[kind].isdisjoint(specs_b[kind]) for kind in specs_a.keys() & specs_b.keys()):
        return MaterialMatch(0.0, "Material specification mismatch (weight/volume/thickness)", conflict=True)

    tokens_a = re.findall(r"[a-z0-9]{5,}", a)
    erp_matched_known_group = False
    for canonical, variants in MATERIAL_SYNONYMS:
        phrase_a = next((v for v in variants if re.search(rf"(?<!\w){re.escape(v)}(?!\w)", a)), None)
        phrase_b = next((v for v in variants if re.search(rf"(?<!\w){re.escape(v)}(?!\w)", b)), None)
        in_a = any(v in a for v in variants)
        in_b = any(v in b for v in variants)
        if in_b:
            erp_matched_known_group = True
        if in_a and in_b:
            note = f"Synonym recognized (\"{canonical}\")" if a != b else "Exact match"
            words = (phrase_a, phrase_b) if phrase_a and phrase_b and phrase_a != phrase_b else None
            return MaterialMatch(1.0 if dim_match or not dims_b else 0.9, note, words)
        if in_b:
            for v in variants:
                if " " in v or len(v) < 5:
                    continue
                for tok in tokens_a:
                    if tok[0] == v[0] and abs(len(tok) - len(v)) <= 1:
                        if SequenceMatcher(None, tok, v).ratio() >= 0.82:
                            note = f"Spelling variant recognized (\"{tok}\" ≈ \"{canonical}\")"
                            return MaterialMatch(0.95 if dim_match or not dims_b else 0.88, note, (tok, phrase_b) if phrase_b else None)

    # Match against the order's material name directly, including newly added items.
    words_a, words_b = _material_words(a), _material_words(b)
    scalar_specs_match = bool(specs_b) and all(values <= specs_a.get(kind, set()) for kind, values in specs_b.items())
    if (not dims_b or dim_match) and (not specs_b or scalar_specs_match):
        typo = _material_typo(words_a.copy(), words_b, dim_match or scalar_specs_match)
        if typo:
            actual, expected = typo
            return MaterialMatch(0.9, f"Typo recognized \"{actual}\" → \"{expected}\" against order description", typo)

    if not erp_matched_known_group:
        if words_a and words_b:
            stems_a = [_en_stem(w) for w in words_a]
            matched_b = 0
            approximations = []
            for word in words_b:
                stem = _en_stem(word)
                if stem in stems_a:
                    matched_b += 1
                    continue
                candidates = {
                    actual for actual, actual_stem in zip(words_a, stems_a)
                    if actual_stem[0] == stem[0] and SequenceMatcher(None, actual_stem, stem).ratio() >= 0.80
                }
                if candidates:
                    matched_b += 1
                    approximations.append((next(iter(candidates)), word) if len(candidates) == 1 else None)
            coverage = matched_b / len(words_b)
            if coverage >= 2 / 3:
                score = 0.95 if (coverage >= 0.99 or dim_match) else 0.88
                words = approximations[0] if len(approximations) == 1 else None
                return MaterialMatch(score, f"Material name match ({matched_b}/{len(words_b)} keywords)", words)

    return MaterialMatch(0.0, "Material not recognized")


# ---------------------------------------------------------------------------
# 3. Load reference datasets from 4 Excel worksheets
# ---------------------------------------------------------------------------

def load_case_database(xlsx_path: Any, fallback_xlsx_path: Optional[str] = None) -> Dict[str, Any]:
    try:
        sheets = read_xlsx_sheets(xlsx_path)
    except (zipfile.BadZipFile, ET.ParseError, KeyError) as exc:
        raise ValueError("File is not a valid Excel workbook (.xlsx)") from exc

    # 1. Invoices and Emails (supports both the standard sheet and an arbitrary first sheet)
    raw_emails = sheets.get("Invoices and Emails")
    if raw_emails is None:
        ref_names = {"Orders and Receipts", "Approvals", "Rules"}
        for sname, srows in sheets.items():
            if sname not in ref_names:
                raw_emails = srows
                break
    raw_emails = raw_emails or []

    emails: List[Dict[str, str]] = []
    for row in raw_emails:
        if len(row) >= 4 and row[0].startswith("E-"):
            emails.append({
                "id": row[0],
                "received_at": row[1],
                "sender": row[2],
                "text": row[3],
            })

    # Support custom workbooks with arbitrary row IDs (not only "E-01")
    if not emails and raw_emails:
        header_tokens = {"#", "id", "no", "no.", "code", "email", "invoice", "received", "date"}
        for idx, row in enumerate(raw_emails, 1):
            non_empty = [c for c in row if c.strip()]
            if len(non_empty) < 3:
                continue
            first_low = row[0].strip().lower()
            second_low = (row[1] if len(row) > 1 else "").strip().lower()
            if first_low in header_tokens or second_low in {"received", "date", "sender"}:
                continue
            if len(row) >= 4 and row[3].strip():
                row_id = row[0].strip() or f"E-{len(emails) + 1:02d}"
                emails.append({
                    "id": row_id,
                    "received_at": row[1].strip() or "16.11 12:00",
                    "sender": row[2].strip() or "Supplier",
                    "text": row[3].strip(),
                })
            elif len(row) >= 3 and row[2].strip():
                emails.append({
                    "id": f"E-{len(emails) + 1:02d}",
                    "received_at": row[0].strip() or "16.11 12:00",
                    "sender": row[1].strip() or "Supplier",
                    "text": row[2].strip(),
                })

    # 2. Orders and Receipts
    raw_orders = sheets.get("Orders and Receipts", [])
    orders: Dict[str, Dict[str, Any]] = {}
    for row in raw_orders:
        if len(row) >= 10 and row[0].startswith("PO-"):
            orders[row[0]] = {
                "order_id": row[0],
                "order_date": row[1],
                "supplier": row[2],
                "supplier_clean": clean_company_name(row[2]),
                "buyer": row[3],
                "material": row[4],
                "unit": row[5],
                "ordered_qty": parse_float(row[6]),
                "accepted_qty": parse_float(row[7]),
                "last_acceptance_date": row[8] if len(row) > 8 else "",
                "order_price": parse_float(row[9]),
                "approval_id": row[10] if len(row) > 10 else "",
            }

    # 3. Approvals (Directum RX)
    raw_approvals = sheets.get("Approvals", [])
    approvals: Dict[str, Dict[str, Any]] = {}
    for row in raw_approvals:
        if len(row) >= 5 and row[0].startswith("AP-"):
            approvals[row[0]] = {
                "approval_id": row[0],
                "date": row[1],
                "order_id": row[2],
                "change_summary": row[3],
                "status": row[4],
                "signed_by": row[5] if len(row) > 5 else "",
            }

    # 4. Rules
    raw_rules = sheets.get("Rules", [])
    rules: Dict[str, Dict[str, str]] = {}
    for row in raw_rules:
        if len(row) >= 3 and row[0].startswith("R-"):
            rules[row[0]] = {
                "rule_id": row[0],
                "topic": row[1],
                "text": row[2],
            }

    # An emails-only workbook falls back to case reference sheets. A workbook providing
    # its own reference sheets may intentionally leave Orders empty.
    case_references = not (sheets.keys() & {"Orders and Receipts", "Approvals", "Rules"})
    if fallback_xlsx_path and (case_references or not rules):
        base_db = load_case_database(fallback_xlsx_path, fallback_xlsx_path=None)
        if case_references:
            orders = base_db["orders"]
            approvals = base_db["approvals"]
        if not rules:
            rules = base_db["rules"]

    return {
        "emails": emails,
        "orders": orders,
        "approvals": approvals,
        "rules": rules,
    }


# ---------------------------------------------------------------------------
# 4. NLP parser for email/invoice text (Entity extraction + R-7 packaging)
# ---------------------------------------------------------------------------

def normalize_invoice_number(raw_num: str) -> Tuple[str, List[str]]:
    """
    Rule R-3:
    A re-sent invoice is a duplicate even if formatted with leading zeros or a slash suffix.
    Returns (canonical_number, normalization_notes).
    """
    notes: List[str] = []
    s = (raw_num or "").strip()
    if "/" in s:
        base = s.split("/")[0].strip()
        notes.append(f"slash suffix in \"{s}\" → base invoice No. {base}")
        s = base
    if re.match(r"^0+\d+$", s):
        stripped = s.lstrip("0") or "0"
        notes.append(f"leading zeros in \"{raw_num}\" → base invoice No. {stripped}")
        s = stripped
    return s, notes


_ITEM_UNITS = r"pieces?|pcs\.?|units?|pc\.?"


def normalize_unit(unit: str) -> str:
    unit = unit.strip().lower().rstrip(".")
    if re.fullmatch(_ITEM_UNITS, unit):
        return "pcs"
    if re.fullmatch(r"rolls?|rl", unit):
        return "roll"
    if re.fullmatch(r"bags?", unit):
        return "bag"
    if re.fullmatch(r"boxes|box", unit):
        return "box"
    if re.fullmatch(r"packs?", unit):
        return "pack"
    if re.fullmatch(r"liters?|litres?|l", unit):
        return "l"
    return unit


_QUOTE_HEADER = re.compile(
    r"^\s*(?:(?:quote(?:\s+from[^:\n]*)?|previous\s+version\s+from\s+quote|quoted\s+email)\s*:|"
    r"-{2,}\s*(?:original message|forwarded message))",
    re.I,
)
_ORDER_REFERENCE = re.compile(r"\bPO[-–—‑](\d+)\b", re.I)
_NUM = r"-?(?:\d{1,3}(?:,\d{3})+|\d{1,3}(?:\s\d{3})+|\d+)(?:\.\d+)?"
_MONEY = rf"(?:\$\s*({_NUM})|({_NUM})\s*(?:usd|dollars?)\b)"


def active_invoice_text(text: str) -> str:
    """Separate the active email body from explicitly quoted reply history."""
    current = []
    for line in text.splitlines():
        if _QUOTE_HEADER.match(line):
            break
        if not line.lstrip().startswith(">"):
            current.append(line)
    return "\n".join(current).strip()


def parse_email_entities(email_item: Dict[str, str]) -> Dict[str, Any]:
    """
    Extract invoice number, purchase order reference, packaging ratio,
    quantities, prices, totals, and risk flags from unstructured email text.
    """
    sender = email_item.get("sender", "")
    text = active_invoice_text(email_item.get("text", ""))
    received_at = email_item.get("received_at", "")

    # Identify sender (supplier vs internal employee)
    is_internal_buyer = "buyer" in sender.lower() or "northberry" in sender.lower()
    sender_company = re.sub(r'["«»]', "", sender.split(",")[0]).strip()
    sender_company_clean = clean_company_name(sender_company)
    sender_email_m = re.search(r"[\w.\-]+@[\w.\-]+", sender)
    sender_email = sender_email_m.group(0) if sender_email_m else ""

    # Explicit purchase order reference
    order_ids = {f"PO-{number}" for number in _ORDER_REFERENCE.findall(text)}
    explicit_order_id = next(iter(order_ids)) if len(order_ids) == 1 else None

    # Order date reference in text (e.g., "your order dated 05.11")
    order_date_ref_m = re.search(r"order\s+(?:dated|from)\s+(\d{2}\.\d{2}(?:\.\d{4})?)", text, re.I)
    referenced_order_date = order_date_ref_m.group(1) if order_date_ref_m else None

    # Email type and risk markers
    is_corrected = bool(re.search(r"(?:corrected|revised)\s+invoice", text, re.I))
    is_resend_mention = bool(re.search(r"resending|re-sending|sending\s+again|duplicate\s+invoice", text, re.I))
    is_requisites_change = bool(re.search(
        r"chang\w*\s+bank|new\s+bank\s+(?:account|details)|new\s+payment\s+details|"
        r"from\s+another\s+(?:company|entity)|different\s+(?:company|entity)|"
        r"payment\s+recipient|beneficiary|financial\s+agent|factoring|"
        r"(?:account|acct\.?)\s*(?:no\.?|#|:)\s*\d|\b\d{16,20}\b",
        text,
        re.I,
    ))

    # Invoice number
    inv_m = re.search(r"invoice\s*(?:no\.?\s*|#\s*)?(\d+(?:/\d+)?)", text, re.I)
    raw_invoice_no = inv_m.group(1) if inv_m else None
    canonical_inv_no, inv_norm_notes = normalize_invoice_number(raw_invoice_no) if raw_invoice_no else (None, [])

    # Informational email check (no invoice total in the body)
    has_total = bool(
        re.search(rf"(?:total|amount\s+due)\s*:?\s*{_MONEY}", text, re.I)
        or re.search(rf"invoice\s+(?:no\.?\s*|#\s*)?\d+.*\bfor\s+{_MONEY}", text, re.I)
    )
    is_info_about_invoice = bool(re.search(r"^(?:re:|regarding)\s+(?:invoice\s+\d+|PO-\d+)", text.strip(), re.I)) and not has_total

    # Grand total extraction
    total_pairs = re.findall(rf"(?:total|amount\s+due)\s*:?\s*{_MONEY}", text, re.I)
    if not total_pairs:
        total_pairs = re.findall(rf"\bfor\s+{_MONEY}", text, re.I)
    totals = [a or b for a, b in total_pairs]
    unique_totals = {parse_float(total) for total in totals}
    total_amount = next(iter(unique_totals)) if len(unique_totals) == 1 else None
    ambiguous_data = len(unique_totals) > 1

    # Extract packaging, quantity, and unit price
    # Pattern 1: Compound packaging (R-7), e.g.:
    # "10 bags of 20 kg, bag price 3,600 USD" or "10 rolls of 1,000 pcs, roll price 1,500 USD"
    pack_matches = list(re.finditer(
        rf"({_NUM})\s*(bags?|rolls?|packs?|boxes|box)\s+of\s+({_NUM})\s*(kg|{_ITEM_UNITS}|rl\.?|m)(?!\w)"
        rf".*?(?:price(?:\s+per\s+\S+)?|\S+\s+price|at)\s+{_MONEY}",
        text,
        re.I,
    ))
    pack_m = pack_matches[0] if pack_matches else None

    raw_qty: Optional[float] = None
    raw_unit: str = ""
    raw_price: Optional[float] = None
    pack_multiplier: float = 1.0
    converted_qty: Optional[float] = None
    converted_unit: str = ""
    converted_unit_price: Optional[float] = None
    conversion_formula: Optional[str] = None
    line_start = len(text)

    # Standard line items specify quantity, unit, and unit price.
    std_matches = [
        match for match in re.finditer(
            rf"({_NUM})\s*({_ITEM_UNITS}|kg|rolls?|rl\.?|bags?)(?!\w)\s*(?:,\s*price|at)\s+{_MONEY}",
            text, re.I,
        )
        if all(match.end() <= pack.start() or match.start() >= pack.end() for pack in pack_matches)
    ]
    ambiguous_data = ambiguous_data or len(std_matches) + len(pack_matches) > 1

    if pack_m:
        line_start = pack_m.start()
        raw_qty = parse_float(pack_m.group(1))
        raw_unit = pack_m.group(2)
        pack_multiplier = parse_float(pack_m.group(3))
        converted_unit = normalize_unit(pack_m.group(4))
        raw_price = parse_float(pack_m.group(5) or pack_m.group(6))
        converted_qty = raw_qty * pack_multiplier
        converted_unit_price = raw_price / pack_multiplier if pack_multiplier else raw_price
        conversion_formula = (
            f"{int(raw_qty)} {raw_unit} × {int(pack_multiplier)} {converted_unit} = "
            f"{int(converted_qty)} {converted_unit}; "
            f"${raw_price:,.0f} / {int(pack_multiplier)} = ${converted_unit_price:,.2f}/{converted_unit}"
        )
    elif std_matches:
        m = std_matches[0]
        line_start = m.start()
        raw_qty = parse_float(m.group(1))
        raw_unit = normalize_unit(m.group(2))
        raw_price = parse_float(m.group(3) or m.group(4))
        converted_qty = raw_qty
        converted_unit = raw_unit
        converted_unit_price = raw_price

    # Extract material description snippet
    material_snippet = re.split(r"total|amount\s+due|reference\s*:|previous\s+version", text[:line_start], maxsplit=1, flags=re.I)[0]
    colon_m = re.search(r":\s*(.+)", material_snippet, re.S)
    if colon_m:
        material_snippet = colon_m.group(1).strip()

    # Batch marker (first / second / remaining)
    batch_info = None
    if re.search(r"first\s+batch", text, re.I):
        batch_info = "First batch"
    elif re.search(r"second\s+batch", text, re.I):
        batch_info = "Second batch"
    elif re.search(r"remaining", text, re.I):
        batch_info = "Order remainder"

    return {
        "is_internal_buyer": is_internal_buyer,
        "sender_company": sender_company,
        "sender_company_clean": sender_company_clean,
        "sender_email": sender_email,
        "explicit_order_id": explicit_order_id,
        "ambiguous_order": len(order_ids) > 1,
        "ambiguous_invoice_data": ambiguous_data,
        "active_text": text,
        "referenced_order_date": referenced_order_date,
        "raw_invoice_no": raw_invoice_no,
        "canonical_invoice_no": canonical_inv_no,
        "invoice_norm_notes": inv_norm_notes,
        "is_corrected": is_corrected,
        "is_resend_mention": is_resend_mention,
        "is_requisites_change": is_requisites_change,
        "is_info_only": is_info_about_invoice or is_internal_buyer,
        "raw_qty": raw_qty,
        "raw_unit": raw_unit,
        "raw_price": raw_price,
        "pack_multiplier": pack_multiplier,
        "converted_qty": converted_qty,
        "converted_unit": converted_unit,
        "converted_unit_price": converted_unit_price,
        "conversion_formula": conversion_formula,
        "total_amount": total_amount,
        "material_snippet": material_snippet,
        "batch_info": batch_info,
        "received_ddmm": parse_date_ddmm(received_at),
    }


# ---------------------------------------------------------------------------
# 5. Deterministic rule engine R-1 ... R-9
# ---------------------------------------------------------------------------

def resolve_order_p1(
    parsed: Dict[str, Any],
    email_text: str,
    orders: Dict[str, Dict[str, Any]],
    earlier_invoices_by_supplier_num: Dict[Tuple[str, str], str],
) -> Tuple[Optional[Dict[str, Any]], float, str]:
    """
    Rule R-1:
    An invoice number is unique only within one supplier. Invoices are linked by explicit order ID,
    or by supplier, material, quantity, and order date when no order ID is provided.
    """
    # 1. Explicit purchase order ID (e.g., PO-06)
    exp_id = parsed.get("explicit_order_id")
    if exp_id:
        if exp_id in orders:
            return orders[exp_id], 1.0, f"Direct link via purchase order {exp_id} in email text (R-1)"
        return None, 0.0, f"Order {exp_id} was not found in the ERP export; automatic fallback to another order is prohibited"

    # 2. Follow-up email referencing an earlier invoice from the same supplier (e.g., E-19 or E-25)
    sup_clean = parsed.get("sender_company_clean", "")
    inv_no = parsed.get("canonical_invoice_no")
    if sup_clean and inv_no and (sup_clean, inv_no) in earlier_invoices_by_supplier_num:
        linked_po = earlier_invoices_by_supplier_num[(sup_clean, inv_no)]
        if linked_po in orders:
            return (
                orders[linked_po],
                0.98,
                f"Linked to {linked_po} via previously recorded invoice No. {inv_no} from {parsed['sender_company']} (R-1)",
            )

    # 3. Supplier changed legal entity name (e.g., Corrugated Box Center Plus, invoice 116)
    if inv_no:
        for (known_sup, known_inv), linked_po in earlier_invoices_by_supplier_num.items():
            if known_inv == inv_no and (known_sup in sup_clean or sup_clean in known_sup):
                if linked_po in orders:
                    return (
                        orders[linked_po],
                        0.92,
                        f"Linked to {linked_po} by base supplier match, invoice No. {inv_no}, material, and quantity (R-1, R-2)",
                    )

    # 4. Multi-attribute search (Supplier + Material/dimensions + Quantity + Order Date) (R-1)
    best_order = None
    best_score = 0.0
    second_score = 0.0
    best_reasons: List[str] = []

    ref_ddmm = parse_date_ddmm(parsed.get("referenced_order_date") or "")
    conv_qty = parsed.get("converted_qty")

    for po_id, ord_obj in orders.items():
        score = 0.0
        reasons: List[str] = []

        # Supplier
        ord_sup = ord_obj["supplier_clean"]
        if sup_clean and (sup_clean == ord_sup or ord_sup in sup_clean or sup_clean in ord_sup):
            score += 0.35
            reasons.append(f"supplier {ord_obj['supplier']}")

        # Material and dimensions
        match = match_material_similarity(email_text, ord_obj["material"])
        if match.score > 0:
            score += 0.35 * match.score
            reasons.append(f"material \"{ord_obj['material']}\" ({match.note})")

        # Quantity
        if conv_qty is not None and abs(conv_qty - ord_obj["ordered_qty"]) < 1e-6:
            score += 0.15
            reasons.append(f"quantity {int(conv_qty)} {ord_obj['unit']}")

        # Order date
        ord_ddmm = parse_date_ddmm(ord_obj["order_date"])
        if ref_ddmm and ord_ddmm and ref_ddmm == ord_ddmm:
            score += 0.15
            reasons.append(f"order date {ord_obj['order_date']}")

        if score > best_score:
            second_score = best_score
            best_score = score
            best_order = ord_obj
            best_reasons = reasons
        elif score > second_score:
            second_score = score

    if best_order and best_score >= 0.55:
        if best_score - second_score < 0.05:
            return None, 0.0, "Multiple similar purchase orders found; explicit order number required"
        explanation = f"Auto-linked without order ID to {best_order['order_id']} by attributes (R-1): " + ", ".join(best_reasons)
        return best_order, round(best_score, 2), explanation

    return None, 0.0, "Purchase order not found in ERP export"


def parse_approval_effects(approval: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract Directum RX approval parameters for rule R-6 validation."""
    if not approval:
        return {"exists": False}

    summary = approval.get("change_summary", "")
    status = approval.get("status", "")
    is_signed = status.strip().lower() == "signed" and bool(approval.get("signed_by", "").strip())

    # New approved price (e.g., "5.50 USD per piece instead of 5.00 USD" or "225 USD per kg instead of 210 USD")
    price_m = re.search(
        r"(?:\$\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*usd)\b.*instead\s+of\s+(?:\$\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*usd)",
        summary,
        re.I,
    )
    new_price = parse_float(price_m.group(1) or price_m.group(2)) if price_m else None

    # New approved quantity (e.g., "Quantity increased from 40 to 50 rolls")
    qty_m = re.search(r"increased\s+from\s+\d+\s+to\s+(\d+)", summary, re.I)
    new_qty = parse_float(qty_m.group(1)) if qty_m else None

    # Effective date ("for deliveries from 18.11.2026")
    eff_m = re.search(r"(?:for\s+deliveries|effective)\s+from\s+(\d{2}\.\d{2}\.\d{4})", summary, re.I)
    effective_from_str = eff_m.group(1) if eff_m else None
    effective_from_ddmm = parse_date_ddmm(effective_from_str) if effective_from_str else None

    # Split batch schedule ("Delivery in two batches: 360 rolls by 10.11, 240 rolls by 15.11")
    is_split_batches = "batches" in summary.lower()
    batches = [parse_float(x) for x in re.findall(r"(\d+)\s*(?:rolls?|pcs|kg)", summary, re.I)] if is_split_batches else []

    # Delayed remainder delivery ("Supplier will deliver the remaining 200 cartons by 20.11.2026")
    is_delayed_rest = "remaining" in summary.lower() and "deliver" in summary.lower()

    return {
        "exists": True,
        "approval_id": approval["approval_id"],
        "order_id": approval["order_id"],
        "date": approval["date"],
        "summary": summary,
        "status": status,
        "signed_by": approval.get("signed_by", ""),
        "is_signed": is_signed,
        "new_price": new_price,
        "new_qty": new_qty,
        "effective_from_str": effective_from_str,
        "effective_from_ddmm": effective_from_ddmm,
        "is_split_batches": is_split_batches,
        "batches": batches,
        "is_delayed_rest": is_delayed_rest,
    }


def _received_key(email: Dict[str, str]) -> datetime:
    """Version ordering is determined by receipt timestamp, not Excel row order."""
    value = email.get("received_at", "").strip()
    if re.fullmatch(r"\d{2}\.\d{2}\s+\d{2}:\d{2}", value):
        value = value[:5] + ".2026" + value[5:]
    for fmt in ("%d.%m.%Y %H:%M",):
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed
        except ValueError:
            pass
    raise ValueError("Received timestamp must follow DD.MM HH:MM or DD.MM.YYYY HH:MM format")


def apply_confirmed_extraction(parsed: Dict[str, Any], fields: Dict[str, str]) -> None:
    """Fill only parser gaps with the operator-confirmed, source-checked fields."""
    if not parsed["raw_invoice_no"] and "invoice" in fields:
        parsed["raw_invoice_no"] = fields["invoice"]
        parsed["canonical_invoice_no"], parsed["invoice_norm_notes"] = normalize_invoice_number(fields["invoice"])
    if parsed["total_amount"] is None and "total" in fields:
        parsed["total_amount"] = float(fields["total"])
    if parsed["raw_qty"] is None and {"quantity", "unit", "price", "material"} <= fields.keys():
        quantity, price = float(fields["quantity"]), float(fields["price"])
        parsed.update(
            raw_qty=quantity, raw_unit=fields["unit"], raw_price=price,
            converted_qty=quantity, converted_unit=fields["unit"], converted_unit_price=price,
            material_snippet=fields["material"],
        )
        unit_source = fields.get("unit_source")
        if unit_source and normalize_unit(unit_source) != fields["unit"]:
            parsed["unit_mapping"] = {"source": unit_source, "target": fields["unit"], "method": "ai"}


MaterialAdvisor = Callable[[str, str], Optional[Tuple[str, str]]]
BatchMaterialAdvisor = Callable[[str, str, str], Optional[Tuple[str, str]]]


def analyze_all_emails(
    db: Dict[str, Any], confirmed_ai: Optional[Dict[str, Dict[str, str]]] = None,
    material_advice: Optional[BatchMaterialAdvisor] = None,
) -> Dict[str, Any]:
    """Reconcile active invoice versions: unverified data never becomes ready to pay."""
    emails = sorted(db["emails"], key=_received_key)
    orders, approvals, rules_ref = db["orders"], db["approvals"], db["rules"]
    earlier_inv_map = {}
    parsed_list = []
    corrections = {}
    for index, em in enumerate(emails):
        p = parse_email_entities(em)
        if confirmed_ai and em["id"] in confirmed_ai and not p["ambiguous_invoice_data"]:
            apply_confirmed_extraction(p, confirmed_ai[em["id"]])
        if p["ambiguous_order"]:
            order, confidence, reason = None, 0.0, "Multiple purchase orders are mentioned in the email. Clarify which order this invoice belongs to."
        else:
            order, confidence, reason = resolve_order_p1(p, p["active_text"], orders, earlier_inv_map)
        p.update(matched_order=order, match_confidence=confidence, p1_reason=reason)
        key = (p["sender_company_clean"], p["canonical_invoice_no"])
        if order and all(key) and not p["is_info_only"] and not p["ambiguous_invoice_data"]:
            earlier_inv_map.setdefault(key, order["order_id"])
            # An email changing payment recipient cannot supersede an active invoice.
            if p["is_corrected"] and not p["is_requisites_change"] and key[0] == order["supplier_clean"]:
                corrections[key] = (index, em["id"])
        parsed_list.append(p)

    seen = {}
    billed = {}  # Only active invoices with verified line item, total, and order terms.
    results = []
    for index, (em, p) in enumerate(zip(emails, parsed_list)):
        order = p["matched_order"]
        oid = order["order_id"] if order else "—"
        inv = p["raw_invoice_no"] or "not specified"
        supplier = p["sender_company"]
        key = (p["sender_company_clean"], p["canonical_invoice_no"])
        amount = p["total_amount"] or 0.0
        approval_raw = approvals.get(order.get("approval_id")) if order else None
        app_eff = parse_approval_effects(approval_raw)
        checks = [{"rule": "R-1 (Order Matching)", "status": "ok" if order else "error", "detail": p["p1_reason"]}]
        triggered = ["R-1"]

        def check(rule, status, detail):
            triggered.extend(re.findall(r"R-\d", rule))
            checks.append({"rule": rule, "status": status, "detail": detail})

        def finish(code, label, color, reason, next_step, category="none", risk=0.0,
                   role=None, recipient=None, request=None):
            actions = []
            if role:
                triggered.append("R-9")
                actions.append({
                    "recipient_role": role,
                    "recipient_name": recipient or (order["buyer"] if order else "Order Owner"),
                    "rule_ref": ", ".join(dict.fromkeys(triggered)),
                    "subject": f"{label}: invoice No. {inv}, order {oid}",
                    "body": f"Hello team,\n\nEmail {em['id']} from {supplier}, received {em['received_at']}.\n"
                            f"Invoice No. {inv}, order {oid}.\n{reason}\n\n{request or next_step}",
                })
            results.append(_build_item_result(
                em, p, order, app_eff, code, label, color, category, amount,
                amount if code == "READY_TO_PAY" else 0.0, max(0.0, round(risk, 2)),
                triggered, checks, reason, next_step, actions,
            ))

        def review(reason, rule="R-1 (Data Completeness)"):
            check(rule, "warn", reason)
            finish("NEEDS_REVIEW", "Manual review required", "slate", reason,
                   "Clarify the missing details and re-run reconciliation. Do not include in the payment registry until resolved.",
                   role="Buyer / Supplier", recipient=order["buyer"] if order else "Order Owner")

        if not order:
            review(p["p1_reason"])
            continue

        if p["is_info_only"] and not p["is_requisites_change"]:
            if app_eff.get("exists"):
                detail = f"Approval {app_eff['approval_id']}: {app_eff['status']}. Email correspondence does not modify order terms."
            else:
                detail = "No signed order amendments in the export. Correspondence does not confirm warehouse receipt."
            check("R-6 (Order Terms)", "ok", detail)
            finish("INFO_LETTER", "Order information", "slate",
                   f"Informational email regarding {oid}. No new payable invoice created. {detail}",
                   f"Archive email under {oid}; confirm details with buyer {order['buyer']}.")
            continue

        if p["sender_company_clean"] != order["supplier_clean"] or p["is_requisites_change"]:
            if not amount:
                linked = next((r for r in reversed(results) if r["order_id"] == oid and r["canonical_invoice_no"] == key[1] and r["stated_amount"]), None)
                amount = linked["stated_amount"] if linked else 0.0
            reason = (f"Order {oid} lists supplier {order['supplier']}; email sender is {supplier}. "
                      "Payment recipient and bank details in the email cannot be verified from the provided export. "
                      "No signed amendment authorizing this change was found (R-2).")
            check("R-2 (Supplier & Bank Details)", "error", reason)
            finish("CRITICAL_REQUISITES", "Verify recipient and bank details", "rose", reason,
                   "Hold payment preparation; verify the contract and signed addendum in Directum RX.",
                   "requisites", amount, "Buyer and CFO", f"{order['buyer']} / CFO")
            continue
        check("R-2 (Supplier)", "ok", f"Supplier matches {order['supplier']}. Use verified contract bank details for payment.")

        if p["ambiguous_invoice_data"]:
            review("Multiple line items or conflicting totals were found in the email. Clarify the current invoice figures.", "R-8 (Arithmetic)")
            continue

        replacement = corrections.get(key)
        if replacement and index < replacement[0]:
            reason = f"Invoice No. {inv} was superseded by a later corrected version {replacement[1]} (R-3)."
            check("R-3 (Invoice Versions)", "error", reason)
            finish("DUPLICATE_OR_REPLACED", f"Superseded by corrected ({replacement[1]})", "amber", reason,
                   f"Archive this version. Reconcile the active revision {replacement[1]} separately.", "duplicate", amount)
            continue
        if all(key) and key in seen:
            original = seen[key]
            reason = f"Invoice No. {inv} (normalized {key[1]}) duplicates document {original} from the same supplier (R-3)."
            check("R-3 (Duplicates)", "error", reason)
            finish("DUPLICATE_OR_REPLACED", f"Duplicate invoice ({original})", "amber", reason,
                   f"Exclude duplicate from payment registry. Check bank statement for payment status of {original}.",
                   "duplicate", amount, "Treasurer", "Treasury")
            continue
        if all(key):
            seen[key] = em["id"]
        check("R-3 (Active Version)", "ok", "Single active invoice version verified for this supplier.")

        missing = []
        for field, label in (("raw_invoice_no", "invoice number"), ("raw_qty", "quantity"),
                             ("raw_price", "unit price"), ("total_amount", "total amount"),
                             ("converted_qty", "quantity in order unit"), ("converted_unit", "unit of measure")):
            if p.get(field) in (None, ""):
                missing.append(label)
        if missing:
            p["missing_extraction"] = [
                key for key, field in (("invoice", "raw_invoice_no"), ("quantity", "raw_qty"),
                                       ("price", "raw_price"), ("total", "total_amount"), ("unit", "converted_unit"))
                if p.get(field) in (None, "")
            ]
            review("Could not extract required fields: " + ", ".join(missing) + ". Order values are never substituted for missing invoice data.")
            continue
        if any(p[field] <= 0 for field in ("raw_qty", "raw_price", "total_amount", "converted_qty", "converted_unit_price")):
            review("Quantity, unit price, packaging ratio, and total must be positive. Manual inspection of the source invoice is required.")
            continue

        snippet = p["material_snippet"]
        match = match_material_similarity(snippet, order["material"])
        unit = normalize_unit(order["unit"])
        units_match = normalize_unit(p["converted_unit"]) == unit
        method = "rules"
        if (
            match.score < 0.85 and not match.conflict and units_match
            and material_advice is not None
        ):
            advice = material_advice(em["id"], snippet, order["material"])
            if advice:
                source, target = advice
                pattern = rf"(?<!\w){re.escape(source)}(?!\w)"
                adjusted = re.sub(pattern, lambda _: target, snippet, flags=re.I)
                verified = match_material_similarity(adjusted, order["material"])
                if adjusted != snippet and verified.score >= 0.85:
                    match = MaterialMatch(verified.score, f"AI mapped \"{source}\" → \"{target}\" against order {oid}", advice)
                    method = "ai"
        if match.score < 0.85 or not units_match:
            review(f"Invoice material or unit could not be verified: {match.note}; converted unit \"{p['converted_unit']}\", "
                   f"order specifies \"{order['material']}\", {unit}. Clarify item and packaging.", "R-7 (Material & Units)")
            continue
        if match.words:
            source, target = match.words
            original = re.search(rf"(?<!\w){re.escape(source)}(?!\w)", snippet, re.I)
            if original:
                p["material_mapping"] = {"source": original.group(), "target": target, "method": method}
        check("R-7 (Material & Units)", "ok", f"{match.note}. {p['conversion_formula'] or 'Invoice unit matches order unit: ' + unit}.")

        expected = round(p["raw_qty"] * p["raw_price"], 2)
        difference = round(amount - expected, 2)
        if abs(difference) >= 0.01:
            reason = f"Invoice No. {inv}: {p['raw_qty']:g} × {p['raw_price']:g} = ${format_amount(expected)}; stated ${format_amount(amount)}. Variance {difference:+,.2f} USD."
            check("R-8 (Invoice Total)", "error", reason)
            finish("MATH_ERROR", "Invoice arithmetic error", "purple", reason,
                   f"Request a corrected invoice No. {inv} from the supplier for ${format_amount(expected)}.",
                   "math_error", abs(difference), "Supplier", supplier)
            continue
        check("R-8 (Invoice Total)", "ok", f"{p['raw_qty']:g} × {p['raw_price']:g} = ${format_amount(expected)}.")

        price = order["order_price"]
        max_qty = order["ordered_qty"]
        approval_note = "ERP purchase order terms apply."
        if app_eff.get("exists"):
            if app_eff.get("order_id") != oid:
                review("The linked approval belongs to a different purchase order. Verify the reference in Directum RX.", "R-6 (Approval Scope)")
                continue
            approval_note = f"{app_eff['approval_id']}: {app_eff['status']}."
            if app_eff["is_signed"]:
                applicable = True
                if app_eff["effective_from_str"]:
                    effective_date = parse_case_date(app_eff["effective_from_str"])
                    accepted_date = parse_case_date(order["last_acceptance_date"])
                    if not effective_date:
                        review("The approval specifies an invalid effective date.", "R-6 (Effective Date)")
                        continue
                    if not accepted_date:
                        review("Applying this approval requires an actual warehouse receipt date. Check the export.", "R-6 (Effective Date)")
                        continue
                    applicable = accepted_date >= effective_date
                    approval_note += f" Effective from {app_eff['effective_from_str']}; receipt date {order['last_acceptance_date']}."
                if applicable:
                    if app_eff["new_price"] is not None:
                        price = app_eff["new_price"]
                    if app_eff["new_qty"] is not None:
                        max_qty = app_eff["new_qty"]
                else:
                    approval_note += " Prior ERP terms apply to this delivery."
        qty, inv_price = p["converted_qty"], p["converted_unit_price"]
        if abs(inv_price - price) > 1e-4:
            reason = f"Invoice price ${inv_price:g}/{unit} differs from effective price ${price:g}/{unit}. {approval_note}"
            check("R-6 (Effective Price)", "error", reason)
            finish("PRICE_OR_QTY_UNAPPROVED", "Unapproved price", "orange", reason,
                   f"Confirm price basis with buyer {order['buyer']}; request correction to ${format_amount(qty * price)} or a signed approval.",
                   "unapproved_change", max(0, qty * (inv_price - price)), "Buyer", order["buyer"])
            continue
        if qty > max_qty:
            excess = qty - max_qty
            reason = (f"Invoice No. {inv} bills {qty:g} {unit} (${format_amount(amount)}), while approved limit is {max_qty:g} {unit} (${format_amount(max_qty * price)}). "
                      f"Accepted {order['accepted_qty']:g} {unit}; warehouse receipt does not authorize the {excess:g} {unit} overrun. {approval_note}")
            check("R-6 (Order Quantity)", "error", reason)
            finish("PRICE_OR_QTY_UNAPPROVED", "Order quantity exceeded", "orange", reason,
                   f"Request overrun approval for {excess:g} {unit} from the buyer and receipt justification from the warehouse, or a corrected invoice for ${format_amount(max_qty * price)}.",
                   "unapproved_change", excess * price, "Buyer and Warehouse Manager", f"{order['buyer']} / Warehouse Manager")
            continue
        check("R-6 (Price & Quantity)", "ok", f"Price ${price:g}/{unit}, order limit {max_qty:g} {unit}. {approval_note}")

        prior_qty, prior_ids = billed.get(oid, (0.0, []))
        if prior_qty + qty > max_qty + 1e-6:
            reason = (f"Order {oid} already has {prior_qty:g} {unit} billed in active invoices {', '.join(prior_ids)}. "
                      f"Invoice No. {inv} adds {qty:g} {unit}: {prior_qty + qty:g} total vs {max_qty:g} {unit} approved.")
            check("R-3 (Duplicate Order Volume)", "error", reason)
            finish("DUPLICATE_OR_REPLACED", "Order volume billed twice", "amber", reason,
                   "Confirm with the supplier which invoices are superseded and which batches they cover; do not include duplicate volume in the registry.",
                   "duplicate", amount, "Supplier and Buyer", f"{supplier} / {order['buyer']}")
            continue
        billed[oid] = (prior_qty + qty, prior_ids + [em["id"]])
        available = max(0.0, order["accepted_qty"] - prior_qty)
        p["available_accepted_qty"] = available
        if qty > available + 1e-6:
            shortage = qty - available
            reason = (f"Accepted on {oid}: {order['accepted_qty']:g} {unit}; previously billed in active invoices {prior_qty:g} {unit}. "
                      f"Available for invoice No. {inv}: {available:g} of {qty:g} {unit}. Uncovered by receipt: {shortage:g} {unit} (${format_amount(shortage * price)}). "
                      "Contract prepayment terms are absent from the export; neither payment nor final rejection can be prepared without them (R-4, R-5).")
            check("R-4, R-5 (Receipt & Prepayment)", "warn", reason)
            finish("NOT_ACCEPTED_YET", "Insufficient confirmed receipt", "blue", reason,
                   "Request contract prepayment terms from the buyer and batch status from the warehouse. "
                   + (f"If post-receipt payment applies, confirm an invoice for the available {available:g} {unit} (${format_amount(available * price)})."
                      if available > 0 else "If prepayment is not stipulated, wait for the new batch receipt to be posted."),
                   "unaccepted_goods", shortage * price, "Buyer and Warehouse Manager", f"{order['buyer']} / Warehouse Manager")
            continue
        check("R-4, R-5 (Receipt)", "ok", f"Available for this invoice: {available:g} {unit}, required {qty:g}; previously billed {prior_qty:g}. Prepayment not required.")
        check("R-9 (Payment Control)", "warn", "Bank statement is not included in the export; explicit treasurer verification is required before payment.")
        finish("READY_TO_PAY", "Ready for draft registry", "emerald",
               f"Order, supplier, active version, material, units, arithmetic, effective price, and available receipt verified. Amount ${format_amount(amount)}. Bank statement and contract bank details check required.",
               "Ask the treasurer to confirm this invoice has not been paid yet. Once verified, include it in the payment registry for CFO approval.",
               role="Treasurer and CFO", recipient="Treasury / CFO")

    # API returns documents in source order while evaluation runs chronologically.
    by_id = {result["id"]: result for result in results}
    results = [by_id[em["id"]] for em in db["emails"]]
    return {"items": results, "summary": _compute_summary_metrics(results, orders, approvals, rules_ref),
            "orders": list(orders.values()), "approvals": list(approvals.values()), "rules": list(rules_ref.values())}


def _build_item_result(
    em: Dict[str, str],
    p: Dict[str, Any],
    order: Optional[Dict[str, Any]],
    app_eff: Dict[str, Any],
    status_code: str,
    status_label: str,
    status_color: str,
    risk_category: str,
    stated_amount: float,
    payable_amount: float,
    prevented_risk: float,
    triggered_rules: List[str],
    rule_checks: List[Dict[str, str]],
    primary_reason: str,
    next_step: str,
    actions: List[Dict[str, str]],
) -> Dict[str, Any]:
    dedup_rules = []
    for r in triggered_rules:
        if r not in dedup_rules:
            dedup_rules.append(r)

    return {
        "id": em["id"],
        "received_at": em["received_at"],
        "sender": em["sender"],
        "text": em["text"],
        "supplier_name": p["sender_company"],
        "raw_invoice_no": p["raw_invoice_no"] or "—",
        "canonical_invoice_no": p["canonical_invoice_no"] or "—",
        "order_id": order["order_id"] if order else "—",
        "order": order,
        "approval": app_eff if app_eff.get("exists") else None,
        "match_confidence": p["match_confidence"],
        "p1_reason": p["p1_reason"],
        "raw_qty": p["raw_qty"],
        "raw_unit": p["raw_unit"],
        "raw_price": p["raw_price"],
        "converted_qty": p["converted_qty"],
        "converted_unit": p["converted_unit"],
        "converted_unit_price": p["converted_unit_price"],
        "conversion_formula": p["conversion_formula"],
        "material_mapping": p.get("material_mapping"),
        "unit_mapping": p.get("unit_mapping") if order and normalize_unit(p["converted_unit"]) == normalize_unit(order["unit"]) else None,
        "missing_extraction": p.get("missing_extraction", []),
        "available_accepted_qty": p.get("available_accepted_qty"),
        "stated_amount": stated_amount,
        "payable_amount": payable_amount,
        "prevented_risk": prevented_risk,
        "status_code": status_code,
        "status_label": status_label,
        "status_color": status_color,
        "risk_category": risk_category,
        "triggered_rules": dedup_rules,
        "rule_checks": rule_checks,
        "primary_reason": primary_reason,
        "next_step": next_step,
        "actions": actions,
    }


def _compute_summary_metrics(
    results: List[Dict[str, Any]],
    orders: Dict[str, Dict[str, Any]],
    approvals: Dict[str, Dict[str, Any]],
    rules_ref: Dict[str, Dict[str, str]],
) -> Dict[str, Any]:
    ready_items = [r for r in results if r["status_code"] == "READY_TO_PAY"]
    blocked_items = [r for r in results if r["status_code"] not in ("READY_TO_PAY", "INFO_LETTER")]
    info_items = [r for r in results if r["status_code"] == "INFO_LETTER"]

    total_payable = sum(r["payable_amount"] for r in ready_items)
    total_prevented = sum(r["prevented_risk"] for r in results)

    by_category = {
        "duplicate": sum(r["prevented_risk"] for r in results if r["risk_category"] == "duplicate"),
        "requisites": sum(r["prevented_risk"] for r in results if r["risk_category"] == "requisites"),
        "math_error": sum(r["prevented_risk"] for r in results if r["risk_category"] == "math_error"),
        "unapproved_change": sum(r["prevented_risk"] for r in results if r["risk_category"] == "unapproved_change"),
        "unaccepted_goods": sum(r["prevented_risk"] for r in results if r["risk_category"] == "unaccepted_goods"),
    }

    counts_by_status: Dict[str, int] = {}
    for r in results:
        counts_by_status[r["status_code"]] = counts_by_status.get(r["status_code"], 0) + 1

    return {
        "total_emails": len(results),
        "ready_to_pay_count": len(ready_items),
        "blocked_or_disputed_count": len(blocked_items),
        "info_letters_count": len(info_items),
        "total_payable_rub": round(total_payable, 2),
        "total_prevented_risk_rub": round(total_prevented, 2),
        "risk_breakdown_rub": by_category,
        "counts_by_status": counts_by_status,
        "orders_count": len(orders),
        "approvals_count": len(approvals),
        "rules_count": len(rules_ref),
    }


def analyze_single_custom_email(
    xlsx_path: Any,
    sender: str,
    text: str,
    received_at: str = "16.11 14:00",
    fallback_xlsx_path: Optional[str] = None,
    ai_fields: Optional[Dict[str, str]] = None,
    material_advisor: Optional[MaterialAdvisor] = None,
) -> Dict[str, Any]:
    db = load_case_database(xlsx_path, fallback_xlsx_path=fallback_xlsx_path)
    return analyze_new_email(db, sender, text, received_at, ai_fields, material_advisor)


def analyze_new_email(
    db: Dict[str, Any],
    sender: str,
    text: str,
    received_at: str,
    ai_fields: Optional[Dict[str, str]] = None,
    material_advisor: Optional[MaterialAdvisor] = None,
    workbook_fields: Optional[Dict[str, Dict[str, str]]] = None,
    workbook_advisor: Optional[BatchMaterialAdvisor] = None,
) -> Dict[str, Any]:
    """Reconcile a new email in queue context without mutating the workbook queue."""
    existing_ids = {email["id"] for email in db["emails"]}
    index = len(existing_ids) + 1
    while f"CHECK-{index:02d}" in existing_ids:
        index += 1
    custom_id = f"CHECK-{index:02d}"
    new_email = {
        "id": custom_id,
        "received_at": received_at,
        "sender": sender,
        "text": text,
    }
    confirmed = dict(workbook_fields or {})
    if ai_fields is not None:
        confirmed[custom_id] = ai_fields

    def advise(email_id, invoice_material, order_material):
        if email_id == custom_id:
            return material_advisor(invoice_material, order_material) if material_advisor else None
        if workbook_advisor:
            return workbook_advisor(email_id, invoice_material, order_material)
        return None

    full_run = analyze_all_emails(
        {**db, "emails": [*db["emails"], new_email]},
        confirmed_ai=confirmed,
        material_advice=advise if material_advisor or workbook_advisor else None,
    )
    return full_run["items"][-1]


if __name__ == "__main__":
    default_xlsx = os.path.join(os.path.dirname(__file__), "data", "case04.xlsx")
    db_data = load_case_database(default_xlsx)
    analysis = analyze_all_emails(db_data)
    print(f"Emails checked: {analysis['summary']['total_emails']}")
    print(f"Ready to pay: {analysis['summary']['ready_to_pay_count']} pcs totaling ${analysis['summary']['total_payable_rub']:,.0f}")
    print(f"Flagged risk/overpayments: ${analysis['summary']['total_prevented_risk_rub']:,.0f}")
    print("Risk breakdown:", json.dumps(analysis["summary"]["risk_breakdown_rub"], ensure_ascii=False))
    print("-" * 100)
    for item in analysis["items"]:
        print(
            f"{item['id']} | Order: {item['order_id']:5s} | Inv: {item['raw_invoice_no']:6s} | "
            f"{item['status_label']:38s} | Stated: ${item['stated_amount']:8.0f} | "
            f"Payable: ${item['payable_amount']:8.0f} | Risk: ${item['prevented_risk']:8.0f} | "
            f"Rules: {','.join(item['triggered_rules'])}"
        )
