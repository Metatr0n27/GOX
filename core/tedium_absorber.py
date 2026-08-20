#!/usr/bin/env python3
"""GOX tedium absorber.

Routes routine work to automation and surfaces only genuine owner/family gates.
This module is intentionally conservative around identity, legal, tax, payment,
security, CAPTCHA/MFA, signatures, and platform-required human actions.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DB_PATH = Path("/var/lib/gox/state/gox.db")

OWNER_GATES = {
    "login", "mfa", "captcha", "identity_verification", "signature",
    "tax_attestation", "payment_details", "oauth_consent", "final_submit",
    "platform_human_only_action",
}

@dataclass
class WorkItem:
    id: str
    lane: str
    kind: str
    objective: str
    status: str = "queued"
    owner_gate: bool = False
    gate_reason: str = ""
    idempotency_key: str = ""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS lanes(
          lane TEXT PRIMARY KEY,
          display_name TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS work_items(
          id TEXT PRIMARY KEY,
          lane TEXT NOT NULL REFERENCES lanes(lane),
          kind TEXT NOT NULL,
          objective TEXT NOT NULL,
          status TEXT NOT NULL,
          owner_gate INTEGER NOT NULL DEFAULT 0,
          gate_reason TEXT NOT NULL DEFAULT '',
          idempotency_key TEXT UNIQUE,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS revenue(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          lane TEXT NOT NULL REFERENCES lanes(lane),
          source TEXT NOT NULL,
          task_id TEXT NOT NULL,
          gross_cents INTEGER NOT NULL DEFAULT 0,
          fee_cents INTEGER NOT NULL DEFAULT 0,
          net_cents INTEGER NOT NULL DEFAULT 0,
          expected_cents INTEGER NOT NULL DEFAULT 0,
          probability REAL NOT NULL DEFAULT 0,
          payout_status TEXT NOT NULL DEFAULT 'unverified',
          owner_minutes REAL NOT NULL DEFAULT 0,
          evidence TEXT NOT NULL DEFAULT '',
          created_at TEXT NOT NULL,
          UNIQUE(lane, source, task_id)
        );
        CREATE TABLE IF NOT EXISTS events(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ts TEXT NOT NULL,
          lane TEXT NOT NULL,
          event TEXT NOT NULL,
          payload TEXT NOT NULL
        );
        """
    )
    db.commit()
    return db


def register_lane(db: sqlite3.Connection, lane: str, display_name: str) -> None:
    db.execute(
        "INSERT OR IGNORE INTO lanes(lane,display_name,created_at) VALUES(?,?,?)",
        (lane, display_name, now()),
    )
    db.commit()


def classify(kind: str) -> tuple[bool, str]:
    if kind in OWNER_GATES:
        return True, kind
    return False, ""


def enqueue(db: sqlite3.Connection, item: WorkItem) -> dict:
    gate, reason = classify(item.kind)
    item.owner_gate = item.owner_gate or gate
    if not item.gate_reason:
        item.gate_reason = reason
    if not item.idempotency_key:
        item.idempotency_key = f"{item.lane}:{item.id}"
    ts = now()
    db.execute(
        """INSERT OR IGNORE INTO work_items
        (id,lane,kind,objective,status,owner_gate,gate_reason,idempotency_key,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (item.id,item.lane,item.kind,item.objective,item.status,int(item.owner_gate),
         item.gate_reason,item.idempotency_key,ts,ts),
    )
    db.execute(
        "INSERT INTO events(ts,lane,event,payload) VALUES(?,?,?,?)",
        (ts,item.lane,"work_enqueued",json.dumps(asdict(item),sort_keys=True)),
    )
    db.commit()
    return asdict(item)


def next_actions(db: sqlite3.Connection, lane: str | None = None) -> list[dict]:
    sql = "SELECT id,lane,kind,objective,status,owner_gate,gate_reason,idempotency_key FROM work_items WHERE status IN ('queued','blocked')"
    args: list[str] = []
    if lane:
        sql += " AND lane=?"
        args.append(lane)
    sql += " ORDER BY owner_gate ASC, created_at ASC"
    rows = db.execute(sql,args).fetchall()
    keys = ["id","lane","kind","objective","status","owner_gate","gate_reason","idempotency_key"]
    return [dict(zip(keys,r)) for r in rows]


def money_summary(db: sqlite3.Connection) -> dict:
    row = db.execute(
        "SELECT COALESCE(SUM(net_cents),0), COALESCE(SUM(expected_cents*probability),0) FROM revenue"
    ).fetchone()
    return {"verified_net_dollars": row[0]/100, "weighted_expected_dollars": row[1]/100}


def record_revenue(db: sqlite3.Connection, *, lane: str, source: str, task_id: str,
                   gross_cents: int = 0, fee_cents: int = 0, expected_cents: int = 0,
                   probability: float = 0.0, payout_status: str = "unverified",
                   owner_minutes: float = 0.0, evidence: str = "") -> None:
    net = gross_cents - fee_cents if payout_status == "verified" else 0
    db.execute(
        """INSERT INTO revenue(lane,source,task_id,gross_cents,fee_cents,net_cents,expected_cents,
        probability,payout_status,owner_minutes,evidence,created_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(lane,source,task_id) DO UPDATE SET
          gross_cents=excluded.gross_cents, fee_cents=excluded.fee_cents,
          net_cents=excluded.net_cents, expected_cents=excluded.expected_cents,
          probability=excluded.probability, payout_status=excluded.payout_status,
          owner_minutes=excluded.owner_minutes, evidence=excluded.evidence""",
        (lane,source,task_id,gross_cents,fee_cents,net,expected_cents,probability,
         payout_status,owner_minutes,evidence,now()),
    )
    db.commit()


def bootstrap_lanes(db: sqlite3.Connection, lanes: Iterable[tuple[str,str]]) -> None:
    for lane,name in lanes:
        register_lane(db,lane,name)


if __name__ == "__main__":
    db = connect()
    print(json.dumps({"status":"ok","money":money_summary(db),"next":next_actions(db)}, indent=2))
