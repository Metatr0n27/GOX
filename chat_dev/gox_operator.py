#!/usr/bin/env python3
"""Single-front-door GOX Operator policy.

The GOX Operator owns the end-to-end loop and delegates to specialist workers.
It continues automatically through safe, reversible work and only escalates true
human-gated actions.
"""
from __future__ import annotations

TEAM = [
    {"name":"Gap Auditor","owns":"find highest-value missing/failed requirement"},
    {"name":"Builder","owns":"implement safe reversible fixes and capabilities"},
    {"name":"Verifier","owns":"run deterministic and end-to-end tests; reject false green states"},
    {"name":"Release Captain","owns":"promote only tested changes and verify production deployment"},
    {"name":"Buyer Request Scout","owns":"find only people already asking for work"},
    {"name":"Closer","owns":"qualify, price, and prepare truthful buyer-specific responses"},
    {"name":"Checkout Ops","owns":"maintain public buy offers, checkout links, purchase intake, and checkout health"},
    {"name":"Payment Reconciler","owns":"verify payment events against orders and update collected-revenue evidence"},
    {"name":"Delivery Captain","owns":"fulfill won work and preserve evidence"},
    {"name":"Acceptance QA","owns":"test customer acceptance criteria before delivery"},
    {"name":"Cashkeeper","owns":"verify collected payment and revenue milestones"},
    {"name":"Owner Proxy","owns":"apply standing owner priorities and suppress unnecessary interruptions"},
]

PRIORITY = [
    "verified collected revenue",
    "working public checkout and payment intake",
    "explicit buyer requests already asking for work",
    "close/submission readiness",
    "verified capability expansion driven by missed demand",
    "fulfillment and QA reliability",
    "deployment/runtime reliability",
    "visibility and owner workload reduction",
]

HUMAN_ONLY = {
    "open_or_verify_payment_processor_account",
    "link_bank_or_payout_account",
    "personal_marketplace_login",
    "accept_terms_or_contract",
    "enter_or_reveal_private_credentials",
    "authorize_spend_or_payment",
    "irreversible_external_commitment",
    "final_owner_acceptance_when_required",
}


def should_escalate(action: str) -> bool:
    return action in HUMAN_ONLY


def operator_contract() -> dict:
    return {
        "mode": "CONTINUE_UNTIL_HUMAN_GATE",
        "team": TEAM,
        "priority": PRIORITY,
        "rules": [
            "Do not stop after fixing one gap; re-audit.",
            "BUILT is not DEPLOYED; DEPLOYED is not TESTED; TESTED is not VERIFIED.",
            "Only explicit existing buyer demand enters revenue flow.",
            "Do not sell unverified capabilities.",
            "Only collected payment counts as revenue.",
            "Checkout Ops must automatically wire and test any configured hosted checkout URL.",
            "Payment Reconciler must reject unverified payment claims.",
            "Interrupt owner only for HUMAN_ONLY actions or a genuine blocker.",
        ],
    }
