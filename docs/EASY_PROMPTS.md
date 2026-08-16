# Easy Prompts

**Easy Prompts** is the renamed replacement for the earlier PromptsOps idea.

Goal: let the GOX owner ask for an outcome in plain language and have GOX perform the repetitive operational sequence safely, with status, tests, rollback, and only necessary approvals.

## Design rules
- Plain-language trigger, structured execution underneath.
- Prefer read-only inspection before changes.
- Snapshot/backup before risky state changes.
- Never kill or restart an unidentified process/service.
- Never overwrite unrelated workspaces.
- Use allowlisted adapters, not arbitrary user-to-shell execution.
- Show `RUNNING / TESTING / BLOCKED / COMPLETE` state in ChatDev.
- Return evidence: service state, health result, commit SHA, test output, payment state, etc.
- Stop for secrets, billing, destructive changes, or ambiguous production targets.

## Starter Easy Prompts

### 1. "Check GOX"
Inspect GOX services, ports, health endpoints, disk, recent failures, deployment SHA, queue state, and revenue engine. Report only actionable problems.

### 2. "Fix ChatDev"
Diagnose ChatDev web/worker failures, identify the exact failing layer, apply only safe/reversible fixes, restart only affected GOX services, and rerun health + end-to-end tests.

### 3. "Deploy ChatDev"
Confirm the approved release branch, verify tests/CI, snapshot current deployment state, deploy the approved SHA, health-check, run end-to-end tests, and automatically roll back on failure.

### 4. "Test everything"
Run adapter, revenue, smoke, restart/persistence, worker-recovery, auth, request-limit, backup-integrity, and deployment-health tests. Do not mark a test passed without evidence.

### 5. "Why is this broken?"
Collect service status, journal tail, process/port ownership, working directory, environment, current SHA, and dependency state. Produce the root cause before changing anything.

### 6. "Make a safety backup"
Snapshot relevant git diffs/status plus application data using the approved backup path. Verify the backup exists and is readable; do not overwrite the live system.

### 7. "Restart ChatDev safely"
Verify which ChatDev services are targeted, record pre-restart status, restart only those services, verify health/worker state, and confirm persistent job history remains.

### 8. "Roll back ChatDev"
Identify the last known-good deployment SHA, preserve current logs/data, switch only the ChatDev release to that version, restart affected services, verify health, and record rollback evidence.

### 9. "Audit exposed ports"
List listening ports, owning process/service, bind address, and whether each exposure is intentional. Do not kill anything. Flag unnecessary `0.0.0.0`/public listeners for approval.

### 10. "Show me where we're at"
Generate the current paper-stack status: VERIFIED, BUILT/UNVERIFIED, MISSING, EXTERNAL BLOCK. Include ChatDev readiness, revenue-engine readiness, active blockers, and the next highest-value actions.

### 11. "Find money GOX can do"
Find explicit current demand, match only against verified GOX capabilities, score expected collected value today, reject unsupported/risky work, and surface the best legitimate opportunities for execution.

### 12. "Run the $500/day engine"
Review qualified demand, active bids, won work, fulfillment/QA state, payment pending, collected revenue, costs, and repeat-client opportunities. Prioritize the actions most likely to increase verified collected revenue today.

## Next implementation step
Expose these as a catalog in ChatDev so the user can click an Easy Prompt or type its natural-language name. Each prompt should resolve to a versioned workflow definition with permission class, required adapters, evidence requirements, timeout, rollback behavior, and approval gates.
