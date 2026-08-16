#!/usr/bin/env python3
"""GOX demand-to-cash pipeline core.

Keeps demand intake, qualification, proposal generation, fulfillment routing,
QA state, and payment verification explicit and auditable.
"""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Opportunity:
    source: str
    external_id: str
    title: str
    description: str
    budget_min: float
    budget_max: float
    currency: str = "USD"
    explicit_demand: bool = True
    source_url: Optional[str] = None


@dataclass
class Capability:
    name: str
    verified: bool
    max_delivery_hours: float
    notes: str = ""


@dataclass
class Qualification:
    accepted: bool
    score: float
    reason: str
    capability: Optional[str] = None


def qualify(opportunity: Opportunity, capabilities: list[Capability]) -> Qualification:
    if not opportunity.explicit_demand:
        return Qualification(False, 0.0, "not explicit buyer demand")
    text = f"{opportunity.title} {opportunity.description}".lower()
    matches = []
    for cap in capabilities:
        if not cap.verified:
            continue
        tokens = [t for t in cap.name.lower().replace('-', ' ').split() if len(t) > 2]
        overlap = sum(1 for t in tokens if t in text)
        if overlap:
            matches.append((overlap, cap))
    if not matches:
        return Qualification(False, 0.0, "no verified GOX capability match")
    matches.sort(key=lambda x: (-x[0], x[1].max_delivery_hours))
    cap = matches[0][1]
    midpoint = max(0.0, (opportunity.budget_min + opportunity.budget_max) / 2.0)
    speed_bonus = max(0.0, 24.0 - cap.max_delivery_hours) / 24.0
    score = round(midpoint * (1.0 + 0.25 * speed_bonus), 2)
    return Qualification(True, score, "verified capability match", cap.name)


def draft_proposal(opportunity: Opportunity, qualification: Qualification) -> dict:
    if not qualification.accepted:
        raise ValueError("cannot draft proposal for rejected opportunity")
    midpoint = (opportunity.budget_min + opportunity.budget_max) / 2.0
    price = max(opportunity.budget_min, min(opportunity.budget_max, midpoint))
    return {
        "title": opportunity.title,
        "capability": qualification.capability,
        "proposed_price": round(price, 2),
        "currency": opportunity.currency,
        "message": (
            f"I can handle this using a tested {qualification.capability} workflow. "
            "I would start by confirming the inputs and success criteria, build the smallest working version, "
            "test the full flow, and deliver with a short handoff note."
        ),
        "requires_owner_submission": True,
    }


def fulfillment_job(opportunity: Opportunity, qualification: Qualification) -> dict:
    if not qualification.accepted:
        raise ValueError("rejected opportunity cannot be fulfilled")
    return {
        "kind": "revenue-fulfillment",
        "source": opportunity.source,
        "external_id": opportunity.external_id,
        "capability": qualification.capability,
        "status": "blocked_until_won",
        "qa_required": True,
        "payment_required_before_revenue_count": True,
    }


def collected_revenue(payment_status: str, gross_amount: float, fees: float = 0.0, refunds: float = 0.0) -> float:
    if payment_status.lower() != "collected":
        return 0.0
    return round(max(0.0, gross_amount - fees - refunds), 2)


def serialize(obj):
    return asdict(obj)
