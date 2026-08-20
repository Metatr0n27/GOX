# GOX Durable Parallel Revenue Agent Runtime Strategy

## Decision
GOX should use a durable, stateful, event-driven runner architecture rather than a chat-driven loop or a pile of independent cron jobs.

The owner remains strategy/approval. The runtime owns execution.

## What the user was reaching for
The useful concept is not Objective-C. It is an **objective-driven agent runner**: a durable supervisor that keeps a goal, fans work out to specialist agents in parallel, persists state, waits for external events, retries safely, and loops until a verified stop condition is reached.

## Required runtime qualities
1. Durable execution across process/VPS restarts.
2. Explicit state machine, not hidden chat state.
3. Parallel fan-out/fan-in for independent research/workers.
4. Human-in-the-loop pauses that survive for hours/days.
5. Event-driven wakeups for new opportunities, replies, settlement, and failures.
6. Idempotent side effects and duplicate-submit protection.
7. Tool boundaries: planning agents do not directly perform unrestricted side effects.
8. Adversarial reviewer/judge independent from the worker.
9. Structured inputs/outputs and evidence provenance.
10. Bounded retries, backoff, rate limits, timeouts, and circuit breakers.
11. Checkpoint/recovery and stale-work detection.
12. Source health, failure memory, suppression/cooldowns.
13. Observability: execution history, logs, latency, cost, owner minutes.
14. Secrets/identity separation and least privilege.
15. Kill switch, pause/resume, and manual override.
16. External settlement evidence before revenue is marked verified.
17. Predicted-versus-actual economics calibration.
18. Portfolio rebalancing toward actual verified net dollars per owner-hour.

## Reference mechanisms worth studying/adapting
### Agentspan / Conductor
Strong fit for runtime durability. Public README describes server-side durable executions, crash recovery, distributed workers, durable human approval, event triggers, parallel agents, guardrails, execution history, Prometheus/OpenTelemetry, and compatibility with existing agent frameworks. License indicated as MIT in its README. **Action: benchmark/adapt runtime mechanisms; do not wholesale adopt before a bounded VPS spike.**

### LangGraph
Strong reference for state graphs, durable checkpoints, memory, human interrupts, branching/subgraphs, and long-running stateful workflows. **Action: keep as a lower-dependency orchestration option.**

### OpenAI Agents SDK + durable orchestration integration
Useful for runners, handoffs, tool guardrails, and pairing agent logic with a durable orchestrator such as Temporal/Dapr/Restate. **Action: study as agent API layer, not necessarily the persistence layer.**

### Bottega
Useful reference for plan -> implement -> adversarial review -> revise -> CI loop and human-at-boundaries pattern. **Action: copy the review-loop discipline, not necessarily its entire engineering workflow.**

### AgentChassis
Useful contract-first pattern: planner cannot implement; scoped work records define acceptance criteria before execution; independent reviewers verify against intent. **Action: adapt contracts/provenance into GOX work items.**

### Iterion
Useful ideas for declarative orchestration, parallel fan-out/fan-in, routing modes, convergence-driven loops, and liveness backstops. **Action: study loop and routing semantics.**

### GPT Researcher / STORM
Useful for objective research decomposition, independent branches, source provenance, contradiction search, aggregation, and publication. **Action: use within the Research plane, not as the main revenue runtime.**

### OpenHands
Useful for tool/code execution, repository interaction, verification, and converting research/plans into tested artifacts. **Action: study execution sandbox and verification patterns.**

### Agent Bounties / CashClaw patterns already studied
Retain funded/readiness/settlement truth, stream/poll fallback, evaluate-before-accept, tool-isolated side effects, persistent state, feedback memory, and continuous evaluation.

## GOX target topology

```text
                         OWNER / STRATEGIST
                    objective + true owner gates
                              |
                              v
+---------------------------------------------------------------+
|                    DURABLE REVENUE SUPERVISOR                 |
| objective: maximize verified net dollars / owner-hour         |
| state, budgets, policies, kill switch, portfolio allocation   |
+---------------------------------------------------------------+
     |                 |                  |                 |
     v                 v                  v                 v
SOURCE CELL       RESEARCH CELL       EXECUTION CELL      AUDIT CELL
adapters          scouts x N          planner             judge
availability      verifier x N        workers x N         evidence
rules             skeptic             synthesizer         security
funding           economics           QA                  economics
     \                 |                  |                 /
      +----------------+------------------+----------------+
                              |
                              v
                        STATE / EVENT BUS
                              |
       +----------------------+------------------------+
       |                      |                        |
       v                      v                        v
 owner-gate events       external replies       settlement/payment
       |                      |                        |
       +----------------------+------------------------+
                              |
                              v
                     LEARN / CALIBRATE / REBALANCE
                              |
                              +-----> loop
```

