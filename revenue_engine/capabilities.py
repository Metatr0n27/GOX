#!/usr/bin/env python3
"""Evidence-backed capability readiness catalog for revenue qualification."""
from demand_to_cash import Capability

# A capability is only verified when we have concrete test/runtime evidence for the
# underlying class of work. Keep this conservative; unverified skills must not be sold.
CAPABILITIES = [
    Capability("automation workflow", True, 8.0, "GOX queue/worker/deploy automation tested on VPS"),
    Capability("python automation", True, 8.0, "Python services, persistence and tests verified on VPS"),
    Capability("api integration", False, 12.0, "Adapter contract exists; customer API integration not yet acceptance-tested"),
    Capability("openai chatbot", False, 12.0, "Requires working customer/API credentials and production adapter validation"),
    Capability("n8n automation", False, 8.0, "Not yet verified in current GOX production environment"),
    Capability("spreadsheet automation", False, 6.0, "Not yet acceptance-tested as a customer deliverable"),
]


def verified_capabilities():
    return [c for c in CAPABILITIES if c.verified]


def readiness():
    return [
        {"name": c.name, "verified": c.verified, "max_delivery_hours": c.max_delivery_hours, "evidence": c.notes}
        for c in CAPABILITIES
    ]
