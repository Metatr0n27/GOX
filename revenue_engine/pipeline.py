#!/usr/bin/env python3
"""Scout -> qualify -> rank -> proposal-ready queue with explicit close path."""
from __future__ import annotations
import hashlib,json,os,re,tempfile
from datetime import datetime,timezone,timedelta
from pathlib import Path
from capabilities import verified_capabilities
from demand_to_cash import draft_proposal,qualify
from scout_public import scout
STATE_DIR=Path(os.environ.get("GOX_REVENUE_STATE","/var/lib/gox/revenue"));QUEUE=STATE_DIR/"opportunities.json";MAX_ITEMS=int(os.environ.get("GOX_REVENUE_QUEUE_MAX","50"));MAX_AGE_HOURS=int(os.environ.get("GOX_REVENUE_MAX_AGE_HOURS","24"))
def _atomic_write(path,payload):
 path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=str(path.parent))
 try:
  with os.fdopen(fd,"w") as f:json.dump(payload,f,indent=2,sort_keys=True);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def _norm(text):return re.sub(r"[^a-z0-9]+"," ",(text or "").lower()).strip()
def _dedupe_key(o):
 if o.source_url:return "url:"+o.source_url.split("?",1)[0].rstrip("/")
 return "sig:"+hashlib.sha256(f"{_norm(o.title)}|{o.budget_min:.2f}|{o.budget_max:.2f}".encode()).hexdigest()[:20]
def _is_fresh(item,now=None):
 now=now or datetime.now(timezone.utc);raw=item.get("scouted_at")
 if not raw:return False
 try:ts=datetime.fromisoformat(raw.replace("Z","+00:00"))
 except ValueError:return False
 return now-ts<=timedelta(hours=MAX_AGE_HOURS)
def build_queue():
 now_dt=datetime.now(timezone.utc);now=now_dt.isoformat();rows=[];seen=set();scanned=rejected=duplicates=0
 for opportunity in scout():
  scanned+=1;key=_dedupe_key(opportunity)
  if key in seen:duplicates+=1;continue
  seen.add(key);q=qualify(opportunity,verified_capabilities())
  if not q.accepted:rejected+=1;continue
  rows.append({"id":f"{opportunity.source}:{opportunity.external_id}","dedupe_key":key,"state":"PROPOSAL_READY_NEEDS_ROUTE","source":opportunity.source,"source_url":opportunity.source_url,"title":opportunity.title,"description":opportunity.description,"budget_min":opportunity.budget_min,"budget_max":opportunity.budget_max,"currency":opportunity.currency,"score":q.score,"capability":q.capability,"proposal":draft_proposal(opportunity,q),"scouted_at":now,"expires_at":(now_dt+timedelta(hours=MAX_AGE_HOURS)).isoformat()})
 rows.sort(key=lambda x:(x["score"],x["budget_max"]),reverse=True);items=rows[:MAX_ITEMS];payload={"generated_at":now,"count":len(items),"scanned":scanned,"rejected":rejected,"duplicates_suppressed":duplicates,"max_age_hours":MAX_AGE_HOURS,"items":items};_atomic_write(QUEUE,payload)
 try:
  from closer_outbox import build_outbox
  payload["closer_outbox"]=build_outbox()
 except Exception as exc:payload["closer_outbox_error"]=str(exc)
 return payload
def read_queue():
 try:payload=json.loads(QUEUE.read_text())
 except (FileNotFoundError,json.JSONDecodeError):return {"generated_at":None,"count":0,"scanned":0,"rejected":0,"duplicates_suppressed":0,"stale_suppressed":0,"items":[]}
 items=payload.get("items",[]);fresh=[i for i in items if _is_fresh(i)];payload["stale_suppressed"]=len(items)-len(fresh);payload["items"]=fresh;payload["count"]=len(fresh);return payload
if __name__=="__main__":print(json.dumps(build_queue(),indent=2))