## Work contract
Every runner task should be an explicit record containing:
- objective
- allowed tools and side effects
- source/opportunity ID
- input provenance
- deadline/TTL
- expected economics
- owner-minute budget
- confidentiality class
- acceptance criteria
- tests/verifier
- retry policy
- idempotency key
- evidence required
- completion state
- failure classification

## State machine
`DISCOVER -> NORMALIZE -> VERIFY -> SCORE -> SELECT -> PLAN -> EXECUTE -> QA -> SUBMIT -> ACCEPT/REVISE -> SETTLE -> VERIFY_PAYMENT -> LEDGER -> LEARN -> REBALANCE`

Exception routes:
- `FAIL -> CLASSIFY -> RETRY/REPAIR/SUPPRESS -> RESUME`
- `OWNER_GATE -> DURABLE_PAUSE -> OWNER_ACTION -> VERIFY -> RESUME`
- `TIMEOUT/STALE -> RECONCILE_EXTERNAL_STATE -> RETRY OR CLOSE`

## Parallelism rules
Parallelism is useful only where independence adds information or throughput.

Use parallel runners for:
- source discovery across independent sources
- independent research/verifier/skeptic branches
- bounded fulfillment subtasks with non-overlapping state
- QA checks
- settlement watchers across active opportunities

Do not parallelize:
- the same consequential submission
- account-bound actions
- writes without idempotency
- agents competing to mutate the same state without a lock/lease

## Missing gaps to close before calling this production
### Runtime/control plane
- durable queue/event bus
- leases/locks for work ownership
- worker heartbeat
- process restart recovery
- dead-letter queue
- retry/backoff/circuit breaker
- execution budgets and cancellation
- versioned work contracts

### Revenue/data plane
- at least one verified live external source adapter
- source-specific rules parser/review state
- availability/funding verifier
- submission/revision adapters where permitted
- settlement/payment evidence adapters
- owner-minute and compute-cost tracking
- predicted-vs-actual calibration

### Safety/governance
- least-privilege credentials
- identity/account lane isolation
- confidential-data classifications
- audit log
- approval policy engine
- kill switch and emergency stop
- action replay protection

### Quality
- adversarial judge independence
- golden tests for state transitions
- simulated crash/restart tests
- duplicate-submit tests
- stale/reconciliation tests
- source outage tests
- settlement evidence tests

### Owner interface
- one owner-gate inbox
- PAY ATTENTION / NO ACTION NEEDED semantics
- hourly executive brief
- immediate critical alerts where delivery system permits
- money/economics dashboard sourced from the ledger, not projections

## Adoption strategy
Do not replace GOX with a large framework immediately.

1. Keep current GOX revenue schema/ledger as system of record.
2. Define a small Runner interface and durable WorkContract.
3. Benchmark two runtime paths on the VPS:
   - Path A: current Python + SQLite/systemd + explicit queue/leases (lowest dependency)
   - Path B: Agentspan/Conductor or LangGraph durable runtime (higher capability)
4. Test both on the same synthetic revenue workflow with crash/restart, parallel workers, owner pause, retry, and evidence collection.
5. Select the smallest runtime that passes reliability requirements.
6. Attach one real read-only source.
7. Run one real opportunity end-to-end.
8. Only then expand sources/workers.

## Selection metric for the runtime itself
The runtime is not judged by elegance or GitHub stars. Judge it by:
- recovery success
- owner minutes saved
- duplicate side effects prevented
- setup/maintenance burden
- observability
- latency/cost
- security surface
- integration effort
- measured effect on verified net dollars per owner-hour

## Definition of ready
GOX is ready for continuous live operation only when it can:
1. ingest a real opportunity automatically,
2. persist and recover its state after a forced restart,
3. execute parallel bounded runners safely,
4. pause durably for a real owner gate,
5. resume after the gate,
6. prevent duplicate external actions,
7. reconcile external truth after failures,
8. capture acceptance/payment evidence,
9. record actual economics,
10. use those outcomes to change future selection.

Until these are externally tested, describe the system as **implementation-in-progress**, not autonomous revenue production.
