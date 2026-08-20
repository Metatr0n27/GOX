#!/usr/bin/env python3
"""Restart-safe job recovery primitives for GOX."""
import json
import os
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

DB_PATH = Path(os.environ.get("GOX_STATE_DB", "/var/lib/gox/state/gox.db"))

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS jobs (
  job_id TEXT PRIMARY KEY,
  lane_id TEXT,
  kind TEXT NOT NULL,
  status TEXT NOT NULL,
  consequential INTEGER NOT NULL DEFAULT 0,
  idempotency_key TEXT UNIQUE,
  lease_owner TEXT,
  lease_expires_at TEXT,
  attempt_count INTEGER NOT NULL DEFAULT 0,
  max_attempts INTEGER NOT NULL DEFAULT 3,
  payload_json TEXT NOT NULL DEFAULT '{}',
  last_error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
"""

def now(): return datetime.now(timezone.utc)
def iso(dt=None): return (dt or now()).isoformat()

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con=sqlite3.connect(DB_PATH)
    con.row_factory=sqlite3.Row
    con.executescript(SCHEMA)
    return con

def enqueue(job_id, kind, lane_id=None, payload=None, consequential=False, idempotency_key=None, max_attempts=3):
    if consequential and not idempotency_key:
        raise ValueError('consequential jobs require idempotency_key')
    with connect() as con:
        con.execute("INSERT OR IGNORE INTO jobs(job_id,lane_id,kind,status,consequential,idempotency_key,max_attempts,payload_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",(job_id,lane_id,kind,'queued',int(consequential),idempotency_key,int(max_attempts),json.dumps(payload or {},sort_keys=True),iso(),iso()))

def claim(worker, lease_seconds=120):
    with connect() as con:
        con.execute("BEGIN IMMEDIATE")
        n=iso()
        row=con.execute("SELECT * FROM jobs WHERE status='queued' OR (status='running' AND lease_expires_at IS NOT NULL AND lease_expires_at < ?) ORDER BY created_at LIMIT 1",(n,)).fetchone()
        if not row: return None
        if row['attempt_count'] >= row['max_attempts']:
            con.execute("UPDATE jobs SET status='blocked',updated_at=? WHERE job_id=?",(n,row['job_id']))
            return None
        exp=iso(now()+timedelta(seconds=lease_seconds))
        con.execute("UPDATE jobs SET status='running',lease_owner=?,lease_expires_at=?,attempt_count=attempt_count+1,updated_at=? WHERE job_id=?",(worker,exp,n,row['job_id']))
        return dict(con.execute("SELECT * FROM jobs WHERE job_id=?",(row['job_id'],)).fetchone())

def complete(job_id):
    with connect() as con: con.execute("UPDATE jobs SET status='complete',lease_owner=NULL,lease_expires_at=NULL,updated_at=? WHERE job_id=?",(iso(),job_id))

def fail(job_id, error, retryable=True):
    with connect() as con:
        row=con.execute("SELECT attempt_count,max_attempts FROM jobs WHERE job_id=?",(job_id,)).fetchone()
        if not row: raise KeyError(job_id)
        status='queued' if retryable and row['attempt_count'] < row['max_attempts'] else 'blocked'
        con.execute("UPDATE jobs SET status=?,last_error=?,lease_owner=NULL,lease_expires_at=NULL,updated_at=? WHERE job_id=?",(status,str(error)[:2000],iso(),job_id))

def recover_stale():
    with connect() as con:
        n=iso(); rows=con.execute("SELECT job_id,consequential,attempt_count,max_attempts FROM jobs WHERE status='running' AND lease_expires_at IS NOT NULL AND lease_expires_at < ?",(n,)).fetchall()
        out=[]
        for r in rows:
            status='blocked' if r['consequential'] or r['attempt_count'] >= r['max_attempts'] else 'queued'
            con.execute("UPDATE jobs SET status=?,lease_owner=NULL,lease_expires_at=NULL,updated_at=? WHERE job_id=?",(status,n,r['job_id']))
            out.append({'job_id':r['job_id'],'status':status})
        return out

if __name__=='__main__': print(json.dumps(recover_stale(),indent=2))
