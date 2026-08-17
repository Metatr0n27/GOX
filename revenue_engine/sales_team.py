#!/usr/bin/env python3
"""Sales execution policy focused on real transactions, not internal activity."""
from __future__ import annotations

TEAM=[
 {"name":"Fresh Cash Hunter","owns":"find explicit paid work posted recently, prioritize hours-old demand"},
 {"name":"Agency Overflow Hunter","owns":"find agencies/consultancies already selling automation and needing fulfillment capacity"},
 {"name":"Contact Path Hunter","owns":"find a lawful public direct contact route for qualified buyers before falling back to marketplace-only channels"},
 {"name":"Offer Selector","owns":"choose the smallest credible paid offer GOX can verify and deliver"},
 {"name":"Closer","owns":"send buyer-specific proposals through an operable channel and record the sent event"},
 {"name":"Reply Watch","owns":"monitor replies to sent proposals and surface meaningful buyer responses immediately"},
 {"name":"Follow-up Captain","owns":"send one concise follow-up when appropriate and stop if the buyer declines or opts out"},
 {"name":"Order Intake","owns":"convert evidenced buyer acceptance into a scoped order and payment request"},
 {"name":"Delivery Pod","owns":"build the paid scope with the minimum specialists required"},
 {"name":"Acceptance QA","owns":"prove the deliverable meets agreed criteria before handoff"},
 {"name":"Cashkeeper","owns":"count only verified collected funds as revenue"},
]

MONEY_LANES=[
 {"id":"rescue","name":"Automation Rescue","price_min":49,"price_max":149,"target":"broken n8n/Make/Zapier/Python workflow","goal":"fastest first-dollar path"},
 {"id":"pilot","name":"Paid Automation Pilot","price_min":75,"price_max":199,"target":"one repetitive business process","goal":"prove value with narrow scope"},
 {"id":"data","name":"Data/Spreadsheet Automation","price_min":99,"price_max":500,"target":"Excel, Sheets, CSV, reporting, cleanup","goal":"simple measurable deliverable"},
 {"id":"crm","name":"CRM/Lead Workflow","price_min":199,"price_max":750,"target":"lead intake, qualification, routing, follow-up","goal":"revenue-linked automation"},
 {"id":"documents","name":"Document Robot","price_min":149,"price_max":750,"target":"PDF, invoice, form, document processing","goal":"remove repetitive admin"},
 {"id":"agency-overflow","name":"Agency Overflow Fulfillment","price_min":500,"price_max":2500,"target":"agencies with existing paying clients","goal":"borrow distribution instead of finding every end buyer"},
 {"id":"maintenance","name":"Automation Maintenance","price_min":99,"price_max":500,"target":"ongoing monitoring/fixes","goal":"recurring revenue"},
]

def contract():
 return {
  "team":TEAM,
  "money_lanes":MONEY_LANES,
  "scoreboard":["offers_sent","buyer_replies","accepted_orders","verified_collected_revenue"],
  "rules":[
   "No internal build counts as sales progress.",
   "Prefer explicit existing demand over speculative prospecting.",
   "Prefer hours-old demand and operable direct contact paths.",
   "Try a lawful public direct contact route before declaring a marketplace login blocker.",
   "Prefer a smaller paid trial that can be delivered quickly over a large vague proposal.",
   "Do not promise unverified capabilities.",
   "Follow up once when appropriate; respect declines and opt-outs.",
   "After each sale/rejection, feed the result back into offer selection and capability verification.",
  ],
 }

if __name__=="__main__":
 import json;print(json.dumps(contract(),indent=2))
