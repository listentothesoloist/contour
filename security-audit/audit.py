import hashlib
import json
import os
import time
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

LEVELS = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
MODEL_URL = "http://127.0.0.1:8070"
MODEL = "Qwen2.5-1.5B-Instruct"
EXPECTED_ROUTES = (
    ("invoice-service", "postgres", 5432),
    ("invoice-service", "otel-collector", 4318),
    ("log-generator", "otel-collector", 4318),
    ("otel-collector", "clickhouse", 9000),
    ("grafana", "clickhouse", 9000),
)


def selects(labels, selector):
    if any(labels.get(key) != value for key, value in selector.get("matchLabels", {}).items()):
        return False
    for expression in selector.get("matchExpressions", []):
        key, operator = expression["key"], expression["operator"]
        values = expression.get("values", [])
        if operator == "In" and (key not in labels or labels[key] not in values):
            return False
        if operator == "NotIn" and labels.get(key) in values:
            return False
        if operator == "Exists" and key not in labels:
            return False
        if operator == "DoesNotExist" and key in labels:
            return False
    return True


def configuration_findings(snapshot, add):
    for pod in snapshot["pods"]:
        name = f"Pod/{pod['name']}"
        context = pod.get("securityContext") or {}
        host_flags = [key for key in ("hostNetwork", "hostPID", "hostIPC") if pod.get(key)]
        if host_flags or pod["hostVolumes"]:
            add("POD-HOST-ACCESS", name, "HIGH", "Pod has access to host node resources",
                f"Flags: {host_flags}. hostPath volumes: {pod['hostVolumes']}.",
                "Disable host namespace access and replace hostPath mounts with standard volumes.",
                "Re-verify the Pod specification and confirm normal application startup.")
        if pod["tokenMounted"]:
            sa = pod.get("serviceAccount") or "default"
            if sa == "default":
                add("POD-SA-TOKEN", name, "MEDIUM", "Pod mounts the default ServiceAccount token",
                    f"Detected projected serviceAccountToken, ServiceAccount: {sa}. Token necessity was not evaluated.",
                    "Disable automountServiceAccountToken where the application does not require Kubernetes API access.",
                    "Confirm that the Pod starts without a projected serviceAccountToken.")
            else:
                add("POD-SA-TOKEN", name, "LOW", f"Pod mounts a dedicated ServiceAccount token ({sa})",
                    f"Detected projected serviceAccountToken for dedicated ServiceAccount {sa}.",
                    "Review bound Role/RoleBinding permissions and token expiration against least-privilege requirements.",
                    "Verify ServiceAccount RBAC permissions and confirm no excess privileges are granted.",
                    status="requires_review")
        for container in pod["containers"]:
            resource = f"{name}/{container['name']}"
            security = container.get("securityContext") or {}
            if security.get("privileged") is True:
                add("CTR-PRIVILEGED", resource, "HIGH", "Privileged mode is enabled",
                    "securityContext.privileged=true.",
                    "Disable privileged mode and retain only the minimum required capabilities.",
                    "Verify the updated Pod specification and readiness status.")
            if security.get("allowPrivilegeEscalation") is not False:
                add("CTR-PRIVILEGE-GUARD", resource, "MEDIUM", "Privilege escalation is not explicitly disabled",
                    "allowPrivilegeEscalation=false is not set.",
                    "Set allowPrivilegeEscalation: false.",
                    "Verify the securityContext field in the updated Pod.")
            if security.get("runAsNonRoot", context.get("runAsNonRoot")) is not True:
                add("CTR-NONROOT", resource, "LOW", "Non-root execution is not enforced",
                    "Effective runAsNonRoot is not set to true. Actual runtime UID was not measured.",
                    "Verify an allowed non-root UID for the image and enable runAsNonRoot.",
                    "Verify securityContext and confirm a successful rollout.")
            seccomp = security.get("seccompProfile") or context.get("seccompProfile") or {}
            if seccomp.get("type") not in ("RuntimeDefault", "Localhost"):
                add("CTR-SECCOMP", resource, "LOW", "Seccomp profile is not explicitly set or restricted",
                    "No effective seccompProfile of type RuntimeDefault or Localhost is present in the specification.",
                    "Explicitly enable seccompProfile: RuntimeDefault if the image is compatible.",
                    "Verify the seccomp profile in the specification and container readiness.")
            if security.get("readOnlyRootFilesystem") is not True:
                add("CTR-ROOTFS", resource, "LOW", "Root filesystem is not enforced as read-only",
                    "readOnlyRootFilesystem=true is not set.",
                    "Enable readOnlyRootFilesystem and mount dedicated writable volumes for working directories.",
                    "Verify the configuration, readiness probes, and write operations.")
            capabilities = security.get("capabilities") or {}
            if "ALL" not in (capabilities.get("drop") or []):
                add("CTR-CAPABILITIES", resource, "LOW", "Default Linux capabilities are not dropped",
                    "ALL is missing from securityContext.capabilities.drop.",
                    "Start with drop: [ALL] and add back only capabilities required by the image.",
                    "Verify the container security profile and standard health checks.")
            for variable in container["secretLikeLiteralVariables"]:
                add("CTR-LITERAL-PASSWORD", resource, "HIGH", "Sensitive environment variable is set as a literal value",
                    f"Variable name: {variable}. Value excluded from snapshot.",
                    "Pass the value via a Kubernetes Secret and rotate exposed credentials if necessary.",
                    "Verify secretKeyRef usage without reading the secret value.")
            for arg_name in container.get("secretLikeArgs") or []:
                add("CTR-LITERAL-ARG-SECRET", resource, "HIGH", "Sensitive literal value passed in startup arguments",
                    f"Startup argument: {arg_name}. Value excluded from snapshot.",
                    "Remove the secret from command/args and supply it via a Kubernetes Secret or mounted file.",
                    "Verify container command/args and confirm no secret values remain in the Pod spec.")
            for cm_name in container.get("configMapEnvFrom") or []:
                add("CTR-ENVFROM-CONFIGMAP", resource, "LOW", "All environment variables are loaded via envFrom ConfigMap",
                    f"Attached ConfigMap: {cm_name}. ConfigMap contents were not read.",
                    "Ensure the ConfigMap contains no sensitive data and prefer explicit key references if needed.",
                    "Audit ConfigMap keys to confirm absence of passwords, tokens, and API keys.",
                    status="requires_review")

    policies = [policy for policy in snapshot["networkPolicies"] if policy["name"] != "target-security-audit-isolation"]
    if not policies:
        add("NET-NO-POLICIES", "Namespace/observability", "MEDIUM", "No NetworkPolicies defined for application workloads",
            "No inter-service network policies are present in the snapshot. Actual reachability was not measured.",
            "Document required connections for Target, Collector, log generator, PostgreSQL, ClickHouse, and Grafana. "
            "After confirming CNI support, enforce allowed routes with NetworkPolicies.",
            "Verify policy selectors and permitted traffic flows alongside standard service health checks.")
    else:
        for pod in snapshot["pods"]:
            directions = set()
            for policy in policies:
                spec = policy["spec"]
                if selects(pod.get("labels") or {}, spec["podSelector"]):
                    directions.update(spec.get("policyTypes") or (["Ingress", "Egress"] if spec.get("egress") else ["Ingress"]))
            missing = sorted({"Ingress", "Egress"} - directions)
            if missing:
                add("NET-POD-ISOLATION", f"Pod/{pod['name']}", "MEDIUM", "Pod is partially or fully uncovered by NetworkPolicies",
                    f"Selectors impose no restrictions for directions: {', '.join(missing)}.",
                    "Enforce required inter-service allowances for the application and deny all other traffic.",
                    "Match policy selectors against Pod labels and verify standard service connectivity.")
    services = {service["name"]: service for service in snapshot["services"]}
    for source, target, port in EXPECTED_ROUTES:
        service = services.get(target, {})
        if not any(item["port"] == port and item.get("protocol", "TCP") == "TCP" for item in service.get("ports", [])):
            add("NET-EXPECTED-PORT", f"Service/{target}", "MEDIUM", "Expected inter-service port is missing",
                f"By design, {source} connects to {target}:{port}/TCP. This port is absent from the snapshot.",
                "Reconcile the Service definition and client configuration with the environment architecture.",
                "Verify the declared port and confirm normal application operation.", status="requires_review")
    for service in snapshot["services"]:
        if service["type"] in ("LoadBalancer", "NodePort", "ExternalName"):
            add("NET-SERVICE-EXPOSURE", f"Service/{service['name']}", "MEDIUM",
                "Service uses an externally exposed type or external name",
                f"spec.type={service['type']}. Exposure boundary depends on network configuration.",
                "Verify whether external publication is intentional. Use ClusterIP for internal dependencies.",
                "Check Service type and ports against the approved architecture diagram.")
    for role in snapshot["roles"]:
        if any("*" in rule.get(field, []) for rule in role["rules"] for field in ("verbs", "resources")):
            add("RBAC-WILDCARD", f"Role/{role['name']}", "HIGH", "Role rules contain a wildcard",
                "Wildcard '*' is present in verbs or resources. Actual role usage requires separate evaluation.",
                "Replace wildcards with the exact set of resources and verbs required by the workload.",
                "Review updated rules against required ServiceAccount operations.")
    for binding in snapshot["roleBindings"]:
        if binding["roleRef"]["kind"] == "ClusterRole":
            add("RBAC-CLUSTERROLE-REF", f"RoleBinding/{binding['name']}", "LOW",
                "RoleBinding references a ClusterRole",
                f"Reference: {binding['roleRef']['name']}. ClusterRole contents are outside the namespace snapshot.",
                "Verify that permissions delegated within the namespace match the ServiceAccount's intended purpose.",
                "Review the granted permission set against cluster owner policy.", status="requires_review")


