"""Audit the current namespace using Kubernetes metadata and static rules."""

import base64
import gzip
import hashlib
import json
import re
import ssl
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from uuid import uuid4

from audit import MODEL, create_report, model_summary
from package_audit import PackageAudit

NAMESPACE = "observability"
ACCOUNT = Path("/var/run/secrets/kubernetes.io/serviceaccount")
API = "https://kubernetes.default.svc"
RESULT = f"/api/v1/namespaces/{NAMESPACE}/configmaps/target-audit-result"
REPORTS_DIR = Path("/reports")
MAX_PVC_REPORTS = 50
INTERVAL = 60
WORKLOADS = {"invoice-service", "postgres", "otel-collector", "clickhouse", "grafana", "log-generator"}
AUDIT_APPS = {"target-security-audit"}
SECRET_NAME = re.compile(r"PASSWORD|SECRET|API_KEY|ACCESS_TOKEN|PRIVATE_KEY", re.IGNORECASE)
SECRET_ARG_EQ = re.compile(
    r"^(-{1,2}[a-z0-9_.-]*(?:password|passwd|secret|api[_-]?key|access[_-]?token|private[_-]?key|token))=(.+)$",
    re.IGNORECASE,
)
SECRET_ARG_FLAG = re.compile(
    r"^(-{1,2}[a-z0-9_.-]*(?:password|passwd|secret|api[_-]?key|access[_-]?token|private[_-]?key|token))$",
    re.IGNORECASE,
)
REPORT_KEY_RE = re.compile(r"^target-passive-audit-(\d{8}T\d{6})-[a-f0-9]{8}\.json$")
ENDPOINTS = {
    "pods": "/api/v1",
    "deployments": "/apis/apps/v1",
    "services": "/api/v1",
    "networkpolicies": "/apis/networking.k8s.io/v1",
    "roles": "/apis/rbac.authorization.k8s.io/v1",
    "rolebindings": "/apis/rbac.authorization.k8s.io/v1",
}


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def request(context, path, changes=None):
    headers = {"Authorization": f"Bearer {(ACCOUNT / 'token').read_text().strip()}"}
    data = None
    if changes is not None:
        data = json.dumps(changes).encode()
        headers["Content-Type"] = "application/merge-patch+json"
    message = Request(API + path, data=data, headers=headers, method="PATCH" if data else "GET")
    with urlopen(message, context=context, timeout=8) as response:
        return json.load(response)


def inventory(context, steps):
    resources = {}
    for kind, prefix in ENDPOINTS.items():
        path = f"{prefix}/namespaces/{NAMESPACE}/{kind}"
        resources[kind] = sorted(
            (item for item in request(context, path)["items"]
             if not item["metadata"].get("deletionTimestamp")
             and item["metadata"].get("labels", {}).get("app") not in AUDIT_APPS),
            key=lambda item: item["metadata"]["name"],
        )
        steps.append({"stage": "audit-inventory", "at": timestamp(),
                      "activity": f"GET {path} · selected objects: {len(resources[kind])}."})
    return resources


def secret_like_args(container):
    tokens = [*(container.get("command") or ()), *(container.get("args") or ())]
    found = []
    for index, raw in enumerate(tokens):
        token = str(raw)
        eq_match = SECRET_ARG_EQ.match(token)
        if eq_match:
            val = eq_match.group(2).strip("\"'")
            if val and not val.startswith("$"):
                found.append(eq_match.group(1))
            continue
        flag_match = SECRET_ARG_FLAG.match(token)
        if flag_match and index + 1 < len(tokens):
            next_val = str(tokens[index + 1]).strip("\"'")
            if next_val and not next_val.startswith("$") and not next_val.startswith("-"):
                found.append(flag_match.group(1))
    return list(dict.fromkeys(found))


def pod_snapshot(pod):
    spec = pod["spec"]
    volumes = spec.get("volumes", [])
    return {
        "name": pod["metadata"]["name"],
        "labels": pod["metadata"].get("labels", {}),
        "hostNetwork": spec.get("hostNetwork", False),
        "hostPID": spec.get("hostPID", False),
        "hostIPC": spec.get("hostIPC", False),
        "hostVolumes": [item["name"] for item in volumes if "hostPath" in item],
        "tokenMounted": any("serviceAccountToken" in source for volume in volumes
                            for source in volume.get("projected", {}).get("sources", [])),
        "serviceAccount": spec.get("serviceAccountName", "default"),
        "securityContext": spec.get("securityContext", {}),
        "containers": [
            {
                "name": container["name"],
                "securityContext": container.get("securityContext", {}),
                "secretLikeLiteralVariables": [
                    entry["name"] for entry in container.get("env", [])
                    if SECRET_NAME.search(entry["name"]) and entry.get("value")
                ],
                "secretLikeArgs": secret_like_args(container),
                "configMapEnvFrom": [
                    entry["configMapRef"]["name"]
                    for entry in container.get("envFrom", [])
                    if isinstance(entry.get("configMapRef"), dict) and entry["configMapRef"].get("name")
                ],
            }
            for field in ("containers", "initContainers", "ephemeralContainers")
            for container in spec.get(field, [])
        ],
    }


