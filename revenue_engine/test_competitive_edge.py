#!/usr/bin/env python3
from competitive_edge import AGENTS, competitive_preflight

assert len(AGENTS) >= 8
opp={"capability":"automation workflow","budget_max":750,"source_url":"https://example.test/job","proposal":{"message":"I can deliver this."}}
r=competitive_preflight(opp,{"automation workflow"})
assert r["ready"] is True and not r["blockers"]
bad=competitive_preflight({"capability":"unverified","budget_max":0,"proposal":{}},{"automation workflow"})
assert bad["ready"] is False
assert "capability not verified" in bad["blockers"]
assert "missing source evidence" in bad["blockers"]
assert "no stated budget" in bad["blockers"]
print("PASS: competitive advantage team preflight")
