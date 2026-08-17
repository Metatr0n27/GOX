#!/usr/bin/env python3
"""GOX Owner-Proxy Verifier.

Acts as a bounded internal reviewer using standing GOX priorities. It does not
impersonate the owner, accept marketplace terms, spend money, or make irreversible
external commitments. Those remain human-gated.
"""
from __future__ import annotations

OWNER_RULES = {
    "daily_cash_target": 500.0,
    "prefer_same_day_cash": True,
    "require_verified_capability": True,
    "require_source_evidence": True,
    "require_test_before_delivery": True,
    "count_only_collected_revenue": True,
    "avoid_repetitive_owner_busywork": True,
}

HUMAN_REQUIRED = {
    "submit_from_personal_marketplace_account",
    "accept_marketplace_terms",
    "enter_or_reveal_credentials",
    "authorize_payment_or_spend",
    "irreversible_external_commitment",
}


def verify_opportunity(item: dict, competitive_preflight: dict | None = None) -> dict:
    blockers=[]
    warnings=[]
    if item.get("state") != "PROPOSAL_READY": blockers.append("not proposal-ready")
    if not item.get("source_url"): blockers.append("missing buyer/source evidence")
    if float(item.get("budget_max",0) or 0) <= 0: blockers.append("no stated budget")
    if not item.get("capability"): blockers.append("no capability match")
    proposal=item.get("proposal") or {}
    if not str(proposal.get("message","")).strip(): blockers.append("proposal missing")
    if competitive_preflight and not competitive_preflight.get("ready",False):
        blockers.extend(competitive_preflight.get("blockers",[]))
    budget=float(item.get("budget_max",0) or 0)
    score=float(item.get("score",0) or 0)
    if budget < 100: warnings.append("low-value opportunity; pursue only if extremely fast or strategic")
    if score <= 0: warnings.append("no positive opportunity score")
    verdict="READY_FOR_OWNER_SUBMIT" if not blockers else "KEEP_WORKING"
    owner_action=("Open the buyer page, review the prepared proposal, and submit from your own account."
                  if verdict=="READY_FOR_OWNER_SUBMIT" else "None yet; agents should resolve blockers first.")
    return {
        "verdict": verdict,
        "blockers": sorted(set(blockers)),
        "warnings": warnings,
        "owner_action": owner_action,
        "human_required": ["submit_from_personal_marketplace_account"] if verdict=="READY_FOR_OWNER_SUBMIT" else [],
        "rules_applied": OWNER_RULES,
    }


def verify_delivery(delivery: dict) -> dict:
    blockers=[]
    if not delivery.get("acceptance_criteria"): blockers.append("acceptance criteria missing")
    if not delivery.get("test_evidence"): blockers.append("test evidence missing")
    if delivery.get("tests_passed") is not True: blockers.append("tests not passed")
    if delivery.get("known_failures"): blockers.append("known failures remain")
    return {
        "verdict":"READY_TO_DELIVER" if not blockers else "KEEP_WORKING",
        "blockers":blockers,
        "owner_action":"Final hands-on acceptance test" if not blockers else "None yet",
    }
