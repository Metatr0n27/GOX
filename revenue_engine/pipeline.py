#!/usr/bin/env python3
"""Scout -> qualify -> rank -> proposal-ready queue."""
from __future__ import annotations
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from capabilities import verified_capabilities
from demand_to_cash import draft_proposal, qualify
from scout_public import scout

STATE_DIR = Path(os.environ.get("GOX_REVENUE_STATE", "/var/lib/gox/revenue"))
QUEUE = STATE_DIR / "opportunities.json"


def _atomic_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f, indent=2, sort_keys=True)
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def build_queue() -> dict:
    now = datetime.now(timezone.utc).isoformat()
    rows = []
    for opportunity in scout():
        q = qualify(opportunity, verified_capabilities())
        if not q.accepted:
            continue
        proposal = draft_proposal(opportunity, q)
        rows.append({
            "id": f"{opportunity.source}:{opportunity.external_id}",
            "state": "PROPOSAL_READY",
            "source": opportunity.source,
            "source_url": opportunity.source_url,
            "title": opportunity.title,
            "budget_min": opportunity.budget_min,
            "budget_max": opportunity.budget_max,
            "currency": opportunity.currency,
            "score": q.score,
            "capability": q.capability,
            "proposal": proposal,
            "scouted_at": now,
        })
    rows.sort(key=lambda x: (x["score"], x["budget_max"]), reverse=True)
    payload = {"generated_at": now, "count": len(rows), "items": rows[:50]}
    _atomic_write(QUEUE, payload)
    return payload


def read_queue() -> dict:
    try:
        return json.loads(QUEUE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"generated_at": None, "count": 0, "items": []}


if __name__ == "__main__":
    print(json.dumps(build_queue(), indent=2))
