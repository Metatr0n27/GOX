#!/usr/bin/env python3
"""Build a minimal owner handoff bundle for proposal submission."""
from __future__ import annotations


def build_submission_pack(item: dict) -> dict:
    proposal = item.get("proposal") or {}
    message = str(proposal.get("message", "")).strip()
    source_url = item.get("source_url")
    blockers = []
    if not source_url:
        blockers.append("missing source URL")
    if not message:
        blockers.append("proposal missing")
    if item.get("state") != "PROPOSAL_READY":
        blockers.append("opportunity not proposal-ready")
    budget_max = float(item.get("budget_max", 0) or 0)
    if budget_max <= 0:
        blockers.append("no stated budget")
    return {
        "opportunity_id": item.get("id"),
        "ready": not blockers,
        "blockers": blockers,
        "source_url": source_url,
        "title": item.get("title"),
        "budget_min": item.get("budget_min", 0),
        "budget_max": item.get("budget_max", 0),
        "currency": item.get("currency", "USD"),
        "capability": item.get("capability"),
        "proposal_text": message,
        "owner_action": "Open source, paste proposal, review marketplace terms, submit from your own account.",
    }


def build_all(queue_payload: dict) -> list[dict]:
    packs = [build_submission_pack(item) for item in queue_payload.get("items", [])]
    return [p for p in packs if p["ready"]]
