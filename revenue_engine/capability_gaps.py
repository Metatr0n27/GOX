#!/usr/bin/env python3
"""Prioritize missing capabilities from explicit buyer requests.

The goal is to turn rejected real demand into an evidence-backed expansion queue,
not to add random tools because they are popular.
"""
from __future__ import annotations
from collections import Counter, defaultdict

KEYWORDS = {
    "n8n automation": ("n8n", "workflow automation", "webhook automation"),
    "api integration": ("api integration", "rest api", "webhook", "oauth"),
    "openai chatbot": ("openai", "chatbot", "ai agent", "llm"),
    "spreadsheet automation": ("google sheets", "spreadsheet", "excel automation"),
    "crm automation": ("crm", "hubspot", "salesforce", "lead follow-up"),
    "email automation": ("email automation", "gmail automation", "email follow-up"),
    "data cleanup": ("data cleanup", "data cleaning", "deduplicate", "csv cleanup"),
}


def infer_missing_capabilities(opportunities: list[dict], verified: set[str]) -> list[dict]:
    counts = Counter(); budget = defaultdict(float); examples = defaultdict(list)
    for item in opportunities:
        text = f"{item.get('title','')} {item.get('description','')}".lower()
        for capability, terms in KEYWORDS.items():
            if capability in verified:
                continue
            if any(term in text for term in terms):
                counts[capability] += 1
                budget[capability] += float(item.get('budget_max',0) or 0)
                if len(examples[capability]) < 3:
                    examples[capability].append(item.get('title'))
    rows=[]
    for capability, demand_count in counts.items():
        avg_budget = budget[capability] / demand_count if demand_count else 0.0
        score = round(demand_count * 100 + avg_budget, 2)
        rows.append({
            "capability": capability,
            "explicit_request_count": demand_count,
            "average_stated_budget": round(avg_budget,2),
            "priority_score": score,
            "examples": examples[capability],
            "state": "NEEDS_VERIFICATION",
            "verification_gate": [
                "install/configure safely",
                "build representative workflow",
                "run deterministic tests",
                "run end-to-end acceptance test",
                "document rollback and limits",
                "only then mark capability verified",
            ],
        })
    rows.sort(key=lambda x:x["priority_score"], reverse=True)
    return rows


def top_gap(opportunities:list[dict], verified:set[str]):
    rows=infer_missing_capabilities(opportunities,verified)
    return rows[0] if rows else None
