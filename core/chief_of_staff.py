#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_DB = Path("/var/lib/gox/state/gox.db")
APPROVAL_ROOT = Path("/var/lib/gox-approval")

OWNER_GATE_KINDS = {
    "login",
    "mfa",
    "captcha",
    "identity_verification",
    "signature",
    "tax_attestation",
    "payment_details",
    "oauth_consent",
    "final_submit",
    "platform_human_only_action",
}


@dataclass
class Decision:
    priority: int
    action: str
    reason: str
    owner_gate: bool = False


def run_gap_scan() -> dict:
    p = subprocess.run(
        ["python3", str(ROOT / "quality" / "gap_scanner.py")],
        text=True,
        capture_output=True,
    )
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"summary": {"scan_error": True}, "checks": [], "error": p.stderr[-2000:]}


def pending_approvals() -> list[dict]:
    pending = APPROVAL_ROOT / "pending"
    if not pending.exists():
        return []
    out = []
    for path in sorted(pending.glob("*.json")):
        try:
            out.append(json.loads(path.read_text()))
        except Exception:
            continue
    return out


def state_snapshot() -> dict:
    if not STATE_DB.exists():
        return {"db_present": False}
    conn = sqlite3.connect(str(STATE_DB))
    conn.row_factory = sqlite3.Row
    result = {"db_present": True}
    try:
        for table in ("lanes", "work_items", "revenue", "events"):
            try:
                result[table] = conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
            except sqlite3.Error:
                result[table] = None
        try:
            row = conn.execute(
                "SELECT COALESCE(SUM(net),0) AS total FROM revenue WHERE payout_status='verified'"
            ).fetchone()
            result["verified_net"] = float(row["total"] or 0)
        except sqlite3.Error:
            result["verified_net"] = 0.0
    finally:
        conn.close()
    return result


def choose_next() -> list[Decision]:
    gaps = run_gap_scan()
    approvals = pending_approvals()
    state = state_snapshot()
    decisions: list[Decision] = []

    if approvals:
        decisions.append(Decision(
            100,
            "surface_owner_approval_queue",
            f"{len(approvals)} owner approval(s) are waiting",
            owner_gate=True,
        ))

    by_id = {c.get("id"): c for c in gaps.get("checks", [])}
    steward = by_id.get("steward_return", {})
    if steward.get("status") != "PASS":
        decisions.append(Decision(
            95,
            "repair_and_prove_steward_return",
            "automatic command/result round trip is not yet proven",
        ))

    for cid, action, label in (
        ("approval_bridge", "prove_approval_bridge", "approval bridge"),
        ("restart_recovery", "prove_restart_recovery", "restart recovery"),
        ("secrets", "run_secret_guard", "secret controls"),
        ("runtime", "prove_runtime", "agent runtime"),
        ("family_lanes", "prove_family_lane_isolation", "family identity lanes"),
    ):
        check = by_id.get(cid, {})
        if check and check.get("status") != "PASS":
            decisions.append(Decision(80, action, f"{label} lacks live PASS evidence"))

    if state.get("verified_net", 0) <= 0:
        decisions.append(Decision(
            70,
            "run_first_dollar_pipeline",
            "verified net revenue is still zero",
        ))

    decisions.sort(key=lambda x: (-x.priority, x.action))
    return decisions


def main() -> int:
    snapshot = {
        "role": "GOX Chief of Staff",
        "operating_rule": "CEO sets strategy and handles only genuine owner gates; GOX executes and proves everything else.",
        "owner_gate_kinds": sorted(OWNER_GATE_KINDS),
        "pending_approvals": pending_approvals(),
        "state": state_snapshot(),
        "gaps": run_gap_scan(),
        "next_actions": [d.__dict__ for d in choose_next()],
    }
    print(json.dumps(snapshot, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