def package_findings(snapshot, add):
    for image in snapshot["images"]:
        for item in image["findings"]:
            fixed = item.get("fixed")
            reference = item.get("reference")
            advice = (f"Rebuild the image with the fixed package version: {fixed}." if fixed
                      else "Check the vendor advisory and availability of a patched base image.")
            source_name = image.get("evidence_source", "Trivy")
            evidence = (f"{source_name}: package {item['package']} {item['installed']} in {image['digest']}. "
                        "Version match identified via the CVE database. Reachability of vulnerable code was not measured.")
            add(item["id"], f"Image/{image['image']}", item["severity"],
                f"{item['id']} affects package {item['package']}", evidence, advice,
                "Match the rebuilt image digest against the running Pod and re-run package scanning.",
                status="version_match", cisa_kev=item["kev"] if snapshot["kev"]["status"] in ("ok", "stale") else None,
                source=reference, installed_version=item["installed"], fixed_version=fixed,
                image_digest=image["digest"], used_by=image["usedBy"], package_name=item["package"])


def create_report(snapshot, *, run=None, access=None, execution_steps=None):
    findings = {}
    if access is None:
        access = {
            "source": "Kubernetes snapshot and archived Trivy results",
            "identity": "kubectl identity during preparation; Job reads the mounted ConfigMap",
            "authorization": "Operator kubectl context; ServiceAccount token is disabled on the Job Pod",
            "scope": snapshot["namespace"],
        }

    def add(rule, resource, severity, issue, evidence, recommendation, verify, status="observed", **extra):
        key = f"{rule}|{resource}|{evidence}"
        identifier = hashlib.sha256(key.encode()).hexdigest()[:12]
        findings[identifier] = {
            "id": identifier, "rule": rule, "resource": resource, "severity": severity, "status": status,
            "issue": issue, "evidence": evidence, "recommendation": recommendation,
            "verification": verify, **extra,
        }
        if status == "version_match":
            read = (f"Matched package details for digest {extra['image_digest']}: "
                    f"{extra['package_name']} version {extra['installed_version']}.")
            compare = f"Package version matched against {rule} in the Trivy database."
        else:
            subject = resource.split("/", 1)[0]
            read = f"Selected entry {resource} from the {subject} snapshot."
            compare = f"Applied rule {rule} to the resource configuration and related snapshot objects."
        outcomes = {
            "observed": "Condition confirmed by configuration parameters.",
            "version_match": "Version matched a vulnerability advisory. Exploitability was not tested.",
            "requires_review": "Condition flagged for additional operator review.",
        }
        trail = [read, compare, evidence]
        if extra.get("cisa_kev"):
            version = snapshot["kev"].get("catalogVersion", "—")
            trail.append(f"{rule} found in CISA KEV catalog version {version}.")
        findings[identifier]["evidence_trace"] = [*trail, outcomes[status]]

    configuration_findings(snapshot, add)
    package_findings(snapshot, add)
    ranked = sorted(findings.values(), key=lambda entry: (
        not entry.get("cisa_kev"), -LEVELS.get(entry["severity"], 0), entry["resource"], entry["rule"],
    ))
    skipped = [f"{item['image']}: {item['reason']}" for item in snapshot["images"] if item["status"] != "ok"]
    database = snapshot.get("vulnerabilityDatabase")
    if database and database["status"] != "ok":
        skipped.append("Trivy vulnerability database is unavailable or stale.")
    if snapshot["kev"]["status"] not in ("ok", "not_applicable"):
        skipped.append("Current CISA KEV catalog version is unavailable.")
    if not snapshot["pods"]:
        skipped.append("No running application Pods were found in the snapshot.")
    completed = {
        "pods": len(snapshot["pods"]),
        "deployments": len(snapshot["deployments"]),
        "services": len(snapshot["services"]),
        "network_policies": len(snapshot["networkPolicies"]),
        "roles": len(snapshot["roles"]),
        "role_bindings": len(snapshot["roleBindings"]),
        "images_scanned": sum(item["status"] == "ok" for item in snapshot["images"]),
        "images_total": len(snapshot["images"]),
    }
    generated_at = datetime.now(timezone.utc).isoformat()
    passive = execution_steps is not None
    steps = list(execution_steps) if passive else [
        {"stage": "audit-inventory", "activity": "Loaded prepared resource snapshot from ConfigMap."},
        {"stage": "audit-evidence", "activity": "Loaded digest-pinned Trivy results and CISA KEV coverage metadata."},
    ]
    steps.extend([
        {"stage": "audit-agent", "at": generated_at,
         "activity": "Evaluated rules against Pod, Service, NetworkPolicy, and RBAC configurations, and processed package scan results."},
        {"stage": "audit-output", "at": generated_at,
         "activity": f"Generated report with {len(ranked)} findings. Each finding includes supporting evidence and a remediation verification step."},
    ])
    return {
        "run": run or os.environ.get("AUDIT_RUN", "local"),
        "mode": "passive" if passive else "one-off",
        "namespace": snapshot["namespace"],
        "captured_at": snapshot["capturedAt"],
        "generated_at": generated_at,
        "access_path": access,
        "execution_steps": steps,
        "status": "partial" if skipped else "completed",
        "coverage": completed,
        "expected_routes": [f"{source} → {target}:{port}/TCP" for source, target, port in EXPECTED_ROUTES],
        "image_scans": [{key: value for key, value in item.items() if key != "findings"} for item in snapshot["images"]],
        "known_exploited_catalog": snapshot["kev"],
        "vulnerability_database": database,
        "priority_findings": [
            {"id": entry["id"],
             "reason": ("Listed in CISA KEV; verify applicability to this environment and check for a fixed version."
                        if entry.get("cisa_kev") else
                        f"Severity {entry['severity']}; "
                        + ("check availability of a fixed package version." if entry["status"] == "version_match"
                           else "start by reviewing the flagged configuration setting."))}
            for entry in ranked[:5]
        ],
        "skipped": skipped,
        "limitations": [
            ("Trivy scans SBOMs by exact image digest. Report includes HIGH, CRITICAL, and CISA KEV matches."
             if passive else "Packages are checked against the Trivy database for HIGH and CRITICAL severities."),
            "Network flows are assessed statically from manifests. Reachability and host access were not probed with active traffic.",
            "Scope is limited to the snapshot of running workloads and resources in the observability namespace.",
        ],
        "counts": dict(Counter(entry["severity"] for entry in ranked)),
        "findings": ranked,
    }


