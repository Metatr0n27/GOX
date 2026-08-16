#!/usr/bin/env python3
"""GOX revenue-engine persistence and deterministic opportunity scoring."""
import hashlib
import json
import sqlite3
import time


def init_revenue_schema(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS opportunities(
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        source_ref TEXT NOT NULL,
        title TEXT NOT NULL,
        deliverable TEXT NOT NULL,
        gross_payout REAL NOT NULL DEFAULT 0,
        estimated_cost REAL NOT NULL DEFAULT 0,
        win_probability REAL NOT NULL DEFAULT 0,
        same_day_probability REAL NOT NULL DEFAULT 0,
        fulfillment_minutes INTEGER,
        capability TEXT,
        status TEXT NOT NULL DEFAULT 'found',
        blocker TEXT,
        captured_at REAL NOT NULL,
        updated_at REAL NOT NULL,
        UNIQUE(source, source_ref)
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS revenue_events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        opportunity_id TEXT,
        event_type TEXT NOT NULL,
        amount REAL NOT NULL DEFAULT 0,
        evidence TEXT,
        created_at REAL NOT NULL,
        FOREIGN KEY(opportunity_id) REFERENCES opportunities(id)
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_opportunity_status ON opportunities(status, captured_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_revenue_created ON revenue_events(created_at)")


def fingerprint(source, source_ref):
    return hashlib.sha256(f"{source}\0{source_ref}".encode()).hexdigest()[:16]


def clamp_probability(value):
    return max(0.0, min(1.0, float(value)))


def score(gross_payout, estimated_cost, win_probability, same_day_probability, fulfillment_minutes=None):
    net=max(0.0,float(gross_payout)-float(estimated_cost))
    expected=net*clamp_probability(win_probability)*clamp_probability(same_day_probability)
    # A separate efficiency metric prevents tiny fast jobs from replacing expected cash value.
    hours=max((fulfillment_minutes or 60)/60.0, 0.25)
    return {"net_payout":round(net,2),"expected_value_today":round(expected,2),"expected_value_per_hour":round(expected/hours,2)}


def upsert_opportunity(conn, item):
    required=("source","source_ref","title","deliverable")
    missing=[k for k in required if not str(item.get(k,"")).strip()]
    if missing: raise ValueError("missing fields: "+", ".join(missing))
    oid=fingerprint(item["source"],item["source_ref"]); now=time.time()
    values=(oid,item["source"],item["source_ref"],item["title"],item["deliverable"],float(item.get("gross_payout",0)),float(item.get("estimated_cost",0)),clamp_probability(item.get("win_probability",0)),clamp_probability(item.get("same_day_probability",0)),item.get("fulfillment_minutes"),item.get("capability"),item.get("status","found"),item.get("blocker"),now,now)
    conn.execute("""INSERT INTO opportunities(id,source,source_ref,title,deliverable,gross_payout,estimated_cost,win_probability,same_day_probability,fulfillment_minutes,capability,status,blocker,captured_at,updated_at)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(source,source_ref) DO UPDATE SET title=excluded.title,deliverable=excluded.deliverable,gross_payout=excluded.gross_payout,estimated_cost=excluded.estimated_cost,win_probability=excluded.win_probability,same_day_probability=excluded.same_day_probability,fulfillment_minutes=excluded.fulfillment_minutes,capability=excluded.capability,status=excluded.status,blocker=excluded.blocker,updated_at=excluded.updated_at""",values)
    return oid


def record_revenue(conn, opportunity_id, amount, evidence):
    if amount <= 0: raise ValueError("collected revenue must be positive")
    if not evidence: raise ValueError("revenue requires verification evidence")
    conn.execute("INSERT INTO revenue_events(opportunity_id,event_type,amount,evidence,created_at) VALUES(?,?,?,?,?)",(opportunity_id,"collected",float(amount),json.dumps(evidence),time.time()))


def collected_since(conn, since):
    row=conn.execute("SELECT COALESCE(SUM(amount),0) FROM revenue_events WHERE event_type='collected' AND created_at>=?",(since,)).fetchone()
    return float(row[0])
