#!/usr/bin/env python3
"""Durable outbound queue from proposal-ready opportunities."""
from __future__ import annotations
import json,os,re,tempfile
from pathlib import Path
from urllib.parse import urlparse
from pipeline import read_queue
STATE_DIR=Path(os.environ.get("GOX_REVENUE_STATE","/var/lib/gox/revenue"));OUTBOX=STATE_DIR/"closer_outbox.json";EMAIL_RE=re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",re.I)
def _atomic_write(path,payload):
 path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=str(path.parent))
 try:
  with os.fdopen(fd,"w") as f:json.dump(payload,f,indent=2,sort_keys=True);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def classify(item):
 # Preserve the buyer's original post body: contact details often live there, not in the title/proposal.
 text=" ".join(str(item.get(k,"")) for k in ("title","description","proposal","source_url","source"));emails=EMAIL_RE.findall(text)
 if emails:return {"channel":"email","target":emails[0],"human_gate":False,"reason":"direct buyer email available","next_action":"SEND_BUYER_PROPOSAL"}
 url=item.get("source_url") or "";host=(urlparse(url).hostname or "").lower()
 if "reddit.com" in host:return {"channel":"reddit","target":url,"human_gate":True,"reason":"authenticated Reddit submission unavailable","next_action":"SUBMIT_ON_REDDIT"}
 if "community.n8n.io" in host:return {"channel":"n8n-community","target":url,"human_gate":True,"reason":"authenticated n8n Community submission unavailable","next_action":"REPLY_ON_N8N_COMMUNITY"}
 if "freelancer.com" in host:return {"channel":"freelancer","target":url,"human_gate":True,"reason":"authenticated bid submission unavailable","next_action":"SUBMIT_FREELANCER_BID"}
 if "upwork.com" in host:return {"channel":"upwork","target":url,"human_gate":True,"reason":"authenticated proposal submission unavailable","next_action":"SUBMIT_UPWORK_PROPOSAL"}
 if url:return {"channel":"web","target":url,"human_gate":True,"reason":"external submission surface not connected","next_action":"OPEN_SUBMISSION_PAGE"}
 return {"channel":"unknown","target":"","human_gate":True,"reason":"no buyer contact path found","next_action":"FIND_CONTACT_PATH"}
def build_outbox():
 q=read_queue();items=[]
 for opp in q.get("items",[]):
  route=classify(opp);items.append({"opportunity_id":opp.get("id"),"title":opp.get("title"),"budget_min":opp.get("budget_min"),"budget_max":opp.get("budget_max"),"capability":opp.get("capability"),"score":opp.get("score"),"proposal":opp.get("proposal"),"source_url":opp.get("source_url"),"submission":route,"state":"AUTO_SEND_READY" if not route["human_gate"] else "HUMAN_SUBMIT_READY"})
 items.sort(key=lambda x:(x["state"]=="AUTO_SEND_READY",x.get("score") or 0,x.get("budget_max") or 0),reverse=True)
 payload={"count":len(items),"auto_send_ready":sum(x["state"]=="AUTO_SEND_READY" for x in items),"human_submit_ready":sum(x["state"]=="HUMAN_SUBMIT_READY" for x in items),"blocked_without_route":sum(x["submission"]["channel"]=="unknown" for x in items),"items":items};_atomic_write(OUTBOX,payload);return payload
def read_outbox():
 try:return json.loads(OUTBOX.read_text())
 except Exception:return {"count":0,"auto_send_ready":0,"human_submit_ready":0,"blocked_without_route":0,"items":[]}
if __name__=="__main__":print(json.dumps(build_outbox(),indent=2))
