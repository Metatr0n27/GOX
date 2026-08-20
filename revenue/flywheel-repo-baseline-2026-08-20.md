# GOX Flywheel Repo Baseline — 2026-08-20

## Purpose
Start the GitHub Flywheel Research Team with a realistic first comparison focused on the two flywheels closest to money: opportunity acquisition and settlement/evidence.

## Baseline candidates

### 1. NSPG13/agent-bounties
Target flywheels: Opportunity, Revenue, Settlement/Evidence, Agent-Orchestration.

Observed mechanisms:
- ready-to-earn funded opportunity inventory
- explicit claim -> solve -> submit -> verify -> confirm-payment lifecycle
- deterministic verifier/readiness gates
- canonical settlement event required before calling work paid
- solver economics requirement for posted work
- stream-first opportunity feed with polling fallback
- explicit separation between offers/submissions/verification and actual payment

GOX action: **ADAPT_PATTERN**.

Why:
This is the strongest current reference for settlement truth and funded-work gating. GOX should copy the state-machine ideas, not assume the marketplace itself guarantees good hourly economics.

Evidence grade:
Architecture/payment mechanics: strong.
Profitability per owner-hour: not established from README alone.

### 2. moltlaunch/cashclaw
Target flywheels: Opportunity, Fulfillment, Learning, Pricing, Owner-Time.

Observed mechanisms:
- real-time work watch with REST fallback
- task evaluation before acceptance
- quote/decline/submit/message tool boundaries
- multi-turn execution loop with side effects isolated behind tools
- feedback -> searchable memory -> future-task context
- configurable pricing and automation toggles
- atomic persistent state
- background self-study when idle

GOX action: **ADAPT_PATTERN**.

Why:
CashClaw is a strong model for how one long-running process can watch, evaluate, execute, submit, learn, and recover without constant owner interaction. The main GOX value is the execution/learning architecture, not any unsupported income claim.

Evidence grade:
Architecture: strong.
Verified earnings per owner-hour: not established from README alone.

### 3. hidorado/dorado
Target flywheels: Opportunity, Application/Bid, Fulfillment, Reputation.

Observed mechanisms from public repo description:
- open agent protocol and SDK
- agent registration/list/bid workflow
- task delivery and public receipts
- example research, PR review, and MCP-test agents

GOX action: **STUDY_ONLY pending deeper repo inspection**.

Why:
Potentially useful as a standardized external opportunity adapter, but the marketplace itself is closed-source and we need stronger evidence on inventory, conversion, payout reliability, and rules before integration.

### 4. AtlasNexusTech/ai2work
Target flywheels: Opportunity, Fulfillment, Settlement.

Observed mechanisms from public repo description:
- GitHub bounty work
- escrowed stablecoin payment
- open-race or direct-hire modes
- CI-attested submission flow
- reputation identity layer

GOX action: **STUDY_ONLY pending deeper repo inspection**.

Why:
Interesting because GitHub issues/PRs are naturally machine-readable and objective CI can reduce subjective acceptance. Current public description reports limited resolved-mainnet history, so this is not yet enough to treat it as a proven high-dollar lane.

## Current objective ranking
1. **Agent Bounties — settlement/evidence pattern**
2. **CashClaw — continuous work/evaluate/execute/learn pattern**
3. **Dorado — external opportunity protocol candidate**
4. **AI2Work — GitHub/CI bounty candidate**

## Realistic GOX build decision
Do not clone a whole external economy into GOX. Build a hybrid:

LIVE OPPORTUNITY ADAPTERS
-> CashClaw-style watch/evaluate loop
-> GOX rules + zero-blocker filter
-> GOX dollars-per-owner-hour scorer
-> Agent-Bounties-style funded/readiness state
-> bounded fulfillment agents
-> QA/verifier
-> submit/deliver
-> canonical external acceptance/payment evidence
-> GOX revenue ledger
-> feedback/calibration loop

## First implementation targets
1. Add `funding_status`, `verification_status`, `settlement_status`, and `payment_evidence` to GOX opportunity/revenue state.
2. Add a real source-adapter interface so different opportunity feeds can plug into the Revenue Engine.
3. Add event-stream/poll fallback semantics for sources that support it.
4. Add a predicted-vs-actual economics calibration record.
5. Keep owner actions isolated to genuine gates.

## Critical realism rule
A repo is an architecture source until actual payout and time evidence prove economics. GOX must never convert a repo author's income claim into an expected hourly wage without independent support.