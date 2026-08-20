# GOX Open-Source Revenue Edge Stack

## Purpose
Use proven open-source agent architectures to improve GOX's revenue engine without copying unverified revenue claims or importing unsafe automation patterns.

## Ranked Sources

### 1. moltlaunch/cashclaw — MIT
Best reusable pattern: one-process autonomous work loop.

Useful concepts to adapt:
- receive work signals
- evaluate task fit
- quote/price
- execute with an LLM/tool runtime
- submit deliverable
- collect outcome/rating
- feed results back into future task selection

Why it matters to GOX: this maps directly onto the existing revenue engine and closes the gap between opportunity discovery and actual fulfillment.

Do not copy blindly: marketplace-specific wallet/onchain code should remain behind an adapter boundary.

### 2. NSPG13/agent-bounties — Apache-2.0
Best reusable pattern: deterministic paid-task lifecycle.

Useful concepts to adapt:
- inspect -> claim -> solve -> submit -> verify -> confirm payment -> repeat
- only treat work as earnable when funded and verification-ready
- deterministic acceptance evidence
- fail-closed opportunity feeds
- explicit settlement confirmation before counting revenue
- bounded wallet / signer separation concepts where relevant

Why it matters to GOX: this is especially aligned with the first-dollar rule because it treats verification and settlement as first-class state rather than optimistic status labels.

### 3. fablerlabs/mainspring — Apache-2.0
Best reusable pattern: long-lived agent governance and durable execution.

Useful concepts to adapt:
- separate reasoning/brain from tool execution
- actions pass through a gate before touching network/files/secrets
- durable sessions and crash-resume behavior
- money, memory, governance, and auditability as runtime concerns

Why it matters to GOX: this strengthens the engine so it can run for long periods without giving broad uncontrolled authority to the model.

### 4. Jennivarl/underworld — MIT
Best reusable pattern: agent subcontracting and explicit unit economics.

Useful concepts to adapt:
- orchestrator decomposes paid work into specialist subtasks
- specialist costs are known before execution
- parent job tracks gross, subcontractor cost, and net margin
- machine-verifiable payment chain

Why it matters to GOX: this is a clean model for future fulfillment cells and per-task margin accounting.

## Important Negative Case
### Ithiel-Labs/make-money-30-Day-experiment
Do not copy its autonomy model.

Useful lessons:
- unrestricted autonomous outreach produced spam and account blocks
- huge build/output volume produced $0 revenue
- spending controls and kill switches are mandatory
- identity/distribution gates are real bottlenecks
- external-action rate limits are necessary
- stop/pause semantics must be hard technical controls

GOX should copy the lessons, not the behavior.

## Revenue Evidence Standard
A repository claiming to be revenue-generating is not enough. GOX should separately classify:
- claimed revenue
- demonstrated transactions
- demonstrated net profit
- demonstrated owner time
- independently verifiable payout evidence

Do not infer dollars-per-hour unless revenue and owner-time evidence are both available.

## Recommended GOX Fusion
Build the runtime as:

OPPORTUNITY FEED
-> CASHCLAW-STYLE EVALUATE/QUOTE
-> AGENT-BOUNTIES-STYLE FUNDED + VERIFICATION-READY GATE
-> GOX RULES / OWNER-GATE FILTER
-> MAINSPRING-STYLE ACTION GOVERNANCE
-> GOX FULFILLMENT CELL
-> QA / DETERMINISTIC EVIDENCE
-> SUBMIT
-> SETTLEMENT CONFIRMATION
-> REVENUE LEDGER
-> FEEDBACK / PORTFOLIO REBALANCER

If fulfillment needs specialist agents:

PARENT JOB
-> UNDERWORLD-STYLE DECOMPOSITION
-> SPECIALIST CELLS WITH KNOWN COST
-> SYNTHESIS
-> QA
-> DELIVERY
-> NET MARGIN RECORD

## License Rule
MIT and Apache-2.0 code may be reused subject to their license requirements. Preserve required notices and provenance for any copied code. Prefer adapting narrowly scoped modules and interfaces over wholesale forks so GOX stays coherent and auditable.

## Priority Implementation Order
1. Work-loop adapter based on CashClaw concepts.
2. Deterministic claim/verification/settlement state based on Agent Bounties concepts.
3. Action-gate and durable session patterns based on Mainspring concepts.
4. Specialist subcontract/margin model based on Underworld concepts.
5. Add explicit external-action rate limits, cost ceilings, and kill switch before high-volume autonomous operation.
