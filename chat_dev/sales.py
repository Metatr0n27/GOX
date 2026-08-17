#!/usr/bin/env python3
"""Public GOX sales surface.

Payment processing is intentionally delegated to a configured hosted checkout URL
(Stripe Payment Link, PayPal, Square, etc.). GOX never stores card data.
"""
from __future__ import annotations
import html, json, os

DEFAULT_OFFERS = [
    {"id":"quick-fix","name":"Automation Quick Fix","price":25,"description":"Fix or adjust one small automation/workflow issue. Fast scope, tested delivery."},
    {"id":"workflow-sprint","name":"Workflow Sprint","price":99,"description":"Build or repair one focused automation workflow with acceptance testing."},
    {"id":"automation-build","name":"Automation Build","price":249,"description":"A larger end-to-end automation build with documented handoff and QA."},
]

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

def render_buy_page()->bytes:
    cards=[]
    for offer in offers():
        oid=str(offer.get("id","offer")); name=html.escape(str(offer.get("name","GOX Service"))); desc=html.escape(str(offer.get("description",""))); price=float(offer.get("price",0) or 0); url=checkout_url(oid)
        if url:
            action=f'<a class="buy" href="{html.escape(url,quote=True)}" rel="noopener">Buy now — ${price:.0f}</a>'
        else:
            action='<button class="buy disabled" disabled>Checkout being connected</button>'
        cards.append(f'<article class="offer"><h2>{name}</h2><div class="price">${price:.0f}</div><p>{desc}</p>{action}</article>')
    configured=any(checkout_url(str(o.get("id","offer"))) for o in offers())
    note='Secure hosted checkout is connected.' if configured else 'Payment processor connection is the only remaining checkout gate.'
    page=f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Buy GOX Automation</title><style>:root{{font-family:system-ui;color-scheme:dark}}body{{margin:0;background:#07111f;color:#eef6ff}}main{{max-width:960px;margin:auto;padding:48px 20px}}h1{{font-size:clamp(2rem,7vw,4rem);margin-bottom:8px}}.sub{{font-size:1.2rem;color:#bdd2ee;max-width:700px}}.offers{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px;margin-top:34px}}.offer{{background:#0d1b2e;border:1px solid #29486f;border-radius:18px;padding:22px}}.price{{font-size:2rem;font-weight:800;margin:10px 0}}.buy{{display:block;text-align:center;margin-top:20px;padding:14px;border-radius:12px;background:#4d9cff;color:white;text-decoration:none;border:0;font-weight:800;width:100%;box-sizing:border-box}}.disabled{{opacity:.5}}.proof{{margin-top:28px;padding:16px;border:1px solid #29486f;border-radius:14px;color:#bdd2ee}}</style></head><body><main><h1>GOX Automation</h1><p class="sub">Buy a focused automation job. We scope it tightly, test it, and deliver working evidence instead of vague promises.</p><section class="offers">{''.join(cards)}</section><div class="proof">{html.escape(note)} GOX does not store card details.</div></main></body></html>'''
    return page.encode()
