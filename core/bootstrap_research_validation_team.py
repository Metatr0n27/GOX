#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from core.runner_contract import WorkContract, ensure_runner_schema, list_active, upsert_contract
from core.tedium_absorber import connect


RESEARCH_OBJECTIVE = (
    'Independently validate GOX architecture, three-lane owner model, durable agent runtime, '
    'cost strategy, and revenue-loop design. Challenge prior advice, compare alternatives, '
    'cite primary evidence, and produce bounded experiments before adoption.'
)


def contracts() -> list[WorkContract]:
    common = {
        'lane': 'research_validation',
        'status': 'queued',
        'allowed_side_effects': [],
        'owner_minute_budget': 0.0,
        'compute_budget_cents': 0,
        'retry_limit': 2,
        'evidence_required': [
            'dated source provenance',
            'contradictory evidence or explicit none found',
            'confidence level',
            'bounded recommendation',
        ],
    }
    specs = [
        ('architecture-scout', 'architecture_scout', 'Compare durable orchestration patterns for GOX: native Python/SQLite/systemd, LangGraph, Agentspan/Conductor, Temporal-style workflows, and other credible alternatives.'),
        ('repo-forensics', 'repo_forensics', 'Inspect candidate GitHub repositories for actual mechanisms, license, maintenance, tests, security surface, and copy/adapt candidates. Do not score stars as evidence.'),
        ('three-lane-analyst', 'operations_design', 'Test whether Find Money / Do the Work / Prove & Improve is the best owner-facing abstraction versus two-lane, four-lane, pods, or state-machine-only organization.'),
        ('cost-funding-scout', 'cost_funding', 'Research model/token/compute costs, free tiers, local inference, included infrastructure, credits, spending caps, and ways to avoid owner cash while preserving reliability. Never assume free credits are durable funding.'),
        ('reliability-scout', 'reliability', 'Enumerate race conditions, stale state, orphaned work, retries, dead letters, crash recovery, rate limits, source outages, and duplicate consequential actions; define required controls.'),
        ('rules-identity-scout', 'rules_identity', 'Identify automation, assistance, identity, confidentiality, credential, account-sharing, payment, tax, MFA/CAPTCHA, and owner-gate boundaries for each candidate revenue source.'),
        ('economics-analyst', 'economics', 'Normalize alternatives by verified net dollars, owner minutes, compute/tool cost, payout probability, time-to-cash, repeatability, rejection risk, and automation share.'),
        ('experiment-designer', 'experiment_designer', 'Design falsifiable crash/recovery, fan-out/fan-in, owner-pause, duplicate-submit, source-outage, and economics experiments using the same acceptance criteria across candidate runtimes.'),
        ('verifier-a', 'independent_verifier', 'Independently reproduce the strongest architecture and cost claims using primary sources or code; do not rely on scout summaries.'),
        ('skeptic-red-team', 'skeptic', 'Try to disprove the preferred architecture, lane model, zero-cash strategy, and revenue assumptions. Search for hidden costs and failure cases.'),
        ('evidence-judge', 'evidence_judge', 'Grade claims E0 assertion, E1 documented mechanism, E2 independently verified, E3 bounded experiment, E4 real external revenue/owner-time evidence. Reject overclaims.'),
        ('synthesis-supervisor', 'research_supervisor', 'Synthesize only claims that survive verification and skepticism into a ranked recommendation, explicit uncertainties, and next experiment. Optimize verified net dollars per owner-hour.'),
    ]
    out: list[WorkContract] = []
    for cid, role, objective in specs:
        out.append(WorkContract(
            id=f'research:{cid}',
            objective=f'{RESEARCH_OBJECTIVE} Role objective: {objective}',
            runner_role=role,
            allowed_tools=['web_read', 'github_read', 'repo_static_analysis'],
            acceptance_criteria=[
                'compare at least three viable options where possible',
                'separate fact, inference, estimate, assumption, and recommendation',
                'record what evidence would change the recommendation',
                'no paid external action without an explicit budget approval',
            ],
            source_refs=[
                'assafelovic/gpt-researcher',
                'langchain-ai/langgraph',
                'agentspan-ai/agentspan',
                'microsoft/autogen',
                'stanford-oval/storm',
                'OpenHands/OpenHands',
            ],
            idempotency_key=f'research-validation:{cid}:v1',
            **common,
        ))
    return out


def bootstrap(db_path: Path | None = None) -> dict:
    db = connect(db_path) if db_path else connect()
    try:
        ensure_runner_schema(db)
        for contract in contracts():
            upsert_contract(db, contract)
        active = list_active(db)
        return {
            'status': 'bootstrapped',
            'team': 'GOX Research Validation Team',
            'contracts': len(contracts()),
            'active': [x['id'] for x in active if x['lane'] == 'research_validation'],
            'budget_policy': 'zero external model spend until explicitly approved',
        }
    finally:
        db.close()


if __name__ == '__main__':
    print(json.dumps(bootstrap(), indent=2, sort_keys=True))
