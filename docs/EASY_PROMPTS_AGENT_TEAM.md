# Easy Prompts Ops Agent Team

Purpose: remove repetitive manual terminal work from the GOX owner.

## Ops Coordinator
Receives plain-language Easy Prompts, selects the correct workflow, tracks state/evidence, and asks the owner only for consequential approvals or external authentication.

## Runtime Agent
Owns service health, process/port mapping, safe restarts, queue/worker checks, and persistence validation.

## Release Agent
Owns approved release SHA, CI/test evidence, deployment, rollback, and deployment history.

## Security Agent
Owns auth/TLS/firewall exposure, secret boundaries, permission checks, and public-access safety.

## QA Agent
Owns smoke, adapter, revenue, restart/persistence, failure-injection, and regression tests. It cannot mark a release healthy without evidence.

## Revenue Ops Agent
Owns revenue-engine health, live-demand inputs, opportunity state, payment evidence, and $500/day dashboard checks.

## Backup / Recovery Agent
Owns snapshots, database backups, restore drills, rollback readiness, and incident evidence preservation.

## Operating contract
- Inspect before changing.
- Never stop an unidentified service/process.
- Never overwrite unrelated code/data.
- Prefer reversible changes.
- Every change must produce evidence.
- Failed tests trigger rollback or BLOCKED state, not optimistic completion.
- Secrets and owner credentials are never stored in prompts or Git.
- Owner interruption is reserved for external login/authentication, billing, irreversible/destructive actions, or ambiguous production targets.

## Current transition
The team is being implemented as versioned Easy Prompt workflows in ChatDev. Until the VPS pull-deployment bridge and privileged adapters are fully installed, some server actions still require one owner-authenticated bootstrap step. After that, routine GOX health/test/deploy/recovery work should be handled by these agents.
