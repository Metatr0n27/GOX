#!/usr/bin/env python3
"""Rank missing money-making capabilities from real rejected buyer demand.

This radar does not widen what GOX is allowed to sell. It only measures explicit
buyer requests that fail current capability verification and recommends what to
verify/build next based on frequency and stated budget.
"""
from __future__ import annotations
import json, os, tempfile
from collections import defaultdict
from pathlib import Path
from capabilities import verified_capabilities
from demand_to_cash import qualify
from scout_public import scout

STATE=Path(os.environ.get("GOX_REVENUE_STATE","/var/lib/gox/revenue"))
OUT=STATE/"demand_gaps.json"
CATEGORIES={
 "api integration":("api","webhook","integration","oauth","rest api","graphql"),
 "spreadsheet automation":("excel","google sheets","spreadsheet","csv","reporting"),
 "web scraping":("scrape","scraping","crawler","crawl","data extraction","selenium","playwright"),
 "data pipeline":("etl","data pipeline","data processing","transform","ingestion"),
 "crm automation":("crm","hubspot","gohighlevel","salesforce","pipedrive","zoho"),
 "ai workflow":("ai agent","agentic","rag","llm","openai","chatbot"),
 "email automation":("email automation","gmail","outlook","follow-up","newsletter"),
 "document automation":("pdf","document processing","invoice","ocr","forms"),
}

def _write(payload):
 OUT.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix=OUT.name+".",dir=str(OUT.parent))
 try:
  with os.fdopen(fd,"w") as f:json.dump(payload,f,indent=2,sort_keys=True);f.flush();os.fsync(f.fileno())
  os.replace(tmp,OUT)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)

def classify(text):
 t=text.lower();hits=[]
 for name,terms in CATEGORIES.items():
  n=sum(1 for term in terms if term in t)
  if n:hits.append((n,name))
 hits.sort(reverse=True)
 return hits[0][1] if hits else "other"

def build():
 verified=verified_capabilities();stats=defaultdict(lambda:{"requests":0,"stated_budget_total":0.0,"max_budget":0.0,"examples":[]})
 scanned=rejected=0
 for opp in scout():
  scanned+=1;q=qualify(opp,verified)
  if q.accepted:continue
  rejected+=1;cat=classify(f"{opp.title} {opp.description}");s=stats[cat];s["requests"]+=1
  stated=max(float(opp.budget_min or 0),float(opp.budget_max or 0));s["stated_budget_total"]+=stated;s["max_budget"]=max(s["max_budget"],stated)
  if len(s["examples"])<5:s["examples"].append({"title":opp.title,"source":opp.source,"source_url":opp.source_url,"budget_max":opp.budget_max,"reason":q.reason})
 ranked=[]
 for category,s in stats.items():
  score=round(s["requests"]*100+s["stated_budget_total"],2)
  ranked.append({"category":category,"unlock_score":score,**s,"recommended_action":"VERIFY_OR_BUILD_CAPABILITY"})
 ranked.sort(key=lambda x:(x["unlock_score"],x["requests"],x["max_budget"]),reverse=True)
 payload={"scanned":scanned,"rejected_for_capability_or_fit":rejected,"ranked_gaps":ranked,"top_gap":ranked[0] if ranked else None};_write(payload);return payload
if __name__=="__main__":print(json.dumps(build(),indent=2))
