#!/usr/bin/env python3
"""Read-only public buyer-request scout.

Ingests only explicit existing demand: hiring posts, paid projects, and people
already asking someone to build/fix/automate/integrate/deliver work. It never
prospects inferred needs or sends messages.
"""
from __future__ import annotations
import hashlib,html,json,re,urllib.request,xml.etree.ElementTree as ET
from dataclasses import asdict
from typing import Iterable
from demand_to_cash import Opportunity
USER_AGENT="GOX-BuyerRequestScout/0.4 (read-only public demand)";ATOM={"a":"http://www.w3.org/2005/Atom"}
BUYER_MARKERS=("[hiring]","[paid]","hiring ","looking to hire","looking for someone","looking for an experienced","looking for a developer","looking for an automation","we're looking for","we are looking for","need someone","need a developer","need an automation","need help with","seeking ","contractor needed","paid project","willing to pay","accepting bids","looking for a specialist","looking for a freelancer","freelancer wanted","developer wanted","developer needed","builder wanted","builders required","automation specialist","automation engineer")
REJECT_MARKERS=("[for hire]","for hire","available for work","hire me","my services","i'm available","i am available")
MONEY_RE=re.compile(r"\$\s?(\d{2,6})(?:\s*[-–—to]+\s*\$?\s?(\d{2,6}))?",re.I);HOURLY_RE=re.compile(r"\$\s?(\d{2,4})(?:\s*[-–—to]+\s*\$?\s?(\d{2,4}))?\s*(?:/|per\s*)?(?:hr|hour)",re.I);TAG_RE=re.compile(r"<[^>]+>")
def _clean(v):v=html.unescape(v or "");return re.sub(r"\s+"," ",TAG_RE.sub(" ",v)).strip()
def explicit_demand(title,body):
 text=f"{title} {body}".lower()
 if any(x in text for x in REJECT_MARKERS):return False
 return any(x in text for x in BUYER_MARKERS)
def extract_budget(text):
 hourly=HOURLY_RE.search(text)
 if hourly:
  low=float(hourly.group(1));high=float(hourly.group(2) or low);return low*4.0,high*4.0
 fixed=MONEY_RE.search(text)
 if fixed:
  low=float(fixed.group(1));high=float(fixed.group(2) or low);return low,high
 return 0.0,0.0
def _get(url,accept,timeout=10):
 req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":accept})
 with urllib.request.urlopen(req,timeout=timeout) as resp:
  if resp.status!=200:raise RuntimeError(f"HTTP {resp.status}: {url}")
  return resp.read(2_000_000)
def parse_atom(raw,source):
 root=ET.fromstring(raw);out=[]
 for entry in root.findall("a:entry",ATOM):
  title=_clean(entry.findtext("a:title",default="",namespaces=ATOM));content=_clean(entry.findtext("a:content",default="",namespaces=ATOM));link_el=entry.find("a:link",ATOM);url=link_el.attrib.get("href","") if link_el is not None else "";external_id=_clean(entry.findtext("a:id",default=url,namespaces=ATOM)) or url
  if not explicit_demand(title,content):continue
  low,high=extract_budget(f"{title} {content}");out.append(Opportunity(source=source,external_id=external_id or hashlib.sha256((title+url).encode()).hexdigest()[:16],title=title,description=content[:4000],budget_min=low,budget_max=high,source_url=url,explicit_demand=True))
 return out
def fetch_atom(url,source,timeout=10):return parse_atom(_get(url,"application/atom+xml,application/xml;q=0.9,*/*;q=0.1",timeout),source)
def fetch_n8n_jobs(limit=20,timeout=10):
 """Read recent topics from the official n8n Community Jobs category via Discourse JSON."""
 base="https://community.n8n.io";category=json.loads(_get(base+"/c/jobs/13.json","application/json",timeout))
 topics=(category.get("topic_list") or {}).get("topics") or [];out=[]
 for topic in topics[:limit]:
  tid=topic.get("id");slug=topic.get("slug") or "topic";title=_clean(topic.get("title") or "")
  if not tid:continue
  url=f"{base}/t/{slug}/{tid}"
  try:
   detail=json.loads(_get(url+".json","application/json",timeout));posts=(detail.get("post_stream") or {}).get("posts") or [];body=_clean(posts[0].get("cooked") if posts else "")
  except Exception:body=_clean(topic.get("excerpt") or "")
  if not explicit_demand(title,body):continue
  low,high=extract_budget(f"{title} {body}")
  out.append(Opportunity(source="n8n-community-jobs",external_id=str(tid),title=title,description=body[:4000],budget_min=low,budget_max=high,source_url=url,explicit_demand=True))
 return out
def default_sources():
 return [("reddit-forhire-new","https://www.reddit.com/r/forhire/new/.rss"),("reddit-freelance-forhire-new","https://www.reddit.com/r/freelance_forhire/new/.rss"),("reddit-n8n-new","https://www.reddit.com/r/n8n/new/.rss"),("reddit-automation-new","https://www.reddit.com/r/automation/new/.rss"),("reddit-ai-automations-new","https://www.reddit.com/r/AiAutomations/new/.rss"),("reddit-remote-python-new","https://www.reddit.com/r/remotepython/new/.rss"),("reddit-search-hiring-n8n","https://www.reddit.com/search.rss?q=%22hiring%22%20n8n&sort=new"),("reddit-search-looking-n8n","https://www.reddit.com/search.rss?q=%22looking%20for%22%20n8n&sort=new"),("reddit-search-automation-specialist","https://www.reddit.com/search.rss?q=%22automation%20specialist%22%20hiring&sort=new"),("reddit-search-workflow-freelancer","https://www.reddit.com/search.rss?q=%22workflow%22%20%22freelancer%22%20automation&sort=new"),("reddit-search-need-automation","https://www.reddit.com/search.rss?q=%22need%22%20%22automation%22%20%22%24%22&sort=new")]
def scout(sources:Iterable[tuple[str,str]]|None=None):
 seen=set();out=[]
 # This is currently the densest source of explicit n8n buyer demand, so scan it first.
 try:candidates=fetch_n8n_jobs()
 except Exception:candidates=[]
 for item in candidates:
  key=item.source_url.split("?",1)[0].rstrip("/") if item.source_url else (item.source,item.external_id)
  if key not in seen:seen.add(key);out.append(item)
 for source,url in (sources or default_sources()):
  try:items=fetch_atom(url,source)
  except Exception:continue
  for item in items:
   key=item.source_url.split("?",1)[0].rstrip("/") if item.source_url else (item.source,item.external_id)
   if key in seen:continue
   seen.add(key);out.append(item)
 return out
if __name__=="__main__":print(json.dumps([asdict(x) for x in scout()],indent=2))
