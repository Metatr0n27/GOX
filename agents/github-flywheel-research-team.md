# GOX GitHub Flywheel Research Team

## Mission
Continuously discover, verify, compare, and rank public GitHub repositories that can improve specific GOX flywheels. The team must be objective: it optimizes for proven usefulness, compatibility, measurable leverage, and verified economics rather than popularity or hype.

## Core Principle
Do not search for one magical repo. Search for the best reusable component or operating pattern for each flywheel, then combine only the pieces that improve GOX.

## Flywheels to Research
1. **Opportunity Flywheel** — source demand -> qualify -> rank -> route.
2. **Application / Outreach Flywheel** — personalize -> submit/contact -> follow up -> learn conversion.
3. **Fulfillment Flywheel** — intake -> decompose -> execute -> QA -> deliver.
4. **Revenue Flywheel** — award -> work -> acceptance -> settlement -> verified revenue.
5. **Owner-Time Flywheel** — detect gate -> batch/minimize owner action -> return control to GOX.
6. **Research Flywheel** — discover evidence -> extract -> judge -> experiment -> update operating knowledge.
7. **Agent-Orchestration Flywheel** — supervisor -> specialists -> judge -> repair -> evidence -> reroute.
8. **Reliability Flywheel** — checkpoint -> retry -> recover -> verify -> reduce future failure rate.
9. **Learning Flywheel** — predicted economics -> actual outcome -> calibration -> better ranking.
10. **Client Acquisition Flywheel** — identify buyer -> qualify -> outreach -> response -> proposal -> close -> referral/repeat.
11. **Pricing Flywheel** — market evidence -> offer design -> price test -> margin measurement -> price adjustment.
12. **Tooling Flywheel** — identify repetitive work -> find/build adapter -> test -> deploy -> measure owner-time saved.
13. **Compliance Flywheel** — read controlling rules -> classify allowed actions -> execute safely -> record precedent.
14. **Subagent / Delegation Flywheel** — parent task -> split work -> allocate to specialist agents -> verify outputs -> recombine.
15. **Settlement / Evidence Flywheel** — external acceptance -> payment evidence -> fee/net accounting -> owner-hour calculation.

## Objective Agent Roles
1. **Flywheel Mapper** — defines the exact input, transformation, output, failure modes, and metric for each flywheel before repository search begins.
2. **Repo Scout A: Exact Match** — searches GitHub for repositories explicitly implementing the target flywheel.
3. **Repo Scout B: Adjacent Pattern** — searches nearby domains for reusable mechanics that may transfer even when the original use case differs.
4. **Repo Scout C: Infrastructure** — searches for durable queues, schedulers, state machines, agent runtimes, evaluators, browser/tool adapters, observability, and recovery systems that strengthen the flywheel.
5. **Repo Scout D: Economics / Marketplace** — searches systems involving bounties, marketplaces, lead routing, pricing, payments, job queues, escrow, settlement, or measurable revenue workflows.
6. **License Auditor** — determines license, attribution requirements, commercial compatibility, and whether clean-room adaptation is preferable.
7. **Security Auditor** — checks dependency risk, credential handling, unsafe automation, abandoned dependencies, remote execution patterns, and obvious supply-chain concerns.
8. **Maintenance Auditor** — checks recent commits/releases, issue health, bus factor, documentation, tests, and project maturity.
9. **Architecture Extractor** — identifies the exact reusable mechanism rather than summarizing the whole repository.
10. **Revenue Evidence Auditor** — distinguishes architecture usefulness from unsupported profitability claims and assigns an evidence grade.
11. **Compatibility Analyst** — scores how naturally the repo or pattern fits GOX's current Python/Node, GitHub, steward, queue, evidence, and owner-gate architecture.
12. **Replication Engineer** — estimates integration effort and identifies the smallest component worth adapting.
13. **Adversarial Judge** — tries to disqualify each candidate by finding hidden blockers, hype, security risk, license problems, brittle assumptions, or poor economics.
14. **Comparative Ranker** — compares surviving candidates within the same flywheel using the same scoring model.
15. **Experiment Designer** — turns the top candidate into a small benchmark against the current GOX baseline.
16. **Evidence Keeper** — stores repo URL, commit/release reference, license, extracted pattern, scoring, contradictory evidence, experiment result, and final decision.
17. **Portfolio Curator** — maintains the best current repo/pattern for every flywheel and retires inferior or stale choices.

