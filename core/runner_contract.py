#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


RUNNER_STATES = {
    'queued', 'leased', 'running', 'owner_gate', 'waiting_external',
    'qa', 'submitted', 'revision', 'settlement', 'complete', 'failed',
    'suppressed', 'cancelled',
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class WorkContract:
    id: str
    objective: str
    lane: str = 'revenue'
    opportunity_id: str = ''
    runner_role: str = 'worker'
    status: str = 'queued'
    allowed_tools: list[str] = field(default_factory=list)
    allowed_side_effects: list[str] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    evidence_required: list[str] = field(default_factory=list)
    confidentiality_class: str = 'internal'
    owner_minute_budget: float = 0.0
    compute_budget_cents: int = 0
    expected_net_cents: int = 0
    expected_owner_hour: float = 0.0
    retry_limit: int = 2
    idempotency_key: str = ''
    lease_owner: str = ''
    lease_until: str = ''
    failure_class: str = ''
    result: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.id:
            raise ValueError('contract id required')
        if not self.objective:
            raise ValueError('objective required')
        if self.status not in RUNNER_STATES:
            raise ValueError(f'invalid status: {self.status}')
        if not self.idempotency_key:
            self.idempotency_key = f'{self.lane}:{self.id}'


def ensure_runner_schema(db: sqlite3.Connection) -> None:
    db.executescript(
        '''
        CREATE TABLE IF NOT EXISTS runner_contracts(
          id TEXT PRIMARY KEY,
          opportunity_id TEXT NOT NULL DEFAULT '',
          lane TEXT NOT NULL,
          runner_role TEXT NOT NULL,
          objective TEXT NOT NULL,
          status TEXT NOT NULL,
          contract_json TEXT NOT NULL,
          idempotency_key TEXT NOT NULL UNIQUE,
          lease_owner TEXT NOT NULL DEFAULT '',
          lease_until TEXT NOT NULL DEFAULT '',
          attempts INTEGER NOT NULL DEFAULT 0,
          last_error TEXT NOT NULL DEFAULT '',
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS runner_events(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ts TEXT NOT NULL,
          contract_id TEXT NOT NULL,
          event TEXT NOT NULL,
          payload TEXT NOT NULL
        );
        '''
    )
    db.commit()


def upsert_contract(db: sqlite3.Connection, contract: WorkContract) -> None:
    contract.validate()
    ts = now()
    payload = json.dumps(asdict(contract), sort_keys=True)
    db.execute(
        '''INSERT INTO runner_contracts(
           id,opportunity_id,lane,runner_role,objective,status,contract_json,
           idempotency_key,lease_owner,lease_until,attempts,last_error,created_at,updated_at)
           VALUES(?,?,?,?,?,?,?,?,?,?,0,'',?,?)
           ON CONFLICT(id) DO UPDATE SET
             opportunity_id=excluded.opportunity_id,lane=excluded.lane,
             runner_role=excluded.runner_role,objective=excluded.objective,
             status=excluded.status,contract_json=excluded.contract_json,
             idempotency_key=excluded.idempotency_key,
             lease_owner=excluded.lease_owner,lease_until=excluded.lease_until,
             updated_at=excluded.updated_at''',
        (contract.id, contract.opportunity_id, contract.lane, contract.runner_role,
         contract.objective, contract.status, payload, contract.idempotency_key,
         contract.lease_owner, contract.lease_until, ts, ts),
    )
    db.execute(
        'INSERT INTO runner_events(ts,contract_id,event,payload) VALUES(?,?,?,?)',
        (ts, contract.id, 'contract_upserted', payload),
    )
    db.commit()


def list_active(db: sqlite3.Connection) -> list[dict[str, Any]]:
    db.row_factory = sqlite3.Row
    rows = db.execute(
        '''SELECT * FROM runner_contracts
           WHERE status NOT IN ('complete','suppressed','cancelled')
           ORDER BY updated_at ASC'''
    ).fetchall()
    return [dict(r) for r in rows]
