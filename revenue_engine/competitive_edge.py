#!/usr/bin/env python3
"""GOX competitive advantage agent team.

These agents do not fabricate credentials or promise unsupported work. They improve
selection, positioning, proposal quality, delivery planning, QA, follow-up, and
learning from outcomes.
"""
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Agent:
    name: str
    mission: str
    outputs: tuple[str, ...]


AGENTS = (
    Agent("Buyer Researcher", "Extract the buyer's actual pain, urgency, constraints, decision criteria, and hidden risks.", ("buyer_summary", "urgency", "decision_criteria", "risks")),
    Agent("Win Strategist", "Choose the strongest truthful angle for winning this specific job instead of sending a generic pitch.", ("positioning", "differentiators", "proof_needed")),
    Agent("Scope Architect", "Turn vague requests into a small, testable delivery plan with clear acceptance criteria and boundaries.", ("scope", "acceptance_criteria", "exclusions", "milestones")),
    Agent("Pricing Strategist", "Price for expected value, speed, delivery risk, platform fees, and likelihood of same-day collection.", ("price", "floor", "rationale")),
    Agent("Proposal Editor", "Produce a concise buyer-specific proposal with no fake claims and a concrete first step.", ("proposal", "opening", "call_to_action")),
    Agent("Preflight QA", "Check that GOX has verified capability, dependencies, credentials, time, and rollback before work is accepted.", ("ready", "blockers", "dependencies")),
    Agent("Delivery Captain", "Sequence the fastest safe implementation path, preserve evidence, and keep the buyer updated at useful milestones.", ("execution_plan", "checkpoints", "evidence")),
    Agent("Acceptance QA", "Test against the buyer's stated success criteria and reject incomplete delivery.", ("test_plan", "results", "release_decision")),
    Agent("Client Success", "Create a clean handoff, ask for acceptance/payment, and identify legitimate follow-on work without spam.", ("handoff", "payment_next_step", "upsell_if_relevant")),
    Agent("Win-Loss Learner", "Capture why an opportunity was won, lost, delayed, refunded, or repeated and feed that back into scoring.", ("outcome", "lesson", "scoring_adjustment")),
)


def team_manifest():
    return [asdict(a) for a in AGENTS]


def competitive_preflight(opportunity: dict, verified_capabilities: set[str]) -> dict:
    capability = str(opportunity.get("capability", "")).strip()
    budget_max = float(opportunity.get("budget_max", 0) or 0)
    blockers = []
    if capability not in verified_capabilities:
        blockers.append("capability not verified")
    if not opportunity.get("source_url"):
        blockers.append("missing source evidence")
    if budget_max <= 0:
        blockers.append("no stated budget")
    proposal = opportunity.get("proposal") or {}
    if not str(proposal.get("message", "")).strip():
        blockers.append("proposal missing")
    return {
        "ready": not blockers,
        "blockers": blockers,
        "advantage_checks": {
            "buyer_specific": True,
            "verified_delivery_only": capability in verified_capabilities,
            "acceptance_criteria_required": True,
            "qa_required": True,
            "payment_followup_required": True,
            "win_loss_learning_required": True,
        },
    }
