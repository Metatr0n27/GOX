#!/usr/bin/env python3
"""Build a durable outbound queue from proposal-ready opportunities.

This module does not impersonate an owner or bypass marketplace authentication.
It makes the sales gap explicit by classifying each qualified opportunity into a
submission path and persisting the exact buyer-specific message, URL, and gate.
"""
from __future__ import annotations
import json, os, re, tempfile
from pathlib import Path
from urllib.parse import urlparse
from pipeline import read_queue

STATE_DIR=Path(os.environ.get("GOX_REVENUE_STATE","/var/lib/gox/revenue"))
OUTBOX=STATE_DIR/"closer_outbox.json"
EMAIL_RE=re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",re.I)

def _atomic_write(path,payload):
 path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=str(path.parent))
 try:
  with os.fdopen(fd,"w") as f:json.dump(payload,f,indent=2,sort_keys=True);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)

def classify(item):
 text=" ".join(str(item.get(k,"")) for k in ("title","proposal","source_url","source"))
 emails=EMAIL_RE.findall(text)
 if emails:
  return {"channel":"email","target":emails[0],"human_gate":False,"reason":"direct buyer email available"}
 url=item.get("source_url") or "";host=(urlparse(url).hostname or "").lower()
 if "reddit.com" in host:return {"channel":"reddit","target":url,"human_gate":True,"reason":"marketplace/account login required"}
 if "freelancer.com" in host:return {"channel":"freelancer","target":url,"human_gate":True,"reason":"marketplace/account login and bid submission required"}
 if "upwork.com" in host:return {"channel":"upwork","target":url,"human_gate":True,"reason":"marketplace/account login and proposal submission required"}
 if url:return {"channel":"web","target":url,"human_gate":True,"reason":"external site submission path not connected"}
 return {"channel":"unknown","target":"","human_gate":True,"reason":"no buyer contact path found"}

def build_outbox():
 q=read_queue();items=[]
 for opp in q.get("items",[]):
  route=classify(opp)
  items.append({
   "opportunity_id":opp.get("id"),"title":opp.get("title"),"budget_min":opp.get("budget_min"),"budget_max":opp.get("budget_max"),
   "capability":opp.get("capability"),"score":opp.get("score"),"proposal":opp.get("proposal"),"source_url":opp.get("source_url"),
   "submission":route,"state":"AUTO_SEND_READY" if not route["human_gate"] else "HUMAN_SUBMIT_READY"
  })
 payload={"count":len(items),"auto_send_ready":sum(1 for x in items if x["state"]=="AUTO_SEND_READY"),"human_submit_ready":sum(1 for x in items if x["state"]=="HUMAN_SUBMIT_READY"),"items":items}
 _atomic_write(OUTBOX,payload);return payload

def read_outbox():
 try:return json.loads(OUTBOX.read_text())
 except Exception:return {"count":0,"auto_send_ready":0,"human_submit_ready":0,"items":[]}

if __name__=="__main__":print(json.dumps(build_outbox(),indent=2))
