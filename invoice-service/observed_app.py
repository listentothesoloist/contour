"""Kubernetes entry point for reconciliation telemetry and intrusion detection."""

import io
import json
import logging
import os
import queue
import re
import threading
import time
import uuid
from collections import Counter, defaultdict, deque
from http.server import ThreadingHTTPServer
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

import psycopg
from psycopg.types.json import Jsonb

from app import Case04RequestHandler, build_static_bundle

OPERATIONS = {
    ("POST", "/api/upload-xlsx"): "workbook.review",
    ("POST", "/api/analyze-custom"): "invoice.check",
    ("POST", "/api/xlsx-review"): "workbook.ai_review",
    ("POST", "/api/extract-ai"): "invoice.ai_extract",
    ("GET", "/api/export-registry.csv"): "registry.export",
    ("GET", "/api/export-audit.csv"): "audit.export",
}
SERVICE = "invoice-reconciliation"
IDS_ENABLED = os.getenv("TARGET_IDS_ENABLED", "true").strip().lower() in {"1", "true", "yes"}
MAX_INSPECT_BODY = 65_536
STATIC_EXTS = (".css", ".js", ".svg", ".ico", ".png", ".jpg", ".woff2")

# Thread-safe sliding window rate tracker per client IP
_RATE_LOCK = threading.Lock()
_REQ_TIMES = defaultdict(deque)
_ERR_TIMES = defaultdict(deque)

# Send telemetry outside the request thread.
_OTLP_QUEUE: "queue.Queue[dict]" = queue.Queue(maxsize=2000)

ATTACK_RULES = (
    (
        "pentest.sqli",
        "SQL Injection",
        "CRITICAL",
        "ERROR",
        re.compile(
            r"(?i)(?:union\s+(?:all\s+)?select|'\s*(?:or|and)\s+['\"\d(]|\"\s*(?:or|and)\s+['\"\d(]|"
            r"\bor\s+1\s*=\s*1\b|\band\s+1\s*=\s*1\b|sleep\s*\(\s*\d|benchmark\s*\(|"
            r"waitfor\s+delay|information_schema|drop\s+table|;\s*(?:select|insert|update|delete|drop)\b|"
            r"'\s*--|%27\s*(?:or|and|--))",
        ),
    ),
    (
        "pentest.path_traversal",
        "Path Traversal / LFI",
        "CRITICAL",
        "ERROR",
        re.compile(
            r"(?i)(?:\.\.[/\\]|%2e%2e[/\\]|%2e%2e%2f|%2e%2e%5c|/etc/passwd|/etc/shadow|/proc/self|win\.ini|boot\.ini)",
        ),
    ),
    (
        "pentest.cmdi",
        "Command Injection / RCE",
        "CRITICAL",
        "ERROR",
        re.compile(
            r"(?i)(?:(?:;|\|\||&&|\|)\s*(?:id|whoami|uname|cat|ls|sh|bash|nc|curl|wget|python3?|perl|php)\b|"
            r"\$\([^)]{1,80}\)|`[^`]{1,80}`|/bin/(?:sh|bash))",
        ),
    ),
    (
        "pentest.ssrf",
        "SSRF / Internal Probe",
        "CRITICAL",
        "ERROR",
        re.compile(
            r"(?i)(?:169\.254\.169\.254|metadata\.google\.internal|kubernetes\.default|"
            r"(?:file|gopher|dict)://|https?://(?:127\.0\.0\.1|localhost|0\.0\.0\.0|host\.docker\.internal)[:/])",
        ),
    ),
    (
        "pentest.xss",
        "XSS",
        "HIGH",
        "ERROR",
        re.compile(
            r"(?i)(?:<\s*script\b|javascript\s*:|on(?:error|load|mouseover|click|focus|toggle)\s*=|"
            r"<\s*(?:svg|img|iframe|body)\b[^>]{0,80}(?:onload|onerror|src\s*=\s*javascript)|alert\s*\(|document\.cookie)",
        ),
    ),
)

