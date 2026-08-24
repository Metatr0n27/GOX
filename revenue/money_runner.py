#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATES = (
    "FOUND",
    "ELIGIBILITY_CHECK",
    "READY",
    "IN_PROGRESS",
    "OWNER_GATE",
    "SUBMITTED",
    "ACCEPTED",
    "COMPLETED",
    "PAID",
    "BLOCKED",
    "EXPIRED",
)

TERMINAL_STATES = {"PAID", "BLOCKED", "EXPIRED"}
OWNER_GATE_TYPES = {"LOGIN", "MFA", "CAPTCHA", "KYC", "PERSONAL_ANSWER", "RECORDING", "ATTESTATION", "FINAL_SUBMIT", "SPEND"}


@dataclass
class Evidence:
    at: str
    kind: str
    detail: str
    source: str | None = None


@dataclass
class Opportunity:
    id: str
    title: str
    platform: str
    url: str
    family_lane: str
    expected_pay: float
    expected_minutes: float
    qualification_probability: float = 0.5
    availability_probability: float = 0.7
    payout_delay_hours: float = 24.0
    status: str = "FOUND"
    owner_gate: dict[str, Any] | None = None
    evidence: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def score(self) -> float:
        hours = max(self.expected_minutes / 60.0, 0.10)
        gross_hourly = self.expected_pay / hours
        probability = max(0.0, min(1.0, self.qualification_probability)) * max(0.0, min(1.0, self.availability_probability))
        delay_penalty = 1.0 / (1.0 + max(0.0, self.payout_delay_hours) / 24.0)
        return gross_hourly * probability * (0.65 + 0.35 * delay_penalty)


