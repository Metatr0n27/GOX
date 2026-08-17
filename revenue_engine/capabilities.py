#!/usr/bin/env python3
"""Evidence-backed capability readiness catalog for revenue qualification."""
from demand_to_cash import Capability
from capability_evidence import read as read_evidence


def _evidence_capability(name, slug, hours, fallback):
    evidence=read_evidence(slug)
    verified=bool(evidence and evidence.get("verified"))
    if verified:
        checks=", ".join(evidence.get("checks",[]) or [])
        version=evidence.get("version") or "unknown"
        notes=f"Runtime evidence PASS; version={version}; checks={checks}"
    else:
        notes=fallback
    return Capability(name,verified,hours,notes)


def capability_catalog():
    # Runtime-backed capabilities are recomputed on every call so successful VPS
    # verification immediately changes qualification without another code deploy.
    return [
        Capability("automation workflow", True, 8.0, "GOX queue/worker/deploy automation tested on VPS"),
        Capability("python automation", True, 8.0, "Python services, persistence and tests verified on VPS"),
        Capability("api integration", False, 12.0, "Customer API integration not yet acceptance-tested end-to-end"),
        Capability("openai chatbot", False, 12.0, "Requires production adapter and acceptance-test evidence"),
        _evidence_capability("n8n automation","n8n-automation",8.0,"n8n runtime evidence has not passed or is stale"),
        Capability("spreadsheet automation", False, 6.0, "Not yet acceptance-tested as a customer deliverable"),
    ]


def verified_capabilities():
    return [c for c in capability_catalog() if c.verified]


def readiness():
    return [
        {"name": c.name, "verified": c.verified, "max_delivery_hours": c.max_delivery_hours, "evidence": c.notes}
        for c in capability_catalog()
    ]

# Backward-compatible snapshot for code that imports CAPABILITIES directly.
CAPABILITIES=capability_catalog()
