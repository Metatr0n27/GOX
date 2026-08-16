# GOX Chat Dev Agent Team

This file defines the execution team for finishing Chat Dev with minimal user involvement.

## Coordinator — Release Captain
Owns sequencing, dependency tracking, acceptance gates, and final user handoff. Does not bypass failed tests or security gates.

## Agent 1 — Resilience Engineer
Owns worker leases, stale-job recovery, bounded retries, dead-letter/quarantine handling, idempotency, and restart safety.

Acceptance:
- a killed worker does not strand jobs forever
- retries are bounded
- repeatedly failing work is quarantined with a visible reason
- duplicate execution is prevented where practical

## Agent 2 — Capability Bridge Engineer
Owns named specialist adapters between Chat Dev and GOX capabilities. Never forwards arbitrary user text to a shell.

Acceptance:
- every executable capability has a stable name, validated input schema, timeout, result schema, and explicit permission class
- unsupported capabilities become `blocked`, not improvised shell commands
- adapter tests cover success, timeout, malformed input, and failure

## Agent 3 — Security Engineer
Owns authentication, session design, request limits, secret boundaries, TLS assumptions, and secure defaults.

Acceptance:
- unauthenticated remote requests cannot use Chat Dev
- secrets live outside Git
- loopback remains the default app bind
- request size/rate controls are defined
- security failures are logged without leaking credentials

## Agent 4 — Platform / VPS Engineer
Owns install, system users, directories, systemd units, reverse proxy, firewall, TLS, backups, rollback, and deployed commit recording.

Acceptance:
- both services start after reboot
- only required ports are exposed
- health checks pass on-host
- rollback is documented and tested
- backup and restore are tested on a non-production copy

## Agent 5 — QA / Failure Injection Engineer
Owns repeated tests and adversarial operational testing.

Acceptance:
- smoke test passes repeatedly
- queued jobs survive web/worker restarts
- worker crash recovery is proven
- malformed/oversized requests fail safely
- authentication success/failure is tested
- persistence survives restart
- user-visible states match backend state

## Agent 6 — UX / Acceptance Engineer
Owns the control-board experience and user acceptance path.

Acceptance:
- user sees queued/running/testing/blocked/complete
- errors are understandable without reading logs
- history is visible after restart
- user can complete one real safe task from their normal device
- user personally approves usability before release is called complete

## Operating rule
Agents may perform safe, reversible internal work automatically. They stop for credentials, destructive production changes, billing, irreversible migrations, or other consequential approvals.

## Dependency order
Resilience + capability contract -> security -> VPS deployment -> failure testing -> user acceptance.

Parallel work is encouraged where dependencies allow it.