SCANNER_UA_RE = re.compile(
    r"(?i)\b(?:sqlmap|nikto|nmap|gobuster|ffuf|dirb|dirbuster|wpscan|nuclei|hydra|"
    r"burp|acunetix|nessus|zaproxy|masscan|wfuzz|feroxbuster|dalfox|xsstrike)\b"
)
SENSITIVE_PATH_RE = re.compile(
    r"(?i)^/(?:\.env|\.git(?:/|$)|\.svn|\.aws|\.htaccess|wp-admin|wp-login|phpmyadmin|"
    r"admin(?:/|$)|administrator|console|debug|actuator|swagger|openapi|graphql|"
    r"api/admin|server-status|metrics|backup|config\.json|secrets|etc/passwd)"
)
BYPASS_HEADERS = ("x-original-url", "x-rewrite-url", "x-custom-ip-authorization", "x-forwarded-host")


def attribute(key, value):
    encoded = {"intValue": str(value)} if isinstance(value, int) else {"stringValue": str(value)}
    return {"key": key, "value": encoded}


def _otlp_worker():
    while True:
        payload = _OTLP_QUEUE.get()
        url = os.environ.get("OTEL_LOGS_URL")
        if url:
            try:
                req = Request(url, json.dumps(payload).encode("utf-8"), {"Content-Type": "application/json"})
                with urlopen(req, timeout=2.5) as response:
                    response.read()
            except (OSError, ValueError):
                logging.warning("OTLP log delivery failed")
        _OTLP_QUEUE.task_done()


def emit_pentest_event(
    *,
    run_id,
    severity,
    operation,
    category,
    risk,
    http_status,
    elapsed_ms,
    source_ip,
    method,
    target_path,
    user_agent,
    snippet,
    exposure,
    message,
):
    attributes = {
        "reconciliation.run_id": str(run_id),
        "operation.name": operation,
        "threat.category": category,
        "threat.risk": risk,
        "http.request.method": method,
        "http.response.status_code": int(http_status),
        "duration.ms": int(elapsed_ms),
        "client.address": source_ip,
        "url.path": target_path[:300],
        "user_agent.original": user_agent[:160],
        "ids.payload_snippet": snippet[:220],
        "ids.response_exposure": exposure,
        "event.source": "real_pentest",
    }
    emit_log("target.ids", severity, message, attributes)


def emit_log(scope, severity, message, attributes):
    number = {"INFO": 9, "WARN": 13, "ERROR": 17}[severity]
    payload = {
        "resourceLogs": [{
            "resource": {"attributes": [attribute("service.name", SERVICE)]},
            "scopeLogs": [{
                "scope": {"name": scope},
                "logRecords": [{
                    "timeUnixNano": str(time.time_ns()),
                    "severityText": severity,
                    "severityNumber": number,
                    "body": {"stringValue": message[:320]},
                    "attributes": [attribute(k, v) for k, v in attributes.items()],
                }],
            }],
        }]
    }
    try:
        _OTLP_QUEUE.put_nowait(payload)
    except queue.Full:
        pass


def connect_audit():
    return psycopg.connect(
        host="postgres", dbname="orders", user="orders",
        password=os.environ["POSTGRES_PASSWORD"], connect_timeout=2,
        options="-c statement_timeout=2000",
    )


def save_audit(run_id, operation, status, elapsed_ms, counts):
    with connect_audit() as conn:
        conn.execute(
            """INSERT INTO reconciliation_runs
               (run_id, operation, http_status, duration_ms, status_counts)
               VALUES (%s, %s, %s, %s, %s)""",
            (run_id, operation, status, elapsed_ms, Jsonb(counts)),
        )


def _record_rate(source_ip, is_static, http_status):
    now = time.monotonic()
    cutoff = now - 10.0
    with _RATE_LOCK:
        req_q = _REQ_TIMES[source_ip]
        err_q = _ERR_TIMES[source_ip]
        while req_q and req_q[0] < cutoff:
            req_q.popleft()
        while err_q and err_q[0] < cutoff:
            err_q.popleft()
        if not is_static:
            req_q.append(now)
        if http_status >= 400:
            err_q.append(now)
        return len(req_q), len(err_q)


