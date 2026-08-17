#!/usr/bin/env python3
"""Public GOX sales and payment-readiness surface.

GOX delegates card entry to a hosted payment processor and never stores card data.
Public policy pages are intentionally factual and avoid inventing business contact
information or financial commitments that have not been configured by the owner.
"""
from __future__ import annotations
import html, json, os

DEFAULT_OFFERS=[
 {"id":"quick-fix","name":"Automation Quick Fix","price":25,"description":"Fix or adjust one small automation/workflow issue. Fast scope, tested delivery."},
 {"id":"workflow-sprint","name":"Workflow Sprint","price":99,"description":"Build or repair one focused automation workflow with acceptance testing."},
 {"id":"automation-build","name":"Automation Build","price":249,"description":"A larger end-to-end automation build with documented handoff and QA."},
]

def business_name(): return os.getenv("GOX_BUSINESS_NAME","GOX").strip() or "GOX"
def support_email(): return os.getenv("GOX_SUPPORT_EMAIL","").strip()
def checkout_url(offer_id:str)->str:
 specific=os.getenv(f"GOX_CHECKOUT_URL_{offer_id.upper().replace('-','_')}","").strip()
 return specific or os.getenv("GOX_CHECKOUT_URL","").strip()
def offers():
 raw=os.getenv("GOX_PUBLIC_OFFERS_JSON","").strip()
 if raw:
  try:
   parsed=json.loads(raw)
   if isinstance(parsed,list) and parsed:return parsed
  except Exception:pass
 return DEFAULT_OFFERS

def readiness()->dict:
 checkout=any(checkout_url(str(o.get("id","offer"))) for o in offers())
 contact=bool(support_email())
 missing=[]
 if not checkout: missing.append("hosted_checkout_url")
 if not contact: missing.append("public_support_email")
 return {"ready":not missing,"checkout_configured":checkout,"support_contact_configured":contact,"missing":missing}

def _shell(title:str,body:str)->bytes:
 nav='<nav><a href="/buy">Buy</a> · <a href="/about">About</a> · <a href="/contact">Contact</a> · <a href="/privacy">Privacy</a> · <a href="/terms">Terms</a> · <a href="/refunds">Refunds</a></nav>'
 return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>:root{{font-family:system-ui;color-scheme:dark}}body{{margin:0;background:#07111f;color:#eef6ff}}main{{max-width:900px;margin:auto;padding:42px 20px}}a{{color:#8fc5ff}}nav{{margin-bottom:28px;color:#789}}.card{{background:#0d1b2e;border:1px solid #29486f;border-radius:18px;padding:22px;margin:18px 0}}.muted{{color:#bdd2ee}}</style></head><body><main>{nav}{body}</main></body></html>'''.encode()

def render_buy_page()->bytes:
 cards=[]
 for offer in offers():
  oid=str(offer.get("id","offer")); name=html.escape(str(offer.get("name","GOX Service"))); desc=html.escape(str(offer.get("description",""))); price=float(offer.get("price",0) or 0); url=checkout_url(oid)
  action=f'<a class="buy" href="{html.escape(url,quote=True)}" rel="noopener">Buy now — ${price:.0f}</a>' if url else '<button class="buy disabled" disabled>Secure checkout being connected</button>'
  cards.append(f'<article class="offer"><h2>{name}</h2><div class="price">${price:.0f}</div><p>{desc}</p>{action}</article>')
 r=readiness(); note='Secure hosted checkout is connected.' if r["checkout_configured"] else 'Hosted checkout is being connected.'
 contact=f'<p>Questions: <a href="mailto:{html.escape(support_email(),quote=True)}">{html.escape(support_email())}</a></p>' if support_email() else ''
 body=f'''<h1>{html.escape(business_name())} Automation</h1><p class="muted">Focused automation implementation, repair, and workflow services. Scope is confirmed before work begins and delivery is acceptance-tested.</p><section class="offers">{''.join(cards)}</section><div class="card">{html.escape(note)} Card details are entered only on the hosted payment processor. {contact}<p><a href="/terms">Terms</a> · <a href="/refunds">Refund policy</a> · <a href="/privacy">Privacy</a></p></div><style>.offers{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px;margin-top:34px}}.offer{{background:#0d1b2e;border:1px solid #29486f;border-radius:18px;padding:22px}}.price{{font-size:2rem;font-weight:800;margin:10px 0}}.buy{{display:block;text-align:center;margin-top:20px;padding:14px;border-radius:12px;background:#4d9cff;color:white;text-decoration:none;border:0;font-weight:800;width:100%;box-sizing:border-box}}.disabled{{opacity:.5}}</style>'''
 return _shell(f"Buy {business_name()} Automation",body)

def render_public_page(path:str)->bytes|None:
 name=html.escape(business_name()); email=support_email(); contact=(f'<a href="mailto:{html.escape(email,quote=True)}">{html.escape(email)}</a>' if email else 'Support contact is being finalized before checkout activation.')
 pages={
  "/about":f'<h1>About {name}</h1><div class="card"><p>{name} provides focused automation implementation and repair services, including workflow automation and Python-based automation where capability has been verified.</p><p>Work is scoped before implementation and tested against agreed acceptance criteria before delivery.</p></div>',
  "/contact":f'<h1>Contact {name}</h1><div class="card"><p>Customer support: {contact}</p><p>Customers also receive payment and order records from the hosted payment processor used at checkout.</p></div>',
  "/privacy":f'<h1>Privacy</h1><div class="card"><p>{name} uses customer information only as needed to scope, deliver, support, and account for purchased services. Payment-card information is entered and processed by the hosted payment processor and is not stored by {name}.</p><p>Operational records may include customer contact information, order scope, delivery status, and payment confirmation identifiers needed for support and accounting.</p></div>',
  "/terms":f'<h1>Service terms</h1><div class="card"><p>{name} sells scoped automation services. The exact deliverable, price, expected turnaround, customer dependencies, and acceptance criteria are confirmed before work begins.</p><p>Customers must provide lawful access to any systems or credentials required for their project. {name} does not promise results outside the agreed technical scope.</p></div>',
  "/refunds":f'<h1>Refund and cancellation policy</h1><div class="card"><p>Any project-specific cancellation or refund terms are disclosed with the order scope before work begins. If {name} cannot deliver an agreed paid scope, the customer will be offered an appropriate correction, replacement scope, or refund for the undelivered portion as applicable.</p><p>For support about a purchase, contact {contact}</p></div>',
 }
 body=pages.get(path)
 return _shell(f"{business_name()} — {path.strip('/').title()}",body) if body else None
