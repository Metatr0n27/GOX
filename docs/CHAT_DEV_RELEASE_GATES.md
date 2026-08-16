# Chat Dev Release Gates

Chat Dev is not considered complete until every required gate is verified on the target host. A checked implementation item means code/config exists; host verification remains separate.

## 1. Source and release control
- [x] Work isolated on `agent/chat-dev-foundation`.
- [x] Dedicated production release branch `release/chat-dev` exists.
- [x] Pull-based deployment bridge with health-check rollback exists.
- [ ] Review full branch diff and open PR.
- [ ] Define/update production release approval procedure.
- [ ] Record deployed commit SHA on target host.
- [ ] Verify rollback on target host.
- [ ] Verify release branch cannot advance accidentally through an automated feature workflow.

## 2. Runtime
- [x] Browser control surface exists.
- [x] `/health` endpoint exists.
- [x] SQLite WAL persistence exists.
- [x] Messages create durable queued jobs.
- [x] Worker claims jobs transactionally.
- [x] User text is never passed directly to a shell.
- [x] Lease fields and stale-running recovery are implemented.
- [x] Bounded retries and quarantine/dead-letter state are implemented.
- [x] Allowlisted adapter registry exists.
- [ ] Enforce adapter execution timeouts.
- [ ] Add first real, useful GOX specialist adapter against a verified runtime/API.
- [ ] Add idempotency keys for every side-effecting adapter.
- [ ] Define cancellation semantics for queued/running work.
- [ ] Define concurrency/resource limits.

## 3. Security
- [x] App service defaults to loopback only.
- [x] App refuses non-loopback bind without an auth secret.
- [x] In-app Basic Auth boundary exists.
- [x] Request body limits exist.
- [x] Example TLS/auth reverse-proxy boundary documented.
- [x] systemd hardening baseline included.
- [ ] Create production credentials outside Git/repo.
- [ ] Verify firewall exposes only required ports.
- [ ] Verify repository/history/logs contain no secrets.
- [ ] Add authentication rate limiting / brute-force protection at proxy or app layer.
- [ ] Add security headers (HSTS after TLS verification, frame/content protections as appropriate).
- [ ] Define credential rotation/revocation procedure.
- [ ] Define customer-data isolation, retention, deletion, and access policy.

## 4. Data and migrations
- [x] Schema migration-by-column exists for current job fields.
- [x] Online-safe SQLite backup utility exists.
- [ ] Introduce explicit schema version/migration table before schema complexity grows.
- [ ] Test backup restore on a separate copy.
- [ ] Configure off-host backup retention.
- [ ] Test corruption/integrity failure behavior.
- [ ] Define retention/archival for job history, opportunity data, and revenue evidence.

## 5. Operations and observability
- [x] Separate web and worker service definitions exist.
- [x] Deployment history records commit SHAs.
- [x] Emergency stop procedure exists.
- [ ] Add structured application/worker logs with job IDs and redaction.
- [ ] Add log rotation and disk-space safeguards.
- [ ] Add health monitoring and alerting for web, worker, disk, database, and deployment failures.
- [ ] Add resource ceilings (CPU/memory/process/file limits) and validate them.
- [ ] Define incident severity, evidence preservation, and recovery procedure.
- [ ] Define uptime/recovery objectives appropriate for GOX.

## 6. Testing and quality
- [x] Repeatable smoke-test script exists.
- [x] Revenue-engine unit test exists.
- [x] Smoke test includes simulated expired-lease recovery path.
- [ ] Add adapter success/validation/timeout/failure tests.
- [ ] Add authentication success/failure tests.
- [ ] Add true process-kill worker recovery test.
- [ ] Test service restart with queued jobs preserved.
- [ ] Test malformed and oversized input on deployed instance.
- [ ] Test concurrent submitters/workers and database lock behavior.
- [ ] Add automated CI for syntax/tests/security checks on every proposed release.
- [ ] Run repeated tests after every major integration.
- [ ] Add a release evidence record instead of relying on checkbox claims alone.

## 7. Revenue engine
- [x] $500/day collected-revenue objective documented.
- [x] Opportunity/revenue persistence exists.
- [x] Deterministic opportunity scoring exists.
- [x] Revenue requires verification evidence before counting.
- [ ] Build approved live-demand source adapters.
- [ ] Build evidence-backed capability readiness catalog.
- [ ] Add cross-source stale/duplicate opportunity handling.
- [ ] Route qualified/won work into allowlisted fulfillment jobs.
- [ ] Define QA evidence contract per deliverable class.
- [ ] Add payment-state verification integrations.
- [ ] Track direct costs/model/API/platform fees and net margin.
- [ ] Track refunds, disputes, revisions, cancellations, and nonpayment.
- [ ] Implement learning loop by source/capability: conversion, revenue/hour, repeat rate.
- [ ] Add daily reconciliation so pending/invoiced money never counts as collected.

## 8. Compliance and platform integrity
- [ ] Inventory demand/payment platforms and their automation/API rules before source adapters go live.
- [ ] Prevent fabricated credentials, experience, portfolios, reviews, locations, or results.
- [ ] Add scam/fraud screening for incoming opportunities and payment instructions.
- [ ] Define prohibited job categories and customer-data restrictions.
- [ ] Add copyright/IP handling rules for customer deliverables.
- [ ] Define invoices/receipts/bookkeeping/tax record workflow for collected revenue.

## 9. User acceptance
- [ ] User can open Chat Dev from their normal device.
- [ ] User can submit a real safe/useful task.
- [ ] User can visibly see queued/running/testing/blocked/complete state.
- [ ] Result is returned and history remains after restart.
- [ ] Revenue dashboard uses actual persisted collected revenue, not a hard-coded value.
- [ ] User personally confirms the workflow is understandable and useful.

## Current external blocking dependency
Authenticated administrative access to the active deployment host is still required once to install/bootstrap the pull-deployment bridge, configure production TLS/credentials/firewall, and run host-level/UAT tests. The design intentionally avoids storing or handing server root credentials to GOX agents.
