#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from core.tedium_absorber import connect, enqueue, WorkItem, register_lane, money_summary

ROOT = Path(__file__).resolve().parents[1]
ENGINE_ROOT = Path('/var/lib/gox/revenue')
INBOX = ENGINE_ROOT / 'inbox'
ARCHIVE = ENGINE_ROOT / 'archive'
REPORT = ENGINE_ROOT / 'latest_report.json'

ALLOWED_VERDICTS = {'ALLOWED', 'ALLOWED_WITH_CONDITIONS'}
OWNER_GATE_KINDS = {
    'login', 'mfa', 'captcha', 'identity_verification', 'signature',
    'tax_attestation', 'payment_details', 'oauth_consent', 'final_submit',
    'platform_human_only_action',
}

@dataclass
class Opportunity:
    id: str
    source: str
    title: str
    lane: str = 'revenue'
    expected_cents: int = 0
    payout_probability: float = 0.0
    owner_minutes: float = 0.0
    gox_share: float = 0.0
    time_to_cash_hours: float = 9999.0
    repeatability: float = 0.0
    payout_certainty: float = 0.0
    rules_verdict: str = 'UNCLEAR'
    blocker: str = ''
    owner_gate_kind: str = ''
    executable_now: bool = False
    next_action: str = ''
    evidence: str = ''
    funding_status: str = 'unknown'
    verification_status: str = 'unverified'
    settlement_status: str = 'unsettled'
    payment_evidence: str = ''


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def predicted_owner_hour(op: Opportunity) -> float:
    owner_hours = max(0.0833, op.owner_minutes / 60.0)
    return round((max(0, op.expected_cents) / 100.0) * clamp01(op.payout_probability) / owner_hours, 4)


def score(op: Opportunity) -> float:
    if op.rules_verdict not in ALLOWED_VERDICTS:
        return -1e9
    if op.blocker:
        return -1e9
    if op.owner_gate_kind and op.owner_gate_kind not in OWNER_GATE_KINDS:
        return -1e9

    owner_hour_value = predicted_owner_hour(op)
    gox_bonus = 40.0 * clamp01(op.gox_share)
    repeat_bonus = 20.0 * clamp01(op.repeatability)
    certainty_bonus = 20.0 * clamp01(op.payout_certainty)
    speed_bonus = 30.0 if op.executable_now else max(0.0, 20.0 - min(op.time_to_cash_hours, 200.0) / 10.0)
    funding_bonus = 20.0 if op.funding_status == 'funded' else 0.0
    gate_penalty = 15.0 if op.owner_gate_kind else 0.0
    return round(owner_hour_value + gox_bonus + repeat_bonus + certainty_bonus + speed_bonus + funding_bonus - gate_penalty, 4)


def _columns(db: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in db.execute(f'PRAGMA table_info({table})').fetchall()}


def _ensure_column(db: sqlite3.Connection, table: str, definition: str) -> None:
    name = definition.split()[0]
    if name not in _columns(db, table):
        db.execute(f'ALTER TABLE {table} ADD COLUMN {definition}')


def ensure_schema(db: sqlite3.Connection) -> None:
    db.executescript(
        '''
        CREATE TABLE IF NOT EXISTS opportunities(
          id TEXT PRIMARY KEY,
          source TEXT NOT NULL,
          title TEXT NOT NULL,
          lane TEXT NOT NULL,
          expected_cents INTEGER NOT NULL DEFAULT 0,
          payout_probability REAL NOT NULL DEFAULT 0,
          owner_minutes REAL NOT NULL DEFAULT 0,
          gox_share REAL NOT NULL DEFAULT 0,
          time_to_cash_hours REAL NOT NULL DEFAULT 9999,
          repeatability REAL NOT NULL DEFAULT 0,
          payout_certainty REAL NOT NULL DEFAULT 0,
          rules_verdict TEXT NOT NULL DEFAULT 'UNCLEAR',
          blocker TEXT NOT NULL DEFAULT '',
          owner_gate_kind TEXT NOT NULL DEFAULT '',
          executable_now INTEGER NOT NULL DEFAULT 0,
          next_action TEXT NOT NULL DEFAULT '',
          evidence TEXT NOT NULL DEFAULT '',
          score REAL NOT NULL DEFAULT 0,
          status TEXT NOT NULL DEFAULT 'candidate',
          updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS engine_runs(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ts TEXT NOT NULL,
          ingested INTEGER NOT NULL DEFAULT 0,
          qualified INTEGER NOT NULL DEFAULT 0,
          selected_id TEXT NOT NULL DEFAULT '',
          report TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS economics_outcomes(
          opportunity_id TEXT PRIMARY KEY,
          predicted_owner_hour REAL NOT NULL DEFAULT 0,
          actual_net_cents INTEGER NOT NULL DEFAULT 0,
          actual_owner_minutes REAL NOT NULL DEFAULT 0,
          actual_owner_hour REAL NOT NULL DEFAULT 0,
          settlement_status TEXT NOT NULL DEFAULT 'unsettled',
          payment_evidence TEXT NOT NULL DEFAULT '',
          updated_at TEXT NOT NULL
        );
        '''
    )
    for definition in (
        "funding_status TEXT NOT NULL DEFAULT 'unknown'",
        "verification_status TEXT NOT NULL DEFAULT 'unverified'",
        "settlement_status TEXT NOT NULL DEFAULT 'unsettled'",
        "payment_evidence TEXT NOT NULL DEFAULT ''",
        "predicted_owner_hour REAL NOT NULL DEFAULT 0",
    ):
        _ensure_column(db, 'opportunities', definition)
    db.commit()


