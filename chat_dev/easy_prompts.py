#!/usr/bin/env python3
"""Versioned Easy Prompts catalog for GOX ChatDev."""

CATALOG = {
    "check-gox": {
        "name": "Check GOX",
        "summary": "Inspect GOX health, services, queue, deployment and revenue state.",
        "permission": "read-only",
        "workflow": "ops.check",
        "requires_approval": False,
    },
    "fix-chatdev": {
        "name": "Fix ChatDev",
        "summary": "Diagnose ChatDev, apply safe reversible fixes, then retest.",
        "permission": "service-maintenance",
        "workflow": "ops.fix_chatdev",
        "requires_approval": False,
    },
    "deploy-chatdev": {
        "name": "Deploy ChatDev",
        "summary": "Deploy the approved release with health checks and rollback.",
        "permission": "release",
        "workflow": "release.deploy",
        "requires_approval": True,
    },
    "test-everything": {
        "name": "Test everything",
        "summary": "Run the full GOX release and persistence test suite.",
        "permission": "read-only",
        "workflow": "qa.full",
        "requires_approval": False,
    },
    "show-status": {
        "name": "Show me where we're at",
        "summary": "Generate the current GOX paper-stack truth status.",
        "permission": "read-only",
        "workflow": "ops.status",
        "requires_approval": False,
    },
    "find-money": {
        "name": "Find money GOX can do",
        "summary": "Find explicit demand and match only against verified GOX capabilities.",
        "permission": "external-read",
        "workflow": "revenue.find_demand",
        "requires_approval": False,
    },
    "run-500-engine": {
        "name": "Run the $500/day engine",
        "summary": "Prioritize legitimate actions most likely to increase verified collected revenue today.",
        "permission": "revenue-ops",
        "workflow": "revenue.daily",
        "requires_approval": False,
    },
}


def list_prompts():
    return [{"id": key, **value} for key, value in CATALOG.items()]


def resolve(prompt_id):
    return CATALOG.get(prompt_id)