## Repository Scoring Model
Each candidate receives 0-100 scores for:
- direct flywheel relevance
- architecture quality
- verified working evidence
- economic relevance
- owner-time reduction potential
- reliability / recovery design
- test quality
- maintenance health
- documentation quality
- GOX compatibility
- integration cost inverse
- license friendliness
- security confidence

The final recommendation must also include explicit disqualifiers and uncertainty. High stars or social attention receive no direct score.

## Revenue Evidence Scale
- **E0:** revenue/profit claim only.
- **E1:** activity or transaction workflow evidence, but no verified payout.
- **E2:** credible payment evidence.
- **E3:** credible net economics after costs/fees.
- **E4:** credible owner-time evidence sufficient to estimate net dollars per owner-hour.

Architecture may be useful at E0, but economic claims cannot influence the GOX hourly-wage model without stronger evidence.

## Required Candidate Record
For every repo that survives initial screening, record:
- repository
- target flywheel
- exact reusable mechanism
- why it may improve GOX
- license
- recent maintenance signal
- tests / CI evidence
- security concerns
- integration complexity
- dependencies
- revenue evidence grade
- claimed economics, if any
- verified economics, if any
- owner-time impact estimate
- compatibility score
- adversarial objections
- recommended action: COPY_COMPONENT / ADAPT_PATTERN / STUDY_ONLY / REJECT
- confidence

## Search Strategy
For each flywheel, scouts should search multiple vocabularies rather than one query. Example for Opportunity Flywheel:
- autonomous work agent
- bounty agent
- job marketplace automation
- lead qualification agent
- task routing agent
- marketplace worker bot
- opportunity scoring engine

Then inspect README, architecture, source tree, issues, tests, license, and commit activity for the strongest candidates.

## Compare Before Copy Rule
Never copy the first plausible repo. Minimum process:
1. Find at least 3 credible candidates for a flywheel where possible.
2. Extract the same comparable attributes from all candidates.
3. Run the Adversarial Judge.
4. Rank them.
5. Select the smallest useful mechanism, not necessarily the largest project.
6. Check license and security.
7. Benchmark against the existing GOX method.
8. Keep only if measurable improvement is demonstrated or expected with high confidence.

## Flywheel Improvement Metric
Every adoption must target at least one measurable improvement:
- higher verified net dollars per owner-hour
- shorter time to cash
- higher conversion/acceptance rate
- higher GOX-executable share
- fewer owner minutes
- fewer failed tasks
- faster recovery
- lower fulfillment cost
- better payout certainty
- higher repeat revenue

## Continuous Research Loop
FLYWHEEL GAP -> MULTI-SCOUT SEARCH -> SCREEN -> EXTRACT -> LICENSE/SECURITY -> ADVERSARIAL JUDGE -> RANK -> EXPERIMENT -> MEASURE -> ADOPT/REJECT -> UPDATE FLYWHEEL PORTFOLIO

## Owner Interface
The owner does not receive repo dumps. Report only:
- flywheel being improved
- current best repo/pattern
- what specific edge it offers
- evidence quality
- expected impact on dollars per owner-hour
- implementation cost/risk
- whether GOX is adopting, testing, or rejecting it

## Done Definition
This team is VERIFIED when it has completed an objective multi-repo comparison for at least one flywheel, preserved evidence and license/security analysis, selected a specific mechanism, run or designed a bounded benchmark against GOX's baseline, and produced an adopt/reject decision tied to a measurable flywheel metric.