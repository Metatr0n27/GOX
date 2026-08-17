#!/usr/bin/env python3
"""Continuously re-evaluate the first-dollar path in bounded safe cycles."""
from __future__ import annotations
import json,time
from pipeline import build_queue
from first_dollar_audit import audit

def cycle():
 before=audit();actions=[]
 if before.get("next_gap") in ("FIND_EXPLICIT_BUYER_DEMAND","CONNECT_OR_USE_AN_AUTHENTICATED_SUBMISSION_CHANNEL"):
  refreshed=build_queue();actions.append({"action":"refresh_and_route_buyers","qualified":refreshed.get("count",0),"outbox":refreshed.get("closer_outbox",{})})
 after=audit()
 return {"at":time.time(),"before":before,"actions":actions,"after":after,"stopped_at":after.get("next_gap")}
if __name__=="__main__":print(json.dumps(cycle(),indent=2))
