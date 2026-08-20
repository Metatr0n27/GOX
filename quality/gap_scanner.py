#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "quality" / "stack_manifest.json"

LIVE_REQUIRED = {
    "owner_voice",
    "approval_bridge",
    "steward_return",
    "runtime",
    "chatdev",
    "easy_jobs",
    "restart_recovery",
    "secrets",
    "first_dollar",
}


def check_path(rel: str) -> dict:
    p = ROOT / rel
    exists = p.exists()
    detail = "missing"
    if exists:
        if p.is_dir():
            try:
                count = sum(1 for _ in p.iterdir())
            except Exception:
                count = -1
            detail = f"directory:{count} entries"
        else:
            detail = f"file:{p.stat().st_size} bytes"
    return {"path": rel, "exists": exists, "detail": detail}


def automatic_steward_result_exists() -> tuple[bool, str]:
    results = ROOT / "remote_steward" / "results"
    if not results.exists():
        return False, "results directory missing"
    found = 0
    for path in results.glob("*.json"):
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        # Manual proof files do not count. Automatic steward output always has action/runs.
        if data.get("action") and isinstance(data.get("runs"), list):
            found += 1
    return found > 0, f"automatic_results:{found}"


def first_dollar_proof_exists() -> tuple[bool, str]:
    proof = ROOT / "revenue" / "first_dollar_verified.json"
    if not proof.exists():
        return False, "verified first-dollar proof missing"
    try:
        data = json.loads(proof.read_text())
    except Exception:
        return False, "verified first-dollar proof invalid JSON"
    net = data.get("net_verified")
    source = data.get("evidence")
    ok = isinstance(net, (int, float)) and net > 0 and bool(source)
    return ok, "verified revenue evidence present" if ok else "revenue proof incomplete"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    report = {"release_rule": manifest["release_rule"], "checks": [], "summary": {}}

    for item in manifest["critical"]:
        evidence = [check_path(x) for x in item.get("evidence", [])]
        present = bool(evidence) and all(x["exists"] for x in evidence)
        status = "PRESENT" if present else "BLOCKED"
        detail = ""

        if present and item["id"] in LIVE_REQUIRED:
            status = "PRESENT_UNVERIFIED"

        if item["id"] == "steward_return":
            ok, detail = automatic_steward_result_exists()
            status = "PASS" if ok else ("PRESENT_UNVERIFIED" if present else "BLOCKED")

        if item["id"] == "first_dollar":
            ok, detail = first_dollar_proof_exists()
            status = "PASS" if ok else ("PRESENT_UNVERIFIED" if present else "BLOCKED")

        report["checks"].append({
            "id": item["id"],
            "label": item["label"],
            "status": status,
            "detail": detail,
            "evidence": evidence,
        })

    counts = {}
    for row in report["checks"]:
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    report["summary"] = {
        **counts,
        "critical_total": len(report["checks"]),
        "complete": all(x["status"] == "PASS" for x in report["checks"]),
        "note": "PRESENT is not PASS. Live proof is required before completion.",
    }
    print(json.dumps(report, indent=2))
    return 0 if report["summary"]["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