def model_summary(report, ready_timeout=100, response_timeout=125):
    prompt = Path("/app/prompt.txt").read_text(encoding="utf8")
    all_findings = report["findings"]
    kev_findings = [entry for entry in all_findings if entry.get("cisa_kev")]
    pkg_findings = [entry for entry in all_findings if entry["status"] == "version_match"]
    cfg_findings = [entry for entry in all_findings if entry["status"] != "version_match"]

    snapshot = {key: report[key] for key in ("coverage", "counts", "expected_routes", "limitations", "skipped")}
    snapshot["totals"] = {
        "all": len(all_findings),
        "packages": len(pkg_findings),
        "config": len(cfg_findings),
        "cisa_kev": len(kev_findings),
    }
    snapshot["kev_highlights"] = [
        {
            "rule": entry["rule"],
            "resource": entry["resource"],
            "package": entry.get("package_name"),
            "installed": entry.get("installed_version"),
            "fixed": entry.get("fixed_version"),
        }
        for entry in kev_findings[:5]
    ]
    snapshot["config_rule_summary"] = dict(Counter(entry["rule"] for entry in cfg_findings))

    candidates = []
    seen_ids = set()

    def take(entry):
        if entry["id"] not in seen_ids:
            seen_ids.add(entry["id"])
            candidates.append(entry)

    for entry in kev_findings[:4]:
        take(entry)
    for entry in pkg_findings:
        if len(candidates) >= 8:
            break
        take(entry)
    seen_rules = set()
    for entry in cfg_findings:
        if len(candidates) >= 16:
            break
        if entry["rule"] not in seen_rules:
            seen_rules.add(entry["rule"])
            take(entry)
    for entry in all_findings:
        if len(candidates) >= 16:
            break
        take(entry)

    keys = {f"F{index}": entry["id"] for index, entry in enumerate(candidates, start=1)}
    snapshot["findings"] = [
        {"id": key, **{field: entry[field] for field in (
            "rule", "resource", "issue", "severity", "recommendation"
        )}, "cisa_kev": entry.get("cisa_kev")}
        for key, entry in zip(keys, candidates)
    ]
    priority_schema = {"type": "array", "maxItems": min(5, len(keys)),
                       "items": {"enum": list(keys)} if keys else {"type": "string"}}
    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string", "minLength": 90},
            "priority_ids": priority_schema,
        },
        "required": ["summary", "priority_ids"],
        "additionalProperties": False,
    }
    deadline = time.monotonic() + ready_timeout
    while True:
        try:
            with urllib.request.urlopen(f"{MODEL_URL}/health", timeout=2):
                break
        except OSError:
            if time.monotonic() >= deadline:
                raise TimeoutError("local model did not become ready") from None
            time.sleep(2)

    user_content = json.dumps(snapshot, ensure_ascii=False)
    attempts = (
        [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content},
        ],
        [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content + "\n\nWrite 2-3 complete sentences in English in the summary field: explicitly name the top priority risk (a CISA KEV CVE or critical finding and its resource), the key remediation step, and the limitation of static analysis."},
        ],
    )
    last_error = ValueError("invalid model report")
    for messages in attempts:
        payload = {
            "model": MODEL,
            "temperature": 0,
            "max_tokens": 420,
            "response_format": {"type": "json_schema", "schema": schema},
            "messages": messages,
        }
        request = urllib.request.Request(
            f"{MODEL_URL}/v1/chat/completions",
            json.dumps(payload).encode(),
            {"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=response_timeout) as response:
            data = json.load(response)
        try:
            result = json.loads(data["choices"][0]["message"]["content"])
            summary, priorities = result["summary"], result["priority_ids"]
            cleaned = " ".join(summary.split()) if isinstance(summary, str) else ""
            if (not 80 <= len(cleaned) <= 1600
                    or not isinstance(priorities, list) or len(priorities) > 5
                    or any(not isinstance(value, str) or value not in keys for value in priorities)):
                last_error = ValueError("invalid or overly brief model report")
                continue
            unique = dict.fromkeys(priorities)
            return {"status": "ok", "model": MODEL, "summary": cleaned,
                    "priority_ids": [keys[key] for key in unique]}
        except (ValueError, KeyError, TypeError) as error:
            last_error = error
    raise last_error


def main():
    snapshot = json.loads(Path("/input/evidence.json").read_text(encoding="utf8"))
    if snapshot.get("namespace") != "observability":
        raise ValueError("unexpected audit namespace")
    report = create_report(snapshot)
    try:
        report["model_review"] = model_summary(report)
    except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
        report["model_review"] = {"status": "unavailable", "model": MODEL, "reason": type(error).__name__}
    report["execution_steps"].append({
        "stage": "audit-model", "at": datetime.now(timezone.utc).isoformat(),
        "activity": ("Received summary from local model." if report["model_review"]["status"] == "ok"
                     else "Local model is unavailable. Rule-based audit results have been preserved in the report."),
    })
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
