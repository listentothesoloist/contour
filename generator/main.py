import json
import math
import os
import random
import sys
import time
import urllib.request
from uuid import uuid4

INTERVAL = 3.0
ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318").rstrip("/")
RESOURCE = {
    "attributes": [
        {"key": "service.name", "value": {"stringValue": "system-generator"}},
        {"key": "deployment.environment.name", "value": {"stringValue": "demo"}},
    ]
}
SCOPE = {"name": "demo.security"}
LEVELS = {"INFO": 9, "WARN": 13, "ERROR": 17}

THREAT_EVENTS = (
    {
        "event_type": "security_alert",
        "severity": "ERROR",
        "operation": "security.sqli",
        "category": "SQL Injection",
        "risk": "CRITICAL",
        "http_status": 403,
        "path": "/api/invoices?order=' OR 1=1--",
        "ips": ("10.244.0.47", "192.168.65.21", "172.18.0.19"),
        "message": "Detected SQL injection attempt in invoice filter parameter",
        "weight": 22,
    },
    {
        "event_type": "security_alert",
        "severity": "ERROR",
        "operation": "security.bruteforce",
        "category": "Brute Force",
        "risk": "HIGH",
        "http_status": 429,
        "path": "/api/auth/login",
        "ips": ("192.168.65.14", "10.244.0.63", "172.18.0.44"),
        "message": "Password brute-force detected: multiple failed login attempts within 10s",
        "weight": 20,
    },
    {
        "event_type": "security_warning",
        "severity": "WARN",
        "operation": "security.auth_denied",
        "category": "Unauthorized Access",
        "risk": "HIGH",
        "http_status": 403,
        "path": "/api/export-registry.csv",
        "ips": ("10.244.0.82", "192.168.65.38", "172.18.0.27"),
        "message": "Rejected unauthorized request to restricted payment registry (401/403)",
        "weight": 20,
    },
    {
        "event_type": "security_alert",
        "severity": "ERROR",
        "operation": "security.requisites_spoof",
        "category": "Payment Spoofing",
        "risk": "CRITICAL",
        "http_status": 403,
        "path": "/api/upload-xlsx",
        "ips": ("10.244.0.31", "192.168.65.52", "172.18.0.15"),
        "message": "Attempted to spoof vendor bank details without ERP approval",
        "weight": 18,
    },
    {
        "event_type": "security_alert",
        "severity": "ERROR",
        "operation": "security.token_leak",
        "category": "Token Leak",
        "risk": "CRITICAL",
        "http_status": 401,
        "path": "/api/admin/audit",
        "ips": ("10.244.0.95", "192.168.65.77", "172.18.0.33"),
        "message": "Detected attempt to transmit ServiceAccount JWT in an external request header",
        "weight": 15,
    },
)

BACKGROUND_INFO_EVENTS = (
    {
        "event_type": "system",
        "severity": "INFO",
        "operation": "telemetry.heartbeat",
        "category": "Baseline",
        "risk": "LOW",
        "http_status": 200,
        "path": "/healthz",
        "ips": ("10.244.0.1",),
        "message": "Scheduled telemetry sensor health check completed",
    },
)

METRICS = (
    ("demo.system.cpu.utilization", "%", "Simulated CPU utilization"),
    ("demo.system.memory.used", "By", "Simulated memory usage"),
    ("demo.system.request.duration.p95", "ms", "Simulated request latency at p95"),
    ("demo.system.queue.depth", "1", "Simulated number of queued tasks"),
    ("demo.system.error.rate", "%", "Simulated percentage of failed requests"),
)


