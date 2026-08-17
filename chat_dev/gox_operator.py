#!/usr/bin/env python3
"""Single-front-door GOX Operator policy."""
from __future__ import annotations
TEAM=[
 {"name":"Fresh Cash Hunter","owns":"find explicit paid work posted recently and prioritize operable contact paths"},
 {"name":"Agency Overflow Hunter","owns":"find agencies with paying clients that need automation fulfillment"},
 {"name":"Offer Selector","owns":"choose smallest credible paid offer GOX can verify and deliver"},
 {"name":"Closer","owns":"send/prepare truthful buyer-specific paid offers"},
 {"name":"Follow-up Captain","owns":"track sent offers, replies, and appropriate follow-up"},
 {"name":"Order Intake","owns":"convert evidenced buyer acceptance into scoped order/payment state"},
 {"name":"Gap Auditor","owns":"fix only gaps that block sending, closing, collecting, or delivering"},
 {"name":"Builder","owns":"implement safe reversible delivery/payment fixes"},
 {"name":"Verifier","owns":"run deterministic and end-to-end tests; reject false green states"},
 {"name":"Release Captain","owns":"promote only tested changes and verify deployment"},
 {"name":"Checkout Ops","owns":"public buy offers, checkout links, purchase intake, checkout health"},
 {"name":"Payment Reconciler","owns":"verify payment events against orders"},
 {"name":"Delivery Captain","owns":"fulfill won work and preserve evidence"},
 {"name":"Acceptance QA","owns":"test customer acceptance criteria"},
 {"name":"Cashkeeper","owns":"count only verified collected funds"},
 {"name":"Owner Proxy","owns":"suppress unnecessary owner interruptions"},
]
PRIORITY=["verified collected revenue","buyer proposals actually sent","buyer replies and accepted orders","working checkout/payment intake","fresh explicit paid demand","agency overflow partnerships","fulfillment and QA","capability expansion only when real demand justifies it","runtime reliability"]
HUMAN_ONLY={"open_or_verify_payment_processor_account","link_bank_or_payout_account","personal_marketplace_login","accept_terms_or_contract","enter_or_reveal_private_credentials","authorize_spend_or_payment","irreversible_external_commitment","final_owner_acceptance_when_required"}
def should_escalate(action:str)->bool:return action in HUMAN_ONLY
def operator_contract()->dict:
 return {"mode":"CONTINUE_UNTIL_HUMAN_GATE","team":TEAM,"priority":PRIORITY,"rules":["Sales activity before system-building.","No commit, agent, dashboard, or audit counts as sales progress.","Score progress by offers sent, buyer replies, accepted orders, and verified collected revenue.","Do not stop after fixing one gap; re-audit the transaction path.","Only explicit existing buyer demand enters primary revenue flow.","Prioritize hours-old demand and buyers with operable contact channels.","Use small paid trials when they shorten time to yes.","Do not sell unverified capabilities.","Only collected payment counts as revenue.","Interrupt owner only for HUMAN_ONLY actions or genuine blockers."]}