class MoneyRunner:
    def __init__(self, root: Path, dry_run: bool = False):
        self.root = root
        self.state_dir = root / ".gox" / "money_runner"
        self.queue_file = self.state_dir / "opportunities.json"
        self.audit_file = self.state_dir / "audit.jsonl"
        self.owner_queue_file = self.state_dir / "owner_gates.json"
        self.dry_run = dry_run
        self.state_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def audit(self, event: str, opportunity_id: str | None, detail: dict[str, Any]) -> None:
        record = {"at": self.now(), "event": event, "opportunity_id": opportunity_id, "detail": detail}
        with self.audit_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")

    def load(self) -> list[Opportunity]:
        if not self.queue_file.exists():
            return []
        raw = json.loads(self.queue_file.read_text(encoding="utf-8"))
        return [Opportunity(**item) for item in raw]

    def save(self, items: list[Opportunity]) -> None:
        self.queue_file.write_text(json.dumps([asdict(x) for x in items], indent=2, sort_keys=True), encoding="utf-8")

    def add(self, item: Opportunity) -> None:
        items = self.load()
        if any(x.id == item.id for x in items):
            raise ValueError(f"duplicate opportunity id: {item.id}")
        if item.status not in STATES:
            raise ValueError(f"invalid status: {item.status}")
        items.append(item)
        self.save(items)
        self.audit("OPPORTUNITY_ADDED", item.id, {"title": item.title, "platform": item.platform})

    def ranked(self) -> list[Opportunity]:
        return sorted((x for x in self.load() if x.status not in TERMINAL_STATES), key=lambda x: x.score(), reverse=True)

    def transition(self, opportunity_id: str, new_state: str, *, evidence: Evidence | None = None) -> Opportunity:
        if new_state not in STATES:
            raise ValueError(f"invalid target state: {new_state}")
        items = self.load()
        found = next((x for x in items if x.id == opportunity_id), None)
        if found is None:
            raise KeyError(opportunity_id)
        proof_required = {"SUBMITTED", "ACCEPTED", "COMPLETED", "PAID"}
        if new_state in proof_required and evidence is None:
            raise ValueError(f"{new_state} requires evidence")
        if evidence is not None:
            found.evidence.append(asdict(evidence))
        old = found.status
        found.status = new_state
        self.save(items)
        self.audit("STATE_CHANGED", found.id, {"from": old, "to": new_state, "evidence": asdict(evidence) if evidence else None})
        return found

    def require_owner(self, opportunity_id: str, gate_type: str, exact_action: str, reason: str, resume_state: str = "IN_PROGRESS") -> Opportunity:
        if gate_type not in OWNER_GATE_TYPES:
            raise ValueError(f"unsupported owner gate: {gate_type}")
        if resume_state not in STATES:
            raise ValueError("invalid resume state")
        items = self.load()
        found = next((x for x in items if x.id == opportunity_id), None)
        if found is None:
            raise KeyError(opportunity_id)
        found.owner_gate = {
            "type": gate_type,
            "exact_action": exact_action,
            "reason": reason,
            "resume_state": resume_state,
            "created_at": self.now(),
            "resolved": False,
        }
        found.status = "OWNER_GATE"
        self.save(items)
        self._refresh_owner_queue(items)
        self.audit("OWNER_GATE_CREATED", found.id, found.owner_gate)
        return found

    def resolve_owner(self, opportunity_id: str, evidence_detail: str) -> Opportunity:
        items = self.load()
        found = next((x for x in items if x.id == opportunity_id), None)
        if found is None or not found.owner_gate:
            raise KeyError(f"no owner gate for {opportunity_id}")
        found.owner_gate["resolved"] = True
        found.owner_gate["resolved_at"] = self.now()
        found.owner_gate["evidence"] = evidence_detail
        found.status = found.owner_gate.get("resume_state", "IN_PROGRESS")
        self.save(items)
        self._refresh_owner_queue(items)
        self.audit("OWNER_GATE_RESOLVED", found.id, {"evidence": evidence_detail, "resume_state": found.status})
        return found

    def _refresh_owner_queue(self, items: list[Opportunity]) -> None:
        gates = [
            {"opportunity_id": x.id, "title": x.title, "platform": x.platform, **x.owner_gate}
            for x in items
            if x.owner_gate and not x.owner_gate.get("resolved")
        ]
        self.owner_queue_file.write_text(json.dumps(gates, indent=2, sort_keys=True), encoding="utf-8")

    def spend_preflight(self, opportunity_id: str, amount: float | None, max_amount: float | None, purpose: str, recipient: str, recurring: bool) -> None:
        ceiling = max_amount if max_amount is not None else amount
        if ceiling is None:
            raise ValueError("unknown spend requires a maximum possible charge")
        self.require_owner(
            opportunity_id,
            "SPEND",
            f"Authorize up to ${ceiling:.2f} for {purpose} to {recipient} ({'recurring' if recurring else 'one-time'}).",
            "Spending is never auto-approved. User notification and explicit authorization are required before commitment.",
            resume_state="IN_PROGRESS",
        )

    def open_browser(self, item: Opportunity, headless: bool = False) -> int:
        script = self.root / "browser_stack" / "auth_browser.py"
        if not script.exists():
            raise FileNotFoundError(script)
        cmd = [sys.executable, str(script), "--service", item.platform.lower().replace(" ", "-"), "--url", item.url]
        if headless:
            cmd.append("--headless")
        self.audit("BROWSER_OPEN_REQUESTED", item.id, {"cmd": cmd, "dry_run": self.dry_run})
        if self.dry_run:
            print("DRY RUN:", " ".join(cmd))
            return 0
        return subprocess.call(cmd, cwd=self.root)

    def status(self) -> dict[str, Any]:
        items = self.load()
        active = [x for x in items if x.status not in TERMINAL_STATES]
        paid = [x for x in items if x.status == "PAID"]
        return {
            "generated_at": self.now(),
            "truth_status": "BUILT-BUT-UNVERIFIED" if active else "NO_ACTIVE_QUEUE",
            "active_count": len(active),
            "owner_gate_count": sum(1 for x in active if x.status == "OWNER_GATE"),
            "verified_paid_total": round(sum(x.expected_pay for x in paid), 2),
            "ranked": [
                {"id": x.id, "title": x.title, "platform": x.platform, "status": x.status, "score": round(x.score(), 2)}
                for x in sorted(active, key=lambda v: v.score(), reverse=True)
            ],
        }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="GOX Money Runner: evidence-first revenue task state machine")
    p.add_argument("--root", default=".")
    p.add_argument("--dry-run", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status")
    rank = sub.add_parser("rank")

    add = sub.add_parser("add")
    add.add_argument("--id", required=True)
    add.add_argument("--title", required=True)
    add.add_argument("--platform", required=True)
    add.add_argument("--url", required=True)
    add.add_argument("--family-lane", required=True)
    add.add_argument("--pay", type=float, required=True)
    add.add_argument("--minutes", type=float, required=True)
    add.add_argument("--qualification", type=float, default=0.5)
    add.add_argument("--availability", type=float, default=0.7)
    add.add_argument("--payout-delay-hours", type=float, default=24.0)

    trans = sub.add_parser("transition")
    trans.add_argument("id")
    trans.add_argument("state", choices=STATES)
    trans.add_argument("--evidence-kind")
    trans.add_argument("--evidence-detail")
    trans.add_argument("--evidence-source")

    gate = sub.add_parser("owner-gate")
    gate.add_argument("id")
    gate.add_argument("type", choices=sorted(OWNER_GATE_TYPES))
    gate.add_argument("exact_action")
    gate.add_argument("reason")
    gate.add_argument("--resume-state", default="IN_PROGRESS", choices=STATES)

    resolve = sub.add_parser("resolve-owner")
    resolve.add_argument("id")
    resolve.add_argument("evidence_detail")

    browse = sub.add_parser("open-browser")
    browse.add_argument("id")
    browse.add_argument("--headless", action="store_true")

    spend = sub.add_parser("spend-preflight")
    spend.add_argument("id")
    spend.add_argument("--amount", type=float)
    spend.add_argument("--max-amount", type=float)
    spend.add_argument("--purpose", required=True)
    spend.add_argument("--recipient", required=True)
    spend.add_argument("--recurring", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    runner = MoneyRunner(Path(args.root).resolve(), dry_run=args.dry_run)

    if args.cmd == "status":
        print(json.dumps(runner.status(), indent=2))
    elif args.cmd == "rank":
        print(json.dumps([{**asdict(x), "score": round(x.score(), 2)} for x in runner.ranked()], indent=2))
    elif args.cmd == "add":
        runner.add(Opportunity(
            id=args.id, title=args.title, platform=args.platform, url=args.url, family_lane=args.family_lane,
            expected_pay=args.pay, expected_minutes=args.minutes, qualification_probability=args.qualification,
            availability_probability=args.availability, payout_delay_hours=args.payout_delay_hours,
        ))
    elif args.cmd == "transition":
        evidence = None
        if args.evidence_detail:
            evidence = Evidence(runner.now(), args.evidence_kind or "USER_OR_SYSTEM_PROOF", args.evidence_detail, args.evidence_source)
        runner.transition(args.id, args.state, evidence=evidence)
    elif args.cmd == "owner-gate":
        runner.require_owner(args.id, args.type, args.exact_action, args.reason, args.resume_state)
    elif args.cmd == "resolve-owner":
        runner.resolve_owner(args.id, args.evidence_detail)
    elif args.cmd == "open-browser":
        item = next((x for x in runner.load() if x.id == args.id), None)
        if item is None:
            raise KeyError(args.id)
        return runner.open_browser(item, headless=args.headless)
    elif args.cmd == "spend-preflight":
        runner.spend_preflight(args.id, args.amount, args.max_amount, args.purpose, args.recipient, args.recurring)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
