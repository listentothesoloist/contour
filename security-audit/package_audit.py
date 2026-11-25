"""Match deployed image SBOMs to vendor advisories and the CISA KEV catalog."""

import gzip
import json
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

TRIVY = "/usr/local/bin/trivy"
CACHE = Path("/cache")
SBOMS = Path("/sboms")
KEV_URL = "https://raw.githubusercontent.com/cisagov/kev-data/develop/known_exploited_vulnerabilities.json"
FEED_INTERVAL = 6 * 3600
RETRY_INTERVAL = 300
MAX_CATALOG_BYTES = 4_000_000
MAX_SBOM_BYTES = 24_000_000


def now():
    return datetime.now(timezone.utc).isoformat()


def trivy(*args, timeout):
    return subprocess.run(
        [TRIVY, *args, "--cache-dir", str(CACHE), "--skip-version-check", "--quiet", "--timeout", f"{timeout}s"],
        capture_output=True, check=True, timeout=timeout + 5,
    ).stdout


def trivy_database():
    try:
        trivy("image", "--download-db-only", timeout=90)
    except (OSError, subprocess.SubprocessError) as error:
        print(f"Trivy database refresh: {type(error).__name__}", flush=True)
    try:
        metadata = json.loads((CACHE / "db/metadata.json").read_bytes())
        next_update = datetime.fromisoformat(metadata["NextUpdate"])
        return {
            "status": "ok" if datetime.now(timezone.utc) < next_update else "stale",
            "updated_at": metadata["UpdatedAt"],
            "next_update": metadata["NextUpdate"],
        }
    except (OSError, KeyError, ValueError):
        return {"status": "unavailable"}


def kev_catalog(previous, previous_ids):
    try:
        with urlopen(KEV_URL, timeout=15) as response:
            content = response.read(MAX_CATALOG_BYTES + 1)
        if len(content) > MAX_CATALOG_BYTES:
            raise ValueError("catalog too large")
        feed = json.loads(content)
        ids = {item["cveID"] for item in feed["vulnerabilities"]}
        if not ids or len(ids) != feed["count"]:
            raise ValueError("invalid CISA KEV catalog")
        return {"status": "ok", "source": KEV_URL, "retrievedAt": now(),
                "catalogVersion": feed["catalogVersion"], "entries": len(ids)}, ids
    except (OSError, KeyError, ValueError) as error:
        print(f"CISA KEV refresh: {type(error).__name__}", flush=True)
        return {**previous, "status": "stale" if previous_ids else "unavailable", "source": KEV_URL}, previous_ids


class PackageAudit:
    def __init__(self):
        self.refresh_after = 0
        self.database = {}
        self.kev = {}
        self.kev_ids = set()
        self.scans = {}

    def refresh_feeds(self):
        if time.monotonic() < self.refresh_after:
            return
        self.database = trivy_database()
        self.kev, self.kev_ids = kev_catalog(self.kev, self.kev_ids)
        current = all(feed["status"] == "ok" for feed in (self.database, self.kev))
        self.refresh_after = time.monotonic() + (FEED_INTERVAL if current else RETRY_INTERVAL)

    def scan_image(self, sbom):
        with gzip.open(sbom, "rb") as source, tempfile.NamedTemporaryFile(suffix=".cdx.json") as plain:
            payload = source.read(MAX_SBOM_BYTES + 1)
            if len(payload) > MAX_SBOM_BYTES:
                raise ValueError("SBOM too large")
            plain.write(payload)
            plain.flush()
            output = trivy(
                "sbom", "--scanners", "vuln", "--offline-scan", "--skip-db-update", "--skip-java-db-update",
                "--cache-backend", "memory", "--format", "json", plain.name, timeout=60,
            )
        results = json.loads(output)
        findings = []
        for group in results.get("Results") or []:
            for item in group.get("Vulnerabilities") or []:
                identifier = item["VulnerabilityID"]
                if item["Severity"] not in ("HIGH", "CRITICAL") and identifier not in self.kev_ids:
                    continue
                findings.append({
                    "id": identifier, "package": item["PkgName"], "installed": item["InstalledVersion"],
                    "fixed": item.get("FixedVersion"), "severity": item["Severity"],
                    "kev": identifier in self.kev_ids, "reference": item.get("PrimaryURL"),
                })
        return findings

    def enrich(self, snapshot):
        self.refresh_feeds()
        snapshot["kev"] = self.kev
        snapshot["vulnerabilityDatabase"] = self.database
        active = {}
        steps = [
            {"stage": "audit-evidence", "at": now(),
             "activity": f"Trivy database: {self.database.get('updated_at', 'unavailable')} · {self.database['status']}."},
            {"stage": "audit-evidence", "at": now(),
             "activity": f"CISA KEV catalog: {self.kev.get('catalogVersion', 'unavailable')} · {self.kev['status']}."},
        ]
        for image in snapshot["images"]:
            digest = image["digest"].rsplit("sha256:", 1)[-1]
            sbom = SBOMS / f"{digest}.cdx.gz"
            if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest) or not sbom.is_file():
                image["reason"] = "SBOM for the exact digest is missing."
            elif self.database["status"] == "unavailable":
                image["reason"] = "Trivy vulnerability database is unavailable."
            else:
                try:
                    key = (digest, sbom.stat().st_mtime_ns, self.database["updated_at"], self.kev.get("catalogVersion"))
                    findings = self.scans[key] if key in self.scans else self.scan_image(sbom)
                    active[key] = findings
                    image.update(status="ok", findings=findings, evidence_source="Trivy SBOM")
                    image.pop("reason", None)
                except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
                    print(f"Trivy SBOM {digest[:12]}: {type(error).__name__}", flush=True)
                    image["reason"] = "Trivy failed to process the SBOM for this digest."
            stage = f"Packages matched against Trivy database. Matches: {len(image['findings'])}."
            steps.append({"stage": "audit-evidence", "at": now(),
                          "activity": f"{image['image']} · {image['digest']} · {image.get('reason') or stage}"})
        self.scans = active
        return steps