def detect_pentest_threats(method, raw_path, headers, body_text, http_status, req_10s, err_10s):
    parsed = urlparse(raw_path)
    path_only = unquote(parsed.path or "/")
    full_target = unquote(raw_path or "/")
    user_agent = str(headers.get("User-Agent") or "")
    auth_header = str(headers.get("Authorization") or "")
    referer = str(headers.get("Referer") or "")
    cookie = str(headers.get("Cookie") or "")

    # Skip binary/huge base64 Excel payloads from body regex to avoid false positives on benign uploads
    body_for_scan = "" if ("data_base64" in body_text and len(body_text) > 8000) else body_text
    haystack_url_body = f"{full_target}\n{body_for_scan}\n{referer}\n{cookie}"
    haystack_ssrf = f"{full_target}\n{body_for_scan}"

    matches = []
    for op, category, risk, severity, pattern in ATTACK_RULES:
        target_text = haystack_ssrf if op == "pentest.ssrf" else haystack_url_body
        m = pattern.search(target_text)
        if m:
            start = max(0, m.start() - 20)
            end = min(len(target_text), m.end() + 40)
            snippet = target_text[start:end].replace("\n", " ").strip()
            matches.append((op, category, risk, severity, snippet))

    if SCANNER_UA_RE.search(user_agent):
        matches.append((
            "pentest.scanner",
            "Security Scanner",
            "HIGH",
            "WARN",
            f"User-Agent: {user_agent[:120]}",
        ))

    if SENSITIVE_PATH_RE.search(path_only):
        matches.append((
            "pentest.recon",
            "Sensitive Path Recon",
            "HIGH",
            "WARN",
            f"{method} {full_target[:140]}",
        ))

    bypass_found = [h for h in BYPASS_HEADERS if headers.get(h)]
    if auth_header or bypass_found or "eyJ" in full_target:
        detail = ", ".join(bypass_found) if bypass_found else ("Authorization header" if auth_header else "JWT in URL")
        matches.append((
            "pentest.auth_abuse",
            "Auth / Header Abuse",
            "HIGH",
            "WARN",
            f"{detail} on {path_only[:100]}",
        ))

    if method not in ("GET", "POST", "HEAD"):
        matches.append((
            "pentest.method_probe",
            "Unsafe HTTP Method",
            "MEDIUM",
            "WARN",
            f"{method} {path_only[:120]}",
        ))

    if req_10s >= 12 or err_10s >= 5:
        matches.append((
            "pentest.bruteforce",
            "Brute Force / Rate Spike",
            "HIGH",
            "ERROR",
            f"{req_10s} req / {err_10s} errors in 10s",
        ))

    if not matches and http_status >= 400:
        sev = "ERROR" if http_status >= 500 else "WARN"
        risk = "HIGH" if http_status >= 500 else "MEDIUM"
        matches.append((
            "pentest.http_error",
            "HTTP 5xx Server Crash" if http_status >= 500 else "HTTP 4xx Probe / Fuzzing",
            risk,
            sev,
            f"{method} {full_target[:120]} -> HTTP {http_status}",
        ))

    if not matches:
        return None

    # Pick highest-priority threat as primary, listing any co-occurring categories
    rank = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    matches.sort(key=lambda item: (-rank.get(item[2], 0), item[3] != "ERROR"))
    op, category, risk, severity, snippet = matches[0]
    extra_cats = list(dict.fromkeys(m[1] for m in matches[1:]))

    if http_status >= 500:
        exposure = "server_error_5xx"
        severity = "ERROR"
        if risk == "MEDIUM":
            risk = "HIGH"
    elif http_status < 300 and op in {
        "pentest.sqli", "pentest.path_traversal", "pentest.cmdi", "pentest.ssrf", "pentest.xss"
    }:
        exposure = "accepted_200"
        severity = "ERROR"
        risk = "CRITICAL"
    elif http_status >= 400:
        exposure = "rejected_4xx"
    else:
        exposure = f"http_{http_status}"

    suffix = f" (+ {', '.join(extra_cats)})" if extra_cats else ""
    message = f"[{category}] {method} {path_only[:100]} -> HTTP {http_status}{suffix}"
    return {
        "operation": op,
        "category": category,
        "risk": risk,
        "severity": severity,
        "snippet": snippet,
        "exposure": exposure,
        "message": message,
    }


