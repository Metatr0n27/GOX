#!/usr/bin/env python3
"""Convert an explicit buyer acceptance into a durable GOX order.

This closes the gap between a sales conversation and fulfillment/payment state.
It never fabricates acceptance: callers must supply evidence of buyer acceptance.
"""
from __future__ import annotations
import hashlib,json,os,tempfile,time
from pathlib import Path
STATE=Path(os.environ.get("GOX_REVENUE_STATE","/var/lib/gox/revenue"));ORDERS=STATE/"orders.json";PAYMENTS=STATE/"payments.json"
def _load(path):
 try:return json.loads(path.read_text())
 except Exception:return {"items":[]}
def _write(path,payload):
 path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=str(path.parent))
 try:
  with os.fdopen(fd,"w") as f:json.dump(payload,f,indent=2,sort_keys=True);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def accept(opportunity_id,title,amount,currency="USD",acceptance_evidence="",buyer_contact=""):
 if not acceptance_evidence.strip():raise ValueError("buyer acceptance evidence required")
 oid="ord_"+hashlib.sha256(f"{opportunity_id}|{acceptance_evidence}".encode()).hexdigest()[:16];orders=_load(ORDERS)
 if not any(x.get("id")==oid for x in orders["items"]):orders["items"].append({"id":oid,"opportunity_id":opportunity_id,"title":title,"amount":float(amount),"currency":currency,"buyer_contact":buyer_contact,"acceptance_evidence":acceptance_evidence,"status":"ACCEPTED_AWAITING_PAYMENT","created_at":time.time()});_write(ORDERS,orders)
 payments=_load(PAYMENTS);pid="pay_"+oid[4:]
 if not any(x.get("id")==pid for x in payments["items"]):payments["items"].append({"id":pid,"order_id":oid,"amount":float(amount),"currency":currency,"status":"awaiting_payment","verified":False,"created_at":time.time()});_write(PAYMENTS,payments)
 return {"order_id":oid,"payment_id":pid,"status":"ACCEPTED_AWAITING_PAYMENT"}
if __name__=="__main__":print("order_intake requires explicit buyer acceptance evidence")
