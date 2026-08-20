#!/usr/bin/env python3
"""Proof gate: GOX does not claim first dollar until verified paid net >= $1 with evidence."""
import json
import os
import sqlite3
from pathlib import Path

DB_PATH=Path(os.environ.get('GOX_STATE_DB','/var/lib/gox/state/gox.db'))

def proof():
    if not DB_PATH.exists():
        return {'status':'BLOCKED','reason':'state_db_missing','verified_net':0}
    con=sqlite3.connect(DB_PATH); con.row_factory=sqlite3.Row
    try:
        rows=con.execute("SELECT revenue_id,lane_id,opportunity_id,net,evidence_ref,recorded_at FROM revenue WHERE payout_status='verified_paid' AND net>0 AND evidence_ref IS NOT NULL ORDER BY recorded_at").fetchall()
    except sqlite3.OperationalError:
        return {'status':'BLOCKED','reason':'revenue_schema_missing','verified_net':0}
    finally:
        con.close()
    total=sum(float(r['net']) for r in rows)
    return {'status':'PASS' if total>=1 else 'BLOCKED','reason':None if total>=1 else 'less_than_one_verified_net_dollar','verified_net':round(total,2),'evidence':[dict(r) for r in rows]}

if __name__=='__main__':
    r=proof(); print(json.dumps(r,indent=2)); raise SystemExit(0 if r['status']=='PASS' else 2)
