#!/usr/bin/env python3
"""Durable outcome ledger for GOX revenue learning."""
from __future__ import annotations
import json, os, tempfile, time
from pathlib import Path
STATE=Path(os.environ.get("GOX_REVENUE_STATE","/var/lib/gox/revenue")); LEDGER=STATE/"outcomes.jsonl"
VALID={"submitted","won","lost","delivered","paid","refunded","abandoned"}

def record(opportunity_id:str,outcome:str,amount:float=0.0,reason:str="",metadata:dict|None=None):
 if outcome not in VALID: raise ValueError("invalid outcome")
 if not opportunity_id: raise ValueError("opportunity_id required")
 row={"ts":time.time(),"opportunity_id":opportunity_id,"outcome":outcome,"amount":float(amount),"reason":reason,"metadata":metadata or {}}
 STATE.mkdir(parents=True,exist_ok=True)
 with LEDGER.open("a",encoding="utf-8") as f: f.write(json.dumps(row,sort_keys=True)+"\n"); f.flush(); os.fsync(f.fileno())
 return row

def read_all():
 try:
  return [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()]
 except FileNotFoundError:return []

def summary():
 rows=read_all(); counts={k:0 for k in VALID}; collected=0.0
 for r in rows:
  counts[r["outcome"]]=counts.get(r["outcome"],0)+1
  if r["outcome"]=="paid":collected+=max(0.0,float(r.get("amount",0)))
 submitted=counts.get("submitted",0); won=counts.get("won",0)
 return {"events":len(rows),"counts":counts,"collected":round(collected,2),"win_rate":round(won/submitted,3) if submitted else None}