def parse_opportunity(data: dict) -> Opportunity:
    raw_time_to_cash = data.get('time_to_cash_hours', 9999)
    time_to_cash_hours = 9999.0 if raw_time_to_cash is None else float(raw_time_to_cash)
    return Opportunity(
        id=str(data['id']),
        source=str(data.get('source', 'unknown')),
        title=str(data.get('title', data['id'])),
        lane=str(data.get('lane', 'revenue')),
        expected_cents=int(data.get('expected_cents', 0) or 0),
        payout_probability=float(data.get('payout_probability', 0) or 0),
        owner_minutes=float(data.get('owner_minutes', 0) or 0),
        gox_share=float(data.get('gox_share', 0) or 0),
        time_to_cash_hours=time_to_cash_hours,
        repeatability=float(data.get('repeatability', 0) or 0),
        payout_certainty=float(data.get('payout_certainty', 0) or 0),
        rules_verdict=str(data.get('rules_verdict', 'UNCLEAR')),
        blocker=str(data.get('blocker', '') or ''),
        owner_gate_kind=str(data.get('owner_gate_kind', '') or ''),
        executable_now=bool(data.get('executable_now', False)),
        next_action=str(data.get('next_action', '') or ''),
        evidence=str(data.get('evidence', '') or ''),
        funding_status=str(data.get('funding_status', 'unknown') or 'unknown'),
        verification_status=str(data.get('verification_status', 'unverified') or 'unverified'),
        settlement_status=str(data.get('settlement_status', 'unsettled') or 'unsettled'),
        payment_evidence=str(data.get('payment_evidence', '') or ''),
    )


def upsert_opportunity(db: sqlite3.Connection, op: Opportunity) -> None:
    register_lane(db, op.lane, op.lane.replace('_', ' ').title())
    db.execute(
        '''INSERT INTO opportunities(
          id,source,title,lane,expected_cents,payout_probability,owner_minutes,gox_share,
          time_to_cash_hours,repeatability,payout_certainty,rules_verdict,blocker,
          owner_gate_kind,executable_now,next_action,evidence,score,status,updated_at,
          funding_status,verification_status,settlement_status,payment_evidence,predicted_owner_hour)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
          source=excluded.source,title=excluded.title,lane=excluded.lane,
          expected_cents=excluded.expected_cents,payout_probability=excluded.payout_probability,
          owner_minutes=excluded.owner_minutes,gox_share=excluded.gox_share,
          time_to_cash_hours=excluded.time_to_cash_hours,repeatability=excluded.repeatability,
          payout_certainty=excluded.payout_certainty,rules_verdict=excluded.rules_verdict,
          blocker=excluded.blocker,owner_gate_kind=excluded.owner_gate_kind,
          executable_now=excluded.executable_now,next_action=excluded.next_action,
          evidence=excluded.evidence,score=excluded.score,updated_at=excluded.updated_at,
          funding_status=excluded.funding_status,verification_status=excluded.verification_status,
          settlement_status=excluded.settlement_status,payment_evidence=excluded.payment_evidence,
          predicted_owner_hour=excluded.predicted_owner_hour''',
        (op.id,op.source,op.title,op.lane,op.expected_cents,op.payout_probability,
         op.owner_minutes,op.gox_share,op.time_to_cash_hours,op.repeatability,
         op.payout_certainty,op.rules_verdict,op.blocker,op.owner_gate_kind,
         int(op.executable_now),op.next_action,op.evidence,score(op),'candidate',now(),
         op.funding_status,op.verification_status,op.settlement_status,op.payment_evidence,
         predicted_owner_hour(op)),
    )
    db.commit()


def ingest(db: sqlite3.Connection) -> int:
    INBOX.mkdir(parents=True, exist_ok=True)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    count = 0
    for path in sorted(INBOX.glob('*.json')):
        try:
            payload = json.loads(path.read_text())
            items = payload if isinstance(payload, list) else [payload]
            for item in items:
                upsert_opportunity(db, parse_opportunity(item))
                count += 1
            target = ARCHIVE / f'{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")}-{path.name}'
            path.replace(target)
        except Exception as exc:
            bad = ARCHIVE / f'BAD-{path.name}'
            path.replace(bad)
            bad.with_suffix('.error.txt').write_text(str(exc))
    return count