class ObservedHandler(Case04RequestHandler):
    def _client_ip(self):
        xff = self.headers.get("X-Forwarded-For")
        if xff:
            return xff.split(",")[0].strip()[:64]
        xri = self.headers.get("X-Real-IP")
        if xri:
            return xri.strip()[:64]
        return str(self.client_address[0]) if self.client_address else "unknown"

    def _buffer_small_body(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return ""
        if not 0 < length <= MAX_INSPECT_BODY:
            return ""
        raw = self.rfile.read(length)
        self.rfile = io.BytesIO(raw)
        return raw.decode("utf-8", errors="ignore")

    def do_GET(self):
        if urlparse(self.path).path == "/healthz":
            super()._send_json({"ok": True})
            return
        self.observe(super().do_GET)

    def do_POST(self):
        self.observe(super().do_POST)

    def do_HEAD(self):
        if urlparse(self.path).path == "/healthz":
            self.send_response(200)
            self.end_headers()
            return
        self.observe(super().do_HEAD)

    def do_PUT(self):
        self.observe(lambda: self.send_error(405, "Method Not Allowed"))

    def do_DELETE(self):
        self.observe(lambda: self.send_error(405, "Method Not Allowed"))

    def do_PATCH(self):
        self.observe(lambda: self.send_error(405, "Method Not Allowed"))

    def do_OPTIONS(self):
        self.observe(lambda: self.send_error(405, "Method Not Allowed"))

    def observe(self, handler):
        parsed_path = urlparse(self.path).path
        operation = OPERATIONS.get((self.command, parsed_path))
        self.run_id = uuid.uuid4()
        self.status = 500
        self.counts = {}
        self.ai_unavailable = False
        body_text = self._buffer_small_body() if self.command in ("POST", "PUT", "PATCH", "DELETE") else ""
        started = time.monotonic()
        try:
            handler()
        finally:
            elapsed_ms = int((time.monotonic() - started) * 1000)
            if operation:
                try:
                    save_audit(self.run_id, operation, self.status, elapsed_ms, self.counts)
                except psycopg.Error:
                    logging.warning("Audit write failed for %s", self.run_id)
                severity = "ERROR" if self.status >= 500 else "WARN" if self.status >= 400 else "INFO"
                emit_log("target.reconciliation", severity, operation, {
                    "reconciliation.run_id": str(self.run_id),
                    "operation.name": operation,
                    "http.response.status_code": self.status,
                    "duration.ms": elapsed_ms,
                    "event.source": "reconciliation",
                })
            if IDS_ENABLED:
                source_ip = self._client_ip()
                is_static = parsed_path.endswith(STATIC_EXTS)
                req_10s, err_10s = _record_rate(source_ip, is_static, self.status)
                finding = detect_pentest_threats(
                    self.command,
                    self.path,
                    self.headers,
                    body_text,
                    self.status,
                    req_10s,
                    err_10s,
                )
                if finding:
                    emit_pentest_event(
                        run_id=self.run_id,
                        severity=finding["severity"],
                        operation=finding["operation"],
                        category=finding["category"],
                        risk=finding["risk"],
                        http_status=self.status,
                        elapsed_ms=elapsed_ms,
                        source_ip=source_ip,
                        method=self.command,
                        target_path=self.path,
                        user_agent=str(self.headers.get("User-Agent") or ""),
                        snippet=finding["snippet"],
                        exposure=finding["exposure"],
                        message=finding["message"],
                    )
            self.run_id = None

    def send_response(self, code, message=None):
        super().send_response(code, message)
        if getattr(self, "run_id", None):
            self.status = code
            self.send_header("X-Reconciliation-Run-ID", str(self.run_id))

    def _send_json(self, data, status=200):
        if getattr(self, "run_id", None):
            items = data.get("data", {}).get("items", [])
            if isinstance(data.get("item"), dict):
                items = [data["item"]]
            self.counts = dict(Counter(
                item["status_code"] for item in items
                if isinstance(item, dict) and "status_code" in item
            ))
            self.ai_unavailable = bool(data.get("ai_message"))
        super()._send_json(data, status)

    def log_request(self, code="-", size="-"):
        pass


if __name__ == "__main__":
    build_static_bundle()
    with connect_audit() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS reconciliation_runs (
            run_id uuid PRIMARY KEY,
            created_at timestamptz NOT NULL DEFAULT now(),
            operation text NOT NULL,
            http_status integer NOT NULL,
            duration_ms integer NOT NULL,
            status_counts jsonb NOT NULL
        )""")
    threading.Thread(target=_otlp_worker, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", 8040), ObservedHandler).serve_forever()
