# GOX Easy Prompt Parallel Orchestration

## Decision
Use the Easy Prompt as a small, explicit work contract and run multiple independent prompts in bounded parallel batches. Do not maximize prompt count. Optimize useful independent coverage per dollar, per minute, and per owner-hour.

## Core rule
Parallel prompts are valuable when they are independent and their results can be compared or merged safely. Consequential actions remain serialized.

## Prompt roles for one objective
For a complex objective, default to a small ensemble:
1. Scout — find candidate facts/options.
2. Verifier — independently check the strongest claims.
3. Skeptic — search for contradictions/failure modes.
4. Planner — turn verified evidence into an execution plan.
5. Worker(s) — execute bounded independent subtasks.
6. Synthesizer — combine outputs without inventing facts.
7. QA/Judge — test acceptance criteria and reject weak work.

Not every objective needs all seven. Start with the smallest set that can falsify errors.

## Concurrency policy
### Research
Default: 3 simultaneous independent prompts
- Scout A
- Scout B / alternative-source scout
- Skeptic or verifier

Increase to 4-6 only when:
- the question has genuinely independent branches,
- expected value of additional coverage exceeds compute cost,
- the synthesis stage can handle the added evidence,
- no shared mutable state is being changed.

### Execution
Default: 1 planner + 1-3 bounded workers in parallel when work can be partitioned without overlap.
Examples: independent source checks, separate data-cleaning shards, independent QA checks.

### Consequential external actions
Concurrency: 1.
Never fan out multiple prompts that could each submit, purchase, accept, claim, send, sign, or mutate the same external account/state.

## Easy Prompt contract
Each prompt should contain:
- objective
- exact scope
- allowed tools
- prohibited side effects
- source/evidence requirements
- acceptance criteria
- token/dollar budget
- deadline/TTL
- output schema
- idempotency key when applicable
- confidence and uncertainty requirements

## Two-hour pilot
Goal: discover the best prompt team size and model-routing policy before allowing meaningful paid model spend.

Run the same representative objective with three configurations:
A. Single strong prompt
B. 3-agent ensemble: Scout + Verifier + Skeptic
C. 5-agent ensemble: 2 Scouts + Verifier + Skeptic + Synthesizer

For each configuration measure:
- input tokens
- output tokens
- model calls
- wall-clock time
- compute dollars
- factual/decision quality
- contradictions caught
- useful unique findings
- duplicated findings
- owner minutes
- completion/rework rate

Do not spend external model money for the pilot unless an explicit dollar cap is approved. Prefer already-included/free/local execution where available.

## Selection rule after pilot
Choose the smallest configuration that reaches the required quality threshold.

A larger swarm is adopted only if:
Incremental expected verified value > incremental compute cost + added coordination/review cost.

## Anti-patterns
- 20 agents researching the same question with no independent roles
- giving every prompt the entire conversation/history
- using premium reasoning for deterministic extraction
- allowing every worker to mutate external state
- counting prompt volume as productivity
- keeping a prompt alive because it is busy rather than because it advances the objective

## Owner-facing language
The owner may simply say:
- “Use a small parallel research team.”
- “Use enough prompts to cross-check this, but keep cost low.”
- “Use stronger reasoning only if the cheaper pass is uncertain.”
- “Do not exceed my test budget.”
- “Show me what the extra prompts bought us.”

GOX should translate this into concurrency, routing, and token/dollar budgets automatically.

## Post-pilot recommendation output
After approximately two hours of representative testing, report:
- recommended default simultaneous prompt count for research
- recommended default simultaneous worker count for execution
- recommended token range per Easy Prompt by task class
- recommended dollar cap per objective
- recommended premium-model escalation threshold
- expected cost per completed objective
- evidence for why these settings are preferred

The recommendation must be based on measured usage, not a generic token number.
