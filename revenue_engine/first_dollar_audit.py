#!/usr/bin/env python3
"""Truthful audit of the shortest path to GOX's first collected dollar."""
from __future__ import annotations
import json,os
from pathlib import Path
STATE=Path(os.environ.get("GOX_REVENUE_STATE","/var/lib/gox/revenue"))
def load(name,default):
 try:return json.loads((STATE/name).read_text())
 except Exception:return default
def audit():
 opp=load("opportunities.json",{"items":[]});out=load("closer_outbox.json",{"items":[]});orders=load("orders.json",{"items":[]});payments=load("payments.json",{"items":[]})
 collected=sum(float(x.get("amount",0) or 0) for x in payments.get("items",[]) if x.get("verified") and x.get("status") in ("paid","succeeded","collected"))
 stages={
  "buyer_demand":{"ok":bool(opp.get("items")),"count":len(opp.get("items",[]))},
  "submission_path":{"ok":bool(out.get("items")),"auto_send_ready":out.get("auto_send_ready",0),"human_submit_ready":out.get("human_submit_ready",0)},
  "buyer_contactable_now":{"ok":bool(out.get("auto_send_ready",0)),"count":out.get("auto_send_ready",0)},
  "accepted_orders":{"ok":bool(orders.get("items")),"count":len(orders.get("items",[]))},
  "verified_collected_revenue":{"ok":collected>0,"amount":collected},
 }
 if collected>0:next_gap=None
 elif not stages["buyer_demand"]["ok"]:next_gap="FIND_EXPLICIT_BUYER_DEMAND"
 elif not stages["buyer_contactable_now"]["ok"]:next_gap="CONNECT_OR_USE_AN_AUTHENTICATED_SUBMISSION_CHANNEL"
 elif not stages["accepted_orders"]["ok"]:next_gap="SEND_AND_CLOSE_BUYER_PROPOSALS"
 else:next_gap="COLLECT_AND_VERIFY_PAYMENT"
 return {"first_dollar":collected>0,"collected":collected,"next_gap":next_gap,"stages":stages}
if __name__=="__main__":print(json.dumps(audit(),indent=2))
