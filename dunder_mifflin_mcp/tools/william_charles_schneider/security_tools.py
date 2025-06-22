"""
This module contains dummy security tools for the William Charles Schneider agent.
"""

from datetime import datetime, timezone
from dunder_mifflin_mcp.config import settings


def run_pen_test() -> dict:
    """
    Simulates a penetration test against the frontend (no login) and returns a JSON report.
    """
    report = {
        "tool": "run_pen_test",
        "target": settings.common.frontend_url,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "summary": {
            "total_tests": 3,
            "critical_findings": 0,
            "high_findings": 1,
            "medium_findings": 1,
            "low_findings": 1,
        },
        "findings": [
            {
                "id": "PT-001",
                "title": "Memory corruption in MP4 module",
                "severity": "HIGH",
                "cve": "CVE-2022-41741",
                "description": (
                    "The ngx_http_mp4_module in nginx 1.21.0-1.23.1 allows memory corruption "
                    "when processing crafted MP4 fragments."
                ),
                "reference": "https://nginx.org/en/security_advisories.html",
            },  # CVE-2022-41741 :contentReference[oaicite:4]{index=4}
            {
                "id": "PT-002",
                "title": "BusyBox credentials exposure",
                "severity": "MEDIUM",
                "cve": "CVE-2021-42375",
                "description": (
                    "The BusyBox `ssl_client` in nginx:1.21.0-alpine leaks credentials "
                    "due to insufficient protection of secrets in memory."
                ),
                "reference": "https://bugs.busybox.net/show_bug.cgi?id=14781",
            },  # CVE-2021-42375 :contentReference[oaicite:5]{index=5}
        ],
    }
    return report


def run_vulnerability_scan() -> dict:
    """
    Simulates a vulnerability scan against the Python backend and returns a JSON report.
    """
    report = {
        "tool": "run_vulnerability_scan",
        "service": "backend",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "vulnerabilities": [
            {
                "id": "VS-1001",
                "package": "multiprocessing (forkserver)",
                "installed_version": "3.9.0",
                "severity": "HIGH",
                "cve": "CVE-2022-42919",
                "description": (
                    "Local privilege escalation in Python multiprocessing forkserver "
                    "when deserializing untrusted pickles."
                ),
                "reference": "https://nvd.nist.gov/vuln/detail/CVE-2022-42919",
            },  # CVE-2022-42919 :contentReference[oaicite:6]{index=6}
            {
                "id": "VS-1002",
                "package": "_ctypes",
                "installed_version": "3.9.0",
                "severity": "CRITICAL",
                "cve": "CVE-2021-3177",
                "description": (
                    "Buffer overflow in `PyCArg_repr` in `_ctypes/callproc.c`, "
                    "leading to potential code execution."
                ),
                "reference": "https://www.twingate.com/blog/tips/cve-2021-3177",
            },  # CVE-2021-3177 :contentReference[oaicite:7]{index=7}
        ],
        "summary": {
            "total_vulnerabilities": 2,
            "by_severity": {"CRITICAL": 1, "HIGH": 1, "MEDIUM": 0, "LOW": 0},
        },
    }
    return report
