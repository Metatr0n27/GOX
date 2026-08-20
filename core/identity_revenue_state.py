#!/usr/bin/env python3
"""GOX identity-separated job state + revenue ledger.

Standard-library only so it can run on the VPS without extra packages.
"""
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(os.environ.get("GOX_STATE_DB", "/var/lib/gox/state/gox.db"))

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS family_lanes (
  lane_id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS opportunities (
  opportunity_id TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  title TEXT NOT NULL,
  url TEXT,
  platform_rules_checked INTEGER NOT NULL DEFAULT 0,
  ai_assistance_allowed TEXT NOT NULL DEFAULT 'unknown',
  geography_ok INTEGER,
  payout_terms TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS applications (
  application_id TEXT PRIMARY KEY,
  lane_id TEXT NOT NULL REFERENCES family_lanes(lane_id),
  opportunity_id TEXT NOT NULL REFERENCES opportunities(opportunity_id),
  status TEXT NOT NULL,
  submitted_at TEXT,
  confirmation_ref TEXT,
  owner_minutes REAL NOT NULL DEFAULT 0,
  UNIQUE(lane_id, opportunity_id)
);
CREATE TABLE IF NOT EXISTS revenue (
  revenue_id TEXT PRIMARY KEY,
  lane_id TEXT NOT NULL REFERENCES family_lanes(lane_id),
  opportunity_id TEXT REFERENCES opportunities(opportunity_id),
  gross REAL NOT NULL DEFAULT 0,
  fees REAL NOT NULL DEFAULT 0,
  net REAL NOT NULL DEFAULT 0,
  expected_net REAL NOT NULL DEFAULT 0,
  probability REAL NOT NULL DEFAULT 0,
  payout_status TEXT NOT NULL DEFAULT 'expected',
  evidence_ref TEXT,
  owner_minutes REAL NOT NULL DEFAULT 0,
  compute_cost REAL NOT NULL DEFAULT 0,
  recorded_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_type TEXT NOT NULL,
  lane_id TEXT,
  object_id TEXT,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
"""

def now():
    return datetime.now(timezone.utc).isoformat()

@contextmanager
def db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    try:
        yield con
        con.commit()
    finally:
        con.close()

def register_lane(lane_id, display_name):
    with db() as con:
        con.execute("INSERT OR IGNORE INTO family_lanes(lane_id,display_name,created_at) VALUES(?,?,?)", (lane_id, display_name, now()))

def record_event(event_type, lane_id=None, object_id=None, payload=None):
    with db() as con:
        con.execute("INSERT INTO events(event_type,lane_id,object_id,payload_json,created_at) VALUES(?,?,?,?,?)", (event_type,lane_id,object_id,json.dumps(payload or {}, sort_keys=True),now()))

def record_revenue(revenue_id, lane_id, gross=0, fees=0, expected_net=0, probability=0, payout_status='expected', opportunity_id=None, evidence_ref=None, owner_minutes=0, compute_cost=0):
    net = float(gross) - float(fees)
    if payout_status == 'verified_paid' and not evidence_ref:
        raise ValueError('verified_paid requires evidence_ref')
    if not 0 <= float(probability) <= 1:
        raise ValueError('probability must be between 0 and 1')
    with db() as con:
        con.execute("INSERT OR REPLACE INTO revenue(revenue_id,lane_id,opportunity_id,gross,fees,net,expected_net,probability,payout_status,evidence_ref,owner_minutes,compute_cost,recorded_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (revenue_id,lane_id,opportunity_id,float(gross),float(fees),net,float(expected_net),float(probability),payout_status,evidence_ref,float(owner_minutes),float(compute_cost),now()))

def dashboard():
    with db() as con:
        earned = con.execute("SELECT COALESCE(SUM(net),0) v FROM revenue WHERE payout_status='verified_paid'").fetchone()['v']
        expected = con.execute("SELECT COALESCE(SUM(expected_net * probability),0) v FROM revenue WHERE payout_status!='verified_paid'").fetchone()['v']
        by_lane = [dict(r) for r in con.execute("SELECT f.lane_id,f.display_name,COALESCE(SUM(CASE WHEN r.payout_status='verified_paid' THEN r.net ELSE 0 END),0) earned,COALESCE(SUM(CASE WHEN r.payout_status!='verified_paid' THEN r.expected_net*r.probability ELSE 0 END),0) expected FROM family_lanes f LEFT JOIN revenue r ON r.lane_id=f.lane_id GROUP BY f.lane_id,f.display_name ORDER BY f.display_name")]
        return {"verified_net_earned": earned, "probability_weighted_expected_net": expected, "by_lane": by_lane}

if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('command', choices=['init','dashboard'])
    a=p.parse_args()
    if a.command=='init':
        with db(): pass
        print(json.dumps({'status':'PASS','db':str(DB_PATH)}))
    else:
        print(json.dumps(dashboard(), indent=2))
