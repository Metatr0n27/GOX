from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable

BOTTLENECKS = (
    "NO_OPPORTUNITIES",
    "LOW_QUALIFICATION",
    "LOW_AVAILABILITY",
    "LOW_PAY_RATE",
    "HIGH_OWNER_TIME",
    "SLOW_PAYOUT",
    "ACCESS_BLOCKER",
    "EXECUTION_FAILURE",
    "SUBMISSION_FAILURE",
    "LOW_ACCEPTANCE",
    "PAYMENT_FAILURE",
    "FORECAST_UNCERTAIN",
)

TEAM_MAP = {
    "NO_OPPORTUNITIES": ["Paid Opportunity Research Swarm", "Revenue Gap Research Swarm", "Profit Controller"],
    "LOW_QUALIFICATION": ["Fit Agent", "Eligibility/Policy Agent", "Profile Evidence Agent"],
    "LOW_AVAILABILITY": ["Opportunity Radar", "Notification/Timing Agent", "Platform Diversification Agent"],
    "LOW_PAY_RATE": ["Money Judge", "High-Value Opportunity Scout", "Pricing Agent"],
    "HIGH_OWNER_TIME": ["Automation Dev", "Browser Team", "Owner-Gate Minimizer"],
    "SLOW_PAYOUT": ["Payout-Speed Cell", "Cashout Optimizer", "Money Judge"],
    "ACCESS_BLOCKER": ["Authenticity Team", "Browser Team", "Gap Closer"],
    "EXECUTION_FAILURE": ["Recovery Agent", "Automation Dev", "Tester/Judge"],
    "SUBMISSION_FAILURE": ["Application/Offer Agent", "Browser Team", "Evidence Agent"],
    "LOW_ACCEPTANCE": ["Application/Offer Agent", "Challenger", "Experiment Agent"],
    "PAYMENT_FAILURE": ["Cashkeeper", "Payout Agent", "Evidence Agent"],
    "FORECAST_UNCERTAIN": ["Metrics Agent", "Baseline Keeper", "Experiment Agent"],
}

@dataclass
class Metrics:
    actionable_opportunities: int = 0
    qualification_rate: float = 1.0
    availability_rate: float = 1.0
    productive_dollars_per_hour: float = 0.0
    owner_minutes_per_paid_hour: float = 0.0
    payout_delay_hours: float = 0.0
    access_failures: int = 0
    execution_failures: int = 0
    submission_failures: int = 0
    acceptance_rate: float = 1.0
    payment_failures: int = 0
    verified_samples: int = 0

@dataclass
class RepairPrompt:
    bottleneck: str
    impact: str
    team: list[str]
    prompt: str
    acceptance_tests: list[str]
    promotion_rule: str


def detect_bottleneck(m: Metrics) -> str:
    if m.actionable_opportunities <= 0:
        return "NO_OPPORTUNITIES"
    if m.access_failures > 0:
        return "ACCESS_BLOCKER"
    if m.execution_failures > 0:
        return "EXECUTION_FAILURE"
    if m.submission_failures > 0:
        return "SUBMISSION_FAILURE"
    if m.payment_failures > 0:
        return "PAYMENT_FAILURE"
    if m.qualification_rate < 0.35:
        return "LOW_QUALIFICATION"
    if m.availability_rate < 0.45:
        return "LOW_AVAILABILITY"
    if m.productive_dollars_per_hour < 20:
        return "LOW_PAY_RATE"
    if m.owner_minutes_per_paid_hour > 15:
        return "HIGH_OWNER_TIME"
    if m.payout_delay_hours > 72:
        return "SLOW_PAYOUT"
    if m.acceptance_rate < 0.40:
        return "LOW_ACCEPTANCE"
    if m.verified_samples < 10:
        return "FORECAST_UNCERTAIN"
    return "FORECAST_UNCERTAIN"


def build_repair_prompt(m: Metrics, objective: str = "maximize verified dollars collected per owner-hour") -> RepairPrompt:
    b = detect_bottleneck(m)
    team = TEAM_MAP[b]
    snapshot = asdict(m)
    tests = [
        "Measure the same bottleneck metric before and after the repair.",
        "Do not promote a change unless evidence shows improvement or a necessary capability was restored.",
        "Rerun the affected workflow end-to-end and verify the external result where applicable.",
        "Preserve the previous known-good method for rollback.",
        "Do not claim submission, acceptance, completion, payment, connection, or deployment without evidence.",
    ]
    prompt = (
        f"GOX EASY PROMPT - REVENUE REPAIR\n"
        f"Objective: {objective}.\n"
        f"Detected bottleneck: {b}.\n"
        f"Current evidence snapshot: {snapshot}.\n"
        f"Assigned specialist team: {', '.join(team)}.\n"
        "Diagnose the root cause, not just the symptom. Generate the smallest complete repair plan. "
        "Execute every authorized machine-actionable step available to GOX. Build any missing reusable tool, adapter, test, or prompt required. "
        "If an external owner gate is truly unavoidable, preserve state and request exactly one minimal owner action. "
        "Then retest, compare against baseline, and either promote the repair or generate the next Easy Prompt for the remaining bottleneck. "
        "Continue recursively until the metric improves, a stronger bottleneck becomes dominant, or a genuine external blocker remains. "
        "Never optimize advertised pay alone; optimize verified dollars collected per elapsed owner-hour and time-to-cash."
    )
    return RepairPrompt(
        bottleneck=b,
        impact=f"Primary limiter for {objective}",
        team=team,
        prompt=prompt,
        acceptance_tests=tests,
        promotion_rule="Promote only with verified improvement versus baseline; otherwise repair again or roll back.",
    )


def choose_next(m: Metrics, previous_bottlenecks: Iterable[str] = ()) -> RepairPrompt:
    result = build_repair_prompt(m)
    if result.bottleneck in set(previous_bottlenecks):
        result.prompt += "\nThis bottleneck has repeated: require a root-cause analysis and a materially different repair hypothesis before retrying."
    return result
