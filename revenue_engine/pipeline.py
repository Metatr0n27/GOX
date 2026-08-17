#!/usr/bin/env python3
"""Scout -> qualify -> rank -> fresh proposal-ready queue."""
from __future__ import annotations
import hashlib, json, os, re, tempfile
from datetime import datetime, timezone
from pathlib import Path
from capabilities import verified_capabilities
from demand_to_cash import draft_proposal, qualify
from scout_public import scout
STATE_DIR=Path(os.environ.get("GOX_REVENUE_STATE","/var/lib/gox/revenue")); QUEUE=STATE_DIR/"opportunities.json"; MAX_ITEMS=int(os.environ.get("GOX_REVENUE_QUEUE_MAX","50"))
def _atomic_write(path,payload):
 path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=str(path.parent))
 try:
  with os.fdopen(fd,"w") as f: json.dump(payload,f,indent=2,sort_keys=True); f.flush(); os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def _norm(text):return re.sub(r"[^a-z0-9]+"," ",(text or "").lower()).strip()
def _dedupe_key(o):
 # URL is strongest. Normalized title+budget catches syndicated/cross-posted demand.
 if o.source_url:return "url:"+o.source_url.split("?",1)[0].rstrip("/")
 raw=f"{_norm(o.title)}|{o.budget_min:.2f}|{o.budget_max:.2f}"; return "sig:"+hashlib.sha256(raw.encode()).hexdigest()[:20]
def build_queue():
 now=datetime.now(timezone.utc).isoformat(); rows=[]; seen=set(); scanned=0; rejected=0; duplicates=0
 for opportunity in scout():
  scanned+=1; key=_dedupe_key(opportunity)
  if key in seen:duplicates+=1; continue
  seen.add(key); q=qualify(opportunity,verified_capabilities())
  if not q.accepted:rejected+=1; continue
  rows.append({"id":f"{opportunity.source}:{opportunity.external_id}","dedupe_key":key,"state":"PROPOSAL_READY","source":opportunity.source,"source_url":opportunity.source_url,"title":opportunity.title,"budget_min":opportunity.budget_min,"budget_max":opportunity.budget_max,"currency":opportunity.currency,"score":q.score,"capability":q.capability,"proposal":draft_proposal(opportunity,q),"scouted_at":now})
 rows.sort(key=lambda x:(x["score"],x["budget_max"]),reverse=True); items=rows[:MAX_ITEMS]
 payload={"generated_at":now,"count":len(items),"scanned":scanned,"rejected":rejected,"duplicates_suppressed":duplicates,"items":items}; _atomic_write(QUEUE,payload); return payload
def read_queue():
 try:return json.loads(QUEUE.read_text())
 except (FileNotFoundError,json.JSONDecodeError):return {"generated_at":None,"count":0,"scanned":0,"rejected":0,"duplicates_suppressed":0,"items":[]}
if __name__=="__main__":print(json.dumps(build_queue(),indent=2))