def log_record(run_id, step, event):
    source_ip = random.choice(event["ips"])
    attributes = [
        {"key": "event.type", "value": {"stringValue": event["event_type"]}},
        {"key": "operation.name", "value": {"stringValue": event["operation"]}},
        {"key": "threat.category", "value": {"stringValue": event["category"]}},
        {"key": "threat.risk", "value": {"stringValue": event["risk"]}},
        {"key": "http.response.status_code", "value": {"intValue": str(event["http_status"])}},
        {"key": "client.address", "value": {"stringValue": source_ip}},
        {"key": "url.path", "value": {"stringValue": event["path"]}},
        {"key": "reconciliation.run_id", "value": {"stringValue": run_id}},
        {"key": "reconciliation.step", "value": {"intValue": str(step)}},
        {"key": "demo.synthetic", "value": {"boolValue": True}},
    ]
    return {
        "timeUnixNano": str(time.time_ns()),
        "severityText": event["severity"],
        "severityNumber": LEVELS[event["severity"]],
        "body": {"stringValue": event["message"]},
        "attributes": attributes,
    }


def continuous_logs():
    run_id = str(uuid4())
    weights = [item["weight"] for item in THREAT_EVENTS]
    selected = [
        random.choice(BACKGROUND_INFO_EVENTS),
        *random.choices(THREAT_EVENTS, weights=weights, k=4),
    ]
    return [log_record(run_id, step, event) for step, event in enumerate(selected, start=1)]


def burst_dangerous_logs():
    run_id = str(uuid4())
    records = [log_record(run_id, step, event) for step, event in enumerate(THREAT_EVENTS, start=1)]
    return run_id, records


def metric_records(elapsed):
    load = 0.5 + math.sin(elapsed / 22) * 0.35
    values = (
        18 + 75 * load + random.uniform(-3, 3),
        round((420 + 500 * load + random.uniform(-18, 18)) * 1024**2),
        42 + 180 * load**2 + random.uniform(-5, 10),
        max(0, round(40 * load**2 + random.uniform(-2, 4))),
        max(0.0, 4 * load**3 + random.uniform(-0.25, 0.25)),
    )
    now = str(time.time_ns())
    return [
        {
            "name": name,
            "description": description,
            "unit": unit,
            "gauge": {"dataPoints": [{"timeUnixNano": now, "asDouble": float(value)}]},
        }
        for (name, unit, description), value in zip(METRICS, values)
    ]


def publish(signal, scoped, rejected_field, raise_on_error=False):
    resource_key, scope_key = (
        ("resourceLogs", "scopeLogs") if signal == "logs" else ("resourceMetrics", "scopeMetrics")
    )
    payload = {resource_key: [{"resource": RESOURCE, scope_key: [{"scope": SCOPE, **scoped}]}]}
    request = urllib.request.Request(
        f"{ENDPOINT}/v1/{signal}", json.dumps(payload).encode(), {"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            result = json.load(response)
        partial = result.get("partialSuccess", {})
        if int(partial.get(rejected_field, 0)):
            if raise_on_error:
                raise RuntimeError(f"OTLP {signal} rejected records: {partial}")
            print(f"OTLP {signal} rejected records: {partial}", flush=True)
    except (OSError, ValueError) as error:
        if raise_on_error:
            raise
        print(f"OTLP {signal} delivery failed: {error}", flush=True)


def run_burst():
    run_id, records = burst_dangerous_logs()
    publish("logs", {"logRecords": records}, "rejectedLogRecords", raise_on_error=True)
    errors = sum(1 for item in THREAT_EVENTS if item["severity"] == "ERROR")
    warnings = sum(1 for item in THREAT_EVENTS if item["severity"] == "WARN")
    print(json.dumps({
        "runId": run_id,
        "total": len(records),
        "errors": errors,
        "warnings": warnings,
        "categories": [item["category"] for item in THREAT_EVENTS],
    }, ensure_ascii=False), flush=True)


def main():
    if "--burst" in sys.argv[1:]:
        run_burst()
        return
    started = deadline = time.monotonic()
    while True:
        publish("logs", {"logRecords": continuous_logs()}, "rejectedLogRecords")
        publish("metrics", {"metrics": metric_records(time.monotonic() - started)}, "rejectedDataPoints")
        deadline = max(deadline + INTERVAL, time.monotonic())
        time.sleep(max(0, deadline - time.monotonic()))


if __name__ == "__main__":
    main()
