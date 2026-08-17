#!/usr/bin/env python3
"""Create an isolated customer configuration from a GOX edition and intake answers.

This is packaging logic only: it never copies internal secrets, deployment controls,
or unrestricted operator capabilities into a customer package.
"""
from __future__ import annotations
import json,re,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def load_json(name): return json.loads((ROOT/name).read_text())
def slug(value): return re.sub(r"[^a-z0-9]+","-",value.lower()).strip("-")[:60] or "customer"
def get_edition(edition_id):
 for e in load_json("editions.json")["editions"]:
  if e["id"]==edition_id:return e
 raise ValueError("unknown edition")
def build(customer_name,edition_id,answers):
 edition=get_edition(edition_id)
 required={q["id"] for q in load_json("customer_intake.json")["questions"] if q.get("required",True)}
 missing=sorted(x for x in required if not str(answers.get(x,"")).strip())
 if missing:raise ValueError("missing intake answers: "+", ".join(missing))
 cid=slug(customer_name)
 config={"customer_id":cid,"customer_name":customer_name,"edition":edition_id,"edition_name":edition["name"],"commercial":{"price_usd":edition["price_usd"],"billing":edition.get("billing","one-time")},"profile":answers,"product_boundary":{"includes":edition["includes"],"excludes":edition["excludes"]},"scoreboard":{"opportunities_found":0,"offers_sent":0,"buyer_replies":0,"accepted_orders":0,"verified_collected_revenue":0.0},"activation":{"state":"PROVISIONED_NOT_ACTIVATED","real_opportunity_test_passed":False},"created_at":time.time()}
 return config

def main(argv):
 if len(argv)!=5:raise SystemExit("usage: provision.py CUSTOMER_NAME EDITION_ID ANSWERS.json OUTPUT.json")
 cfg=build(argv[1],argv[2],json.loads(Path(argv[3]).read_text()));Path(argv[4]).write_text(json.dumps(cfg,indent=2,sort_keys=True));print(argv[4])
if __name__=="__main__":main(sys.argv)