def snapshot(resources):
    def fields(kind, source=None, **defaults):
        return [
            {"name": item["metadata"]["name"],
             **{key: (item[source] if source else item).get(key, default) for key, default in defaults.items()}}
            for item in resources[kind]
        ]

    images = {}
    for pod in resources["pods"]:
        for group in ("containerStatuses", "initContainerStatuses", "ephemeralContainerStatuses"):
            for container in pod.get("status", {}).get(group, []):
                digest = container.get("imageID")
                if not digest:
                    continue
                image = images.setdefault(digest, {
                    "digest": digest, "image": container["image"], "usedBy": [], "findings": [],
                    "status": "not_scanned", "reason": "Package details have not been collected yet.",
                })
                image["usedBy"].append(f"{pod['metadata']['name']}/{container['name']}")
    return {
        "namespace": NAMESPACE,
        "pods": [pod_snapshot(item) for item in resources["pods"]],
        "deployments": [item["metadata"]["name"] for item in resources["deployments"]],
        "services": fields("services", "spec", type="ClusterIP", ports=[]),
        "networkPolicies": fields("networkpolicies", spec={}),
        "roles": fields("roles", rules=[]),
        "roleBindings": fields("rolebindings", roleRef={}),
        "images": [images[key] for key in sorted(images)],
    }


def report_sort_key(filename):
    match = REPORT_KEY_RE.match(filename)
    return (1, match.group(1), filename) if match else (0, "", filename)


def persist_report_pvc(key, payload):
    if not REPORTS_DIR.is_dir():
        return False
    target = REPORTS_DIR / key
    tmp = REPORTS_DIR / f".{key}.tmp"
    tmp.write_bytes(payload)
    tmp.replace(target)
    stored = sorted(
        (path for path in REPORTS_DIR.iterdir() if path.is_file() and REPORT_KEY_RE.match(path.name)),
        key=lambda path: report_sort_key(path.name),
        reverse=True,
    )
    for stale in stored[MAX_PVC_REPORTS:]:
        stale.unlink(missing_ok=True)
    return True


def publish(context, report):
    key = f"{report['run']}.json"
    payload = json.dumps(report, ensure_ascii=False, separators=(",", ":")).encode()
    try:
        persist_report_pvc(key, payload)
    except OSError as error:
        print(f"PVC report persistence warning: {type(error).__name__}", flush=True)
    data = base64.b64encode(gzip.compress(payload, compresslevel=6)).decode()
    budget = 850_000
    budget -= len(data.encode()) + len(key)
    if budget < 0:
        raise ValueError("report exceeds ConfigMap storage budget")
    current = request(context, RESULT)
    plain = current.get("data") or {}
    binary = current.get("binaryData") or {}
    existing = plain | binary
    updated = {"data": {}, "binaryData": {key: data}}
    kept = 0
    for old in sorted(existing, key=report_sort_key, reverse=True):
        if old == key:
            continue
        entry_size = len(existing[old].encode()) + len(old)
        if REPORT_KEY_RE.match(old) and kept < 2 and budget - entry_size >= 0:
            budget -= entry_size
            kept += 1
        else:
            updated["binaryData" if old in binary else "data"][old] = None
    request(context, RESULT, {"metadata": {"resourceVersion": current["metadata"]["resourceVersion"]}, **updated})


def main():
    if (ACCOUNT / "namespace").read_text().strip() != NAMESPACE:
        raise ValueError("unexpected namespace")
    context = ssl.create_default_context(cafile=str(ACCOUNT / "ca.crt"))
    access = {
        "source": "In-cluster Kubernetes API over HTTPS",
        "identity": f"system:serviceaccount:{NAMESPACE}:target-passive-auditor",
        "authorization": "RoleBinding target-passive-auditor · read resources and write report to target-audit-result",
        "scope": NAMESPACE,
    }
    packages = PackageAudit()
    previous = None
    while True:
        wait = INTERVAL
        steps = [{"stage": "audit-inventory", "at": timestamp(),
                  "activity": "Used the agent's standard ServiceAccount credentials for Kubernetes API requests."}]
        try:
            resources = inventory(context, steps)
            ready = {item["metadata"]["name"] for item in resources["deployments"]
                     if item.get("status", {}).get("readyReplicas", 0) > 0}
            if previous is None and not WORKLOADS <= ready:
                time.sleep(5)
                continue
            evidence = snapshot(resources)
            steps.append({"stage": "audit-evidence", "at": timestamp(),
                          "activity": "Captured snapshot of configuration fields and image digests. Environment variable values were excluded."})
            steps.extend(packages.enrich(evidence))
            fingerprint = hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest()
            if fingerprint != previous:
                evidence["capturedAt"] = timestamp()
                run = f"target-passive-audit-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{uuid4().hex[:8]}"
                report = create_report(evidence, run=run, access=access, execution_steps=steps)
                try:
                    report["model_review"] = model_summary(report, ready_timeout=15, response_timeout=90)
                except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
                    report["model_review"] = {"status": "unavailable", "model": MODEL, "reason": type(error).__name__}
                report["execution_steps"].append({
                    "stage": "audit-model", "at": timestamp(),
                    "activity": ("Qwen generated a summary based on already verified rules and matches."
                                 if report["model_review"]["status"] == "ok"
                                 else "Qwen is unavailable. Priorities were calculated from CISA KEV and finding severity."),
                })
                report["execution_steps"].append({
                    "stage": "audit-interface", "at": timestamp(),
                    "activity": "Full report saved to PVC target-audit-reports (/reports) and published to ConfigMap target-audit-result.",
                })
                publish(context, report)
                previous = fingerprint
                print(f"{run}: {len(report['findings'])} findings", flush=True)
        except (OSError, ValueError) as error:
            print(f"Passive audit unavailable: {type(error).__name__} {getattr(error, 'code', '')}", flush=True)
            wait = 10
        time.sleep(wait)


if __name__ == "__main__":
    main()
