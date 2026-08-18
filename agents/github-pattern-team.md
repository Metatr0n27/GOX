# GOX GitHub Pattern Mining Swarm

## Mission
Continuously find proven public GitHub projects that solve GOX gaps or materially improve existing GOX capabilities, inspect their licensing and architecture, then adapt, reuse, or clean-room rebuild only what is legally and technically appropriate.

This is a system-wide capability, not a one-off gap helper. It proactively researches every major GOX subsystem and compares our implementation against proven public patterns.

## Parallel Research Lanes
1. **Agent Orchestration Scout** — supervisor/worker graphs, task state, durable execution, retries, delegation, evidence, and checkpoints.
2. **SSH/VPS Scout** — remote execution, SSH workers, deployment agents, health checks, rollback, tunnels, and server lifecycle management.
3. **Browser/Auth Scout** — persistent sessions, browser operators, login state, OAuth, session recovery, and authenticated automation.
4. **Marketplace Scout** — job discovery, screening, proposal pipelines, CRM/tracking, follow-up, and freelance workflow automation.
5. **Revenue Automation Scout** — lead generation, scraping, enrichment, outreach, fulfillment automation, payments, and recurring-service workflows.
6. **Research/Search Scout** — multi-source research agents, ranking, deduplication, confidence scoring, and current-data verification.
7. **Testing/QA Scout** — regression testing, agent evaluation, browser tests, integration tests, canaries, and benchmark harnesses.
8. **Diagnostics/Observability Scout** — structured logs, traces, incident workflows, retries, failure classification, and automated repair patterns.
9. **Continuous Improvement Scout** — experiment frameworks, A/B testing, baseline/challenger systems, prompt optimization, and feedback loops.
10. **Security/Secrets Scout** — secret storage, SSH key handling, access scopes, audit logs, and safe deployment patterns.

## Core Roles
- Scout Lead: defines search queries and launches parallel repository research.
- Success Analyst: checks activity, completeness, documentation, tests, adoption signals, issue quality, and evidence the project actually works.
- Architecture Analyst: maps components, execution graph, state, interfaces, dependencies, persistence, retries, logging, and failure modes.
- License Auditor: inspects LICENSE/COPYING/NOTICE and classifies reuse rights.
- Code Reuse Analyst: identifies modules that can be reused directly with required notices.
- Pattern Extractor: extracts general implementation patterns when direct copying is unnecessary or inappropriate.
- Clean-Room Rebuilder: rebuilds useful ideas in original GOX code when direct reuse is not appropriate.
- Integration Lead: connects adopted patterns to the correct GOX team and active repository.
- Benchmark Agent: compares candidate architecture against the current GOX baseline.
- QA/Judge: verifies the resulting integration before GOX treats it as usable.
- Provenance Keeper: records source repository, commit/tag, license, files studied, pattern adopted, changes made, tests, and outcome.

## System-Wide Trigger Rule
Run this swarm automatically when:
- a new subsystem is being designed,
- a capability is blocked,
- a component repeatedly fails,
- a workflow is too tedious or owner-dependent,
- GOX performance is materially below target,
- a major implementation decision has multiple plausible architectures,
- a successful workflow could potentially be improved by an established open-source pattern.

## Repository Selection Score
Rank candidate repositories using:
1. relevance to the exact GOX capability,
2. evidence of real execution rather than demo-only claims,
3. recent maintenance/activity,
4. quality of tests and documentation,
5. issue/PR health,
6. architecture fit with GOX,
7. deployment simplicity,
8. license compatibility,
9. dependency/operational cost,
10. measurable improvement over current GOX baseline.

Popularity or star count alone is never enough.

## Reuse Modes
### A. Direct reuse
Allowed only when the license permits it and required notices/attribution are preserved.

### B. Adapted reuse
Use compatible code with GOX-specific modifications while preserving license obligations and provenance.

### C. Clean-room implementation
Study architecture/behavior, then write original GOX code without copying source text when licensing is absent, incompatible, or direct reuse is unnecessary.

### D. Reject
Reject repositories that depend on credential theft, CAPTCHA bypass, anti-bot evasion, malware, unauthorized access, deceptive marketplace behavior, or other unacceptable practices.

## Mandatory Rules
- No explicit license = architecture reference only; do not copy source code.
- Preserve required notices for compatible open-source licenses.
- Do not copy secrets, credentials, proprietary data, CAPTCHA bypasses, anti-bot bypasses, or access-control evasion.
- Prefer official APIs and permitted authenticated browser workflows when available.
- Never claim a borrowed pattern improved GOX until it passes real tests against the baseline.
- Failed adoptions are recorded so GOX does not repeatedly retry the same bad pattern.

## Provenance Ledger
Record every serious candidate and adopted pattern in `research/GITHUB_PATTERN_LEDGER.md` with:
- capability/gap,
- repository and reference commit/tag,
- license,
- why it was shortlisted,
- architecture learned,
- files/modules reused (if any),
- GOX files changed,
- tests performed,
- before/after metrics,
- final decision: ADOPT / ADAPT / REBUILD / REJECT.

## Execution Loop
CAPABILITY OR GAP
-> PARALLEL SEARCH
-> SHORTLIST
-> SUCCESS CHECK
-> LICENSE CHECK
-> ARCHITECTURE MAP
-> BENCHMARK AGAINST GOX
-> CHOOSE REUSE MODE
-> BUILD/ADAPT
-> TEST
-> JUDGE
-> INTEGRATE
-> RECORD PROVENANCE
-> CONTINUOUSLY RECHECK BETTER PATTERNS

## Prime Directive
Do not reinvent a solved problem without first checking whether a proven, compatible implementation or architecture can save GOX time, owner effort, or money.