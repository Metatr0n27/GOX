from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

DEFAULT_FUNCTIONS = [
    "Paper Stack",
    "Easy Prompts",
    "Easy Jobs",
    "Money Runner",
    "Idea Vault",
    "Verification & Completion",
    "Approval Preflight",
    "Research/Testing/Improvement",
    "Money Meter",
    "Hourly MONEYMAKER Reporting",
    "Browser Team",
    "Recovery",
    "Family Routing",
    "Explain Mode",
]

@dataclass
class EasyAllPlan:
    objective: str
    functions: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)


def build_plan(objective: str, requested_functions: Iterable[str] | None = None) -> EasyAllPlan:
    funcs = list(dict.fromkeys(requested_functions or DEFAULT_FUNCTIONS))
    rules = [
        "Use current source-of-truth state before acting.",
        "Prioritize verified dollars collected per owner-hour and time-to-cash for money objectives.",
        "Run safe/reversible machine-doable work automatically.",
        "Route only genuine owner gates: login, MFA, CAPTCHA, KYC, personal answers/recordings, legal attestations, final owner-only submit, payment authorization.",
        "Never claim applied, submitted, accepted, completed, paid, connected, or deployed without exact evidence.",
        "When a blocker appears, invoke Easy Prompts to generate the correct specialist repair team, test, repair, retest, and resume.",
        "After every material result, update evidence, Money Meter, Paper Stack continuity, and next action.",
        "Do not spend user money without prior spending notification and required authorization.",
        "Do not let documentation or architecture work block a ready-to-run revenue lane.",
    ]
    return EasyAllPlan(objective=objective, functions=funcs, rules=rules)


def launch_money_now() -> EasyAllPlan:
    return build_plan("Make legitimate money as soon as possible, then continuously maximize verified dollars collected per owner-hour.")
