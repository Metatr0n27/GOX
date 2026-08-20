# GOX Authentic Revenue Runner Team

## Mission
Operate the complete money loop continuously and authentically: find work, verify it, rank it, execute what GOX is allowed to execute, surface only genuine owner gates, verify outcomes, learn from failures, and improve verified net dollars per owner-hour.

## Operating Rule
The owner sets goals and handles only genuine owner-only gates. Runners execute, verify, repair, and return evidence. No runner may impersonate a person, fabricate qualifications, share accounts, bypass MFA/CAPTCHA, or violate platform/client rules.

## Authentic Runner Roles
1. **Revenue Supervisor Runner** — owns the portfolio, selects which lane gets resources, and stops low-value work.
2. **Source Discovery Runner** — continuously finds live sources of legitimate paid work.
3. **Source Adapter Runner** — converts each approved source into normalized opportunity records for the Revenue Engine.
4. **Availability/Funding Runner** — verifies that work is actually available, funded or plausibly payable, and not merely advertised.
5. **Rules Runner** — checks controlling terms, task instructions, confidentiality, AI/tool/delegation rules, and identity requirements.
6. **Eligibility Runner** — checks whether the correct person/lane can legitimately participate and receive payment.
7. **Blocker Runner** — rejects queues/tasks that require unavailable human-only steps, client selection, unavailable payout, another person's approval, or prohibited assistance.
8. **Economics Runner** — predicts net dollars, payout probability, owner minutes, time-to-cash, repeatability, and expected dollars per owner-hour.
9. **Owner-Gate Runner** — isolates login, MFA, CAPTCHA, identity, OAuth, tax/payment, signatures, consent, or required final submit into the smallest possible owner action.
10. **Task Intake Runner** — captures task state, IDs/hashes, deadlines, evidence requirements, and duplicate-submit protection.
11. **Task Planner Runner** — decomposes allowed work into bounded steps and assigns specialists.
12. **Specialist Worker Runners** — perform spreadsheet/data cleanup, structured research, document cleanup, categorization, QA, coding, or other allowed work.
13. **Independent Worker Runner** — produces a separate solution when ensemble review is useful and permitted.
14. **Synthesizer Runner** — combines independent work without inventing unsupported facts.
15. **QA Challenger Runner** — tries to reject the output before the client/platform can; checks completeness, format, source support, constraints, and hidden failure modes.
16. **Submission Runner** — prepares or performs submission where rules permit; otherwise routes the precise final owner gate.
17. **Acceptance Runner** — watches for accepted/rejected/revision states and routes revision work automatically.
18. **Settlement Runner** — tracks payable/paid/settled state and requires external evidence before calling revenue verified.
19. **Revenue Ledger Runner** — records gross, fees, net, owner minutes, compute cost, payment evidence, and effective dollars per owner-hour.
20. **Failure-Memory Runner** — records source/task failure causes and suppresses repeated bad paths.
21. **Calibration Runner** — compares predicted versus actual economics and updates confidence/scoring inputs.
22. **Portfolio Rebalancer Runner** — moves effort toward sources/classes with better actual economics and away from weak ones.
23. **Gap Detector Runner** — finds missing adapters, tools, permissions, state, tests, evidence, or automation that forces owner effort.
24. **Gap Closer Runner** — fixes technical gaps when GOX can do so; creates reusable assets and verifies them.
25. **Reliability Runner** — watches stale work, retries safe actions, handles checkpoints/recovery, and prevents duplicate side effects.
26. **Security Runner** — protects secrets, validates identity boundaries, redacts logs, and blocks risky automation.
27. **Research Runner** — studies GitHub repos, market patterns, literature, pricing, competitor workflows, and failure cases that may improve a flywheel.
28. **Evidence Judge Runner** — distinguishes claims from verified facts and rejects unsupported success declarations.
29. **Chief-of-Staff Runner** — synthesizes only what the owner needs: PAY ATTENTION or NO ACTION NEEDED, current money status, best lane, blocker/gap, and exact owner action if any.

## Required State Machine
DISCOVER -> NORMALIZE -> VERIFY RULES/ELIGIBILITY -> VERIFY AVAILABILITY/FUNDING -> SCORE -> SELECT -> PLAN -> EXECUTE -> QA -> SUBMIT -> ACCEPT/REVISE -> SETTLE -> VERIFY PAYMENT -> RECORD ECONOMICS -> LEARN -> REBALANCE -> REPEAT

Any failure routes to:
FAILURE -> CLASSIFY -> REPAIR or SUPPRESS SOURCE -> RECORD LESSON -> RESUME

Any genuine owner gate routes to:
OWNER GATE -> MINIMAL ACTION -> VERIFY COMPLETION -> RETURN TO RUNNER LOOP

## Runner Truth Rules
- Application submitted is not money.
- Task completed is not money.
- Task accepted is not money unless payment/settlement is externally evidenced.
- Advertised hourly pay is not realized dollars per owner-hour.
- A source with repeated empty queues or excessive owner gates must be downranked.
- Every side effect must be idempotent or have duplicate protection.
- Every consequential state transition must have evidence.

## Gap Classes The Team Must Detect Automatically
- no live opportunity adapters
- stale hard-coded platform assumptions
- weak or missing availability/funding proof
- unclear task-level AI/tool rules
- identity/payout incompatibility
- missing browser/API/connector path
- missing persistent state/checkpoint
- duplicate submission risk
- no revision loop
- no settlement verification
- no actual owner-minute tracking
- no compute/tool cost accounting
- no predicted-vs-actual calibration
- no source failure memory
- no source suppression/cooldown
- no portfolio rebalancing
- no stale-task/timeout handling
- no backoff/rate-limit handling
- no source health score
- no provenance/evidence schema
- no confidential-data boundary
- no kill switch/manual override
- no runtime heartbeat/observability
- no regression tests for money-critical state transitions
- research documents not wired into runtime behavior

## Owner Interface
The owner should normally see one of two states:

**NO ACTION NEEDED** — GOX is actively working, waiting on an external party, or repairing itself.

**PAY ATTENTION** — a genuine owner-only gate or high-value strategic decision exists. Include one exact action and why it matters.

## Success Metric
Primary: verified net dollars per owner-hour.
Secondary: time-to-cash, acceptance rate, repeatability, GOX-executable share, owner minutes, failure rate, recovery time, payout certainty, and recurring revenue.

## Definition of Authentic
An agent/runner is authentic only when it has a real input, real state, a bounded authority set, observable actions, evidence-backed outputs, and explicit failure/repair behavior. Markdown role descriptions alone do not count as running agents.
