# GOX Three-Lane Strategy Validation Team

## Mission
Independently test whether GOX should be organized around a three-lane operating model and whether the proposed lanes actually improve verified net dollars per owner-hour.

This team exists to challenge prior advice, not to confirm it.

## The hypothesis under test
Candidate operating model:
1. **Find Money** — discover, verify, score, and qualify opportunities.
2. **Do the Work** — plan, execute, QA, submit, and revise where allowed.
3. **Prove & Improve the Money** — verify acceptance/payment, record economics, learn, suppress weak paths, and rebalance.

The team must also test competing models, including:
- two-lane model: acquisition + fulfillment/settlement
- four-lane model: discovery + verification + execution + settlement/learning
- functional-agent model without lane boundaries
- source-specific pods
- event-driven state-machine organization rather than lane-first organization

No lane model is accepted because it sounds simple.

## Authenticity standard
An authentic research agent must have:
- a defined objective
- independent evidence gathering
- explicit sources/provenance
- a bounded decision output
- uncertainty/confidence
- contradiction handling
- no fabricated evidence
- a reproducible research record

Markdown role descriptions alone do not make the agents operational. Runtime execution must later instantiate these roles as durable runner contracts with inputs, tools, outputs, and evidence.

## Independent research cells

### 1. Architecture Scout
Objective: find credible agent-runtime and operations architectures relevant to durable multi-agent revenue systems.
Looks for:
- durable execution
- fan-out/fan-in
- event-driven workflows
- human-in-the-loop
- state machines
- retries/recovery
- work ownership/leases
- observability

Output: candidate mechanisms, not popularity rankings.

### 2. Operations Design Scout
Objective: research whether three functional lanes are a useful operating abstraction or whether another partitioning is better.
Tests:
- cognitive simplicity for owner
- clean handoffs
- accountability
- failure isolation
- scalability
- minimal duplicated state

Output: comparison table of organizational models.

### 3. Revenue Economics Scout
Objective: test which structure best optimizes verified net dollars per owner-hour.
Normalizes:
- gross dollars
- net dollars
- owner minutes
- compute/tool cost
- probability of payout
- time to cash
- repeatability
- rejection risk
- automation share

Output: economic model and thresholds.

### 4. Reliability Scout
Objective: identify hidden failure modes in long-running parallel agent systems.
Must inspect:
- duplicate work
- race conditions
- stale state
- orphaned tasks
- crash recovery
- bad retries
- dead-letter handling
- source outages
- rate limits
- external-state mismatch
- accidental repeated submissions

Output: failure catalog + required controls.

### 5. Security / Identity Scout
Objective: identify boundaries that cannot be automated or pooled across accounts.
Must inspect:
- credentials
- MFA/CAPTCHA
- identity verification
- OAuth/consent
- tax/payment setup
- account-sharing rules
- confidential task data
- least privilege
- audit trail

Output: owner-gate policy and credential-isolation requirements.

### 6. Platform / Rules Scout
Objective: determine whether each revenue source permits the proposed assistance, automation, API/browser interaction, or multi-agent execution.
Output for each source:
- ALLOWED
- ALLOWED_WITH_CONDITIONS
- HUMAN_ONLY
- UNCLEAR
- PROHIBITED
with source evidence and date.

### 7. Runtime Framework Scout
Objective: compare current GOX-native runtime against durable orchestration frameworks.
Candidates should include where relevant:
- current Python + SQLite + systemd
- LangGraph
- Agentspan / Conductor
- Temporal-style durable workflow patterns
- Restate/Dapr-style durable execution patterns

Output: adoption matrix with reliability, setup burden, integration cost, observability, owner-time reduction, security surface.

### 8. Research Method Scout
Objective: verify that the research process itself is robust.
References useful patterns from systems such as GPT Researcher/STORM and scientific literature review practice.
Output: source-quality rubric, contradiction policy, freshness policy, and reproducibility checklist.

## Independent verification layer

### 9. Verifier A
Re-runs the strongest claims from the scouts independently.
May not rely on scout summaries alone.

### 10. Verifier B
Attempts to reproduce architecture/economics claims from primary sources or code.

### 11. Skeptic / Red Team
Goal: prove the preferred design is wrong.
Must ask:
- Why would three lanes fail?
- Where do handoffs add latency?
- Which state belongs to more than one lane?
- Does the model hide source-specific constraints?
- Does parallelism increase duplicate/consequential action risk?
- Are we optimizing activity rather than verified payment?

### 12. Evidence Judge
Scores each claim:
- E0 assertion only
- E1 mechanism documented
- E2 mechanism independently verified
- E3 tested in a bounded experiment
- E4 tested with real external revenue/owner-time evidence

No architectural recommendation can be called proven above its evidence level.

## Comparative decision protocol
Every major design choice must compare at least three viable options where possible.

For each option record:
- mechanism
- evidence
- contradictory evidence
- integration effort
- operational burden
- recovery model
- owner-minute effect
- effect on verified net dollars/owner-hour
- security/rules risk
- reversibility
- confidence

## Decision questions
The team must answer these before recommending a model:
1. Is three lanes the best owner-facing abstraction?
2. Is the internal runtime better modeled as lanes, a state machine, pods, or both?
3. Which boundaries should be organizational only versus enforced technical boundaries?
4. What is the minimum durable runtime needed before live revenue work?
5. Which functions should run in parallel and which must be serialized?
6. Where are true owner gates?
7. What evidence is required before GOX counts money as earned?
8. Which failure modes can silently create false confidence?
9. What architecture minimizes owner intervention without increasing risk?
10. What is the smallest bounded experiment that can falsify the preferred design?

## Likely provisional model to test
Owner-facing structure may be three lanes for simplicity:
- Lane 1: Find Money
- Lane 2: Do the Work
- Lane 3: Prove & Improve

But the technical runtime underneath should remain an explicit event/state machine:
DISCOVER -> VERIFY -> SCORE -> PLAN -> EXECUTE -> QA -> SUBMIT -> SETTLE -> VERIFY_PAYMENT -> LEARN -> REBALANCE

This is a hypothesis, not a conclusion.

## First experiments
### Experiment A — architecture simulation
Run synthetic opportunities through:
- three-lane grouping
- four-lane grouping
- no-lane state-machine-only grouping
Measure handoffs, duplicate state, recovery complexity, owner alerts, and completion latency.

### Experiment B — crash/recovery
Force worker death at planning, execution, submission-prep, settlement-watch stages.
Success requires exact recovery without duplicate consequential actions.

### Experiment C — parallelism
Fan out 3 independent research/QA workers and verify deterministic fan-in.
Then attempt a consequential duplicate-submission scenario and ensure the runtime serializes/prevents it.

### Experiment D — owner gate
Pause for a simulated login/MFA/consent gate for an extended period, resume without lost state.

### Experiment E — economics
Compare predicted versus actual owner minutes and costs on a bounded real opportunity. The architecture only survives if it improves or preserves expected verified net dollars per owner-hour.

## Output format
Every team run produces:
- QUESTION
- OPTIONS
- EVIDENCE
- CONTRADICTIONS
- RISKS
- EXPERIMENT
- RESULT
- CONFIDENCE
- RECOMMENDATION
- WHAT WOULD CHANGE THE RECOMMENDATION

## Current policy
Do not treat the three-lane model as settled truth until the team has challenged it and a runtime experiment supports it. Use it provisionally as an owner-facing simplification while preserving the more precise state-machine model underneath.