def qualified(db: sqlite3.Connection) -> list[dict]:
    db.row_factory = sqlite3.Row
    rows = db.execute(
        '''SELECT * FROM opportunities
           WHERE rules_verdict IN ('ALLOWED','ALLOWED_WITH_CONDITIONS')
             AND blocker=''
             AND settlement_status != 'settled'
           ORDER BY score DESC, updated_at DESC'''
    ).fetchall()
    return [dict(r) for r in rows]


def route_selected(db: sqlite3.Connection, candidate: dict | None) -> str:
    if not candidate:
        return ''
    oid = candidate['id']
    gate_kind = candidate['owner_gate_kind'] or ''
    if gate_kind:
        enqueue(db, WorkItem(
            id=f'owner-gate:{oid}', lane=candidate['lane'], kind=gate_kind,
            objective=candidate['next_action'] or f'Complete owner gate for {candidate["title"]}',
            status='queued', owner_gate=True, gate_reason=gate_kind,
            idempotency_key=f'opportunity:{oid}:owner-gate'))
        db.execute("UPDATE opportunities SET status='owner_gate' WHERE id=?", (oid,))
    else:
        enqueue(db, WorkItem(
            id=f'execute:{oid}', lane=candidate['lane'], kind='revenue_execution',
            objective=candidate['next_action'] or f'Advance {candidate["title"]}',
            status='queued', owner_gate=False,
            idempotency_key=f'opportunity:{oid}:execute'))
        db.execute("UPDATE opportunities SET status='selected' WHERE id=?", (oid,))
    db.commit()
    return oid


def record_outcome(db: sqlite3.Connection, *, opportunity_id: str, actual_net_cents: int,
                   actual_owner_minutes: float, settlement_status: str,
                   payment_evidence: str = '') -> None:
    row = db.execute('SELECT predicted_owner_hour FROM opportunities WHERE id=?', (opportunity_id,)).fetchone()
    predicted = float(row[0]) if row else 0.0
    owner_hours = max(0.0833, actual_owner_minutes / 60.0)
    actual_hour = round((actual_net_cents / 100.0) / owner_hours, 4) if actual_net_cents > 0 else 0.0
    db.execute(
        '''INSERT INTO economics_outcomes(
           opportunity_id,predicted_owner_hour,actual_net_cents,actual_owner_minutes,
           actual_owner_hour,settlement_status,payment_evidence,updated_at)
           VALUES(?,?,?,?,?,?,?,?)
           ON CONFLICT(opportunity_id) DO UPDATE SET
             predicted_owner_hour=excluded.predicted_owner_hour,
             actual_net_cents=excluded.actual_net_cents,
             actual_owner_minutes=excluded.actual_owner_minutes,
             actual_owner_hour=excluded.actual_owner_hour,
             settlement_status=excluded.settlement_status,
             payment_evidence=excluded.payment_evidence,
             updated_at=excluded.updated_at''',
        (opportunity_id,predicted,actual_net_cents,actual_owner_minutes,actual_hour,
         settlement_status,payment_evidence,now()),
    )
    db.execute(
        'UPDATE opportunities SET settlement_status=?, payment_evidence=? WHERE id=?',
        (settlement_status,payment_evidence,opportunity_id),
    )
    db.commit()


def calibration_summary(db: sqlite3.Connection) -> dict:
    rows = db.execute(
        "SELECT predicted_owner_hour,actual_owner_hour FROM economics_outcomes WHERE settlement_status='settled'"
    ).fetchall()
    if not rows:
        return {'settled_samples': 0, 'mean_predicted_owner_hour': 0.0, 'mean_actual_owner_hour': 0.0}
    n = len(rows)
    return {
        'settled_samples': n,
        'mean_predicted_owner_hour': round(sum(r[0] for r in rows) / n, 4),
        'mean_actual_owner_hour': round(sum(r[1] for r in rows) / n, 4),
    }


def build_report(db: sqlite3.Connection, ingested_count: int) -> dict:
    q = qualified(db)
    selected = q[0] if q else None
    selected_id = route_selected(db, selected)
    money = money_summary(db)
    report = {
        'ts': now(),
        'engine': 'GOX Revenue Engine',
        'ingested': ingested_count,
        'qualified_count': len(q),
        'selected': selected,
        'top_options': q[:7],
        'verified_revenue': money['verified_net_dollars'],
        'calibration': calibration_summary(db),
        'owner_alert': 'PAY ATTENTION' if selected and selected.get('owner_gate_kind') else 'NO ACTION NEEDED',
        'next_action': selected.get('next_action') if selected else 'Acquire more qualified opportunity signals',
    }
    ENGINE_ROOT.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True))
    db.execute(
        'INSERT INTO engine_runs(ts,ingested,qualified,selected_id,report) VALUES(?,?,?,?,?)',
        (report['ts'], ingested_count, len(q), selected_id, json.dumps(report, sort_keys=True)),
    )
    db.commit()
    return report


def run_once(db_path: Path | None = None) -> dict:
    db = connect(db_path) if db_path else connect()
    try:
        ensure_schema(db)
        ingested_count = ingest(db)
        return build_report(db, ingested_count)
    finally:
        db.close()


def main() -> int:
    print(json.dumps(run_once(), indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
