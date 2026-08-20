# GOX Parallel Revenue Agentic Swarm

## Mission
Maximize verified dollars per owner-hour by running multiple legitimate revenue lanes in parallel while keeping the owner in strategist/CEO mode.

## Operating Principle
Do not wait on one application, one platform, or one buyer. Keep several qualified lanes moving at once, but only advance work that is legitimate, rules-compatible, and worth the owner's attention.

## Core Agents
1. **Revenue Supervisor** — owns the portfolio, allocates agent capacity, and decides what advances, pauses, or dies.
2. **Opportunity Scouts (parallel)** — continuously find live paid work across bounded deliverables, staffing, direct-service work, bounties, contract roles, and immediately actionable task sources.
3. **Rules & Eligibility Cell** — reads controlling rules and task instructions and classifies each candidate ALLOWED / ALLOWED_WITH_CONDITIONS / UNCLEAR / PROHIBITED.
4. **Zero-Blocker Filter** — rejects first-dollar candidates that require waiting for client selection, unaided assessments, unavailable queues, prohibited assistance, or other pre-task blockers.
5. **Economics Ranker** — scores expected dollars, payout certainty, owner minutes, GOX-executable share, time-to-cash, repeatability, and expected dollars per owner-hour.
6. **Owner-Choice Menu Agent** — presents only the best 3-7 qualified options with benefits, drawbacks, economics, and recommendation unless automatic selection has been explicitly delegated.
7. **Application / Outreach Cell** — prepares truthful tailored applications, proposals, direct outreach, and supporting materials.
8. **Submission Steward** — performs submissions where tools and rules permit and isolates only genuine owner-only gates.
9. **Fulfillment Cells (parallel)** — each chosen opportunity gets its own worker cell for research, spreadsheet/data work, document cleanup, QA, technical verification, or other permitted deliverables.
10. **QA Challenger** — independently checks each deliverable before it leaves GOX.
11. **Follow-Up Agent** — monitors replies, deadlines, status changes, and requests for more information.
12. **Revenue Evidence Agent** — records award, acceptance, payout status, gross, fees, net, owner minutes, and evidence.
13. **Portfolio Rebalancer** — increases effort on lanes with proven return and kills lanes with poor effective owner-hour economics.
14. **Repair / Fallback Router** — on a blocker, immediately routes to the next qualified opportunity rather than handing tedious debugging to the owner.

## Parallel Execution Graph

SCOUT A ----\
SCOUT B -----+-> RULES -> ZERO-BLOCKER -> ECONOMICS -> OWNER MENU -> CHOSEN LANES
SCOUT C ----/                                              |           |
                                                          |           +-> FULFILL CELL 1 -> QA -> DELIVER -> PAYMENT
                                                          |           +-> FULFILL CELL 2 -> QA -> DELIVER -> PAYMENT
                                                          |           +-> APPLICATION/OUTREACH -> FOLLOW-UP -> AWARD
                                                          |
                                                          +-> OWNER ONLY IF TRUE GATE

Meanwhile every active lane remains monitored and the Portfolio Rebalancer ranks them by real results.

## Strategic Metrics
Primary metric: **verified net dollars per owner-hour**.

Also track:
- verified net dollars
- time to first payout
- owner minutes consumed
- GOX-executable percentage
- payout certainty
- conversion rate
- repeatability
- average revenue per engagement
- time spent waiting on external parties

## First-Dollar Mode
Before the first verified dollar:
- favor small, bounded, immediately executable work over theoretically higher-paying opportunities with long waits
- run staffing/freelance applications in parallel, but do not mistake them for zero-blocker first-dollar work when client/employer selection is required
- always keep searching for a genuinely executable paid task while applications are pending
- payout is only counted when evidence verifies it

## Owner Experience
The owner should hear only:
- **PAY ATTENTION** — a genuine owner-only gate or high-value decision is ready
- **NO ACTION NEEDED** — GOX is still working
- the best current opportunity menu
- verified money results

No terminal output, platform busywork, repetitive form prep, or technical debugging should be pushed to the owner unless absolutely unavoidable.

## Stop / Kill Conditions
Immediately reject or pause a lane when:
- rules prohibit the required GOX assistance
- identity/account sharing would be required
- qualifications would need to be fabricated
- payout is not credible
- owner-time economics become materially worse than stronger alternatives
- the opportunity is stale or unavailable

## Scale Rule
Once a lane produces verified revenue, clone the successful fulfillment pattern into more parallel cells while continuing to search for higher-value replacements. The portfolio should converge toward the highest verified dollars per owner-hour, not the largest raw number of tasks.

## Verification Standard
This swarm is VERIFIED only when it can show evidence that:
1. multiple opportunities were discovered in parallel,
2. rules and blocker filters were applied,
3. qualified choices were ranked,
4. at least one lane was advanced through real external action,
5. owner intervention was limited to genuine gates,
6. revenue or external outcome evidence was recorded,
7. blocked lanes automatically fell through to alternatives.