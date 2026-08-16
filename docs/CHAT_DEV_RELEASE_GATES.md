# Chat Dev Release Gates

Chat Dev is not considered complete until every required gate is verified on the target host.

## 1. Source and rollback
- [x] Work isolated on `agent/chat-dev-foundation`.
- [ ] Review branch diff and open PR.
- [ ] Record deployed commit SHA.
- [ ] Verify rollback to prior commit/service state.

## 2. Runtime
- [x] Browser control surface exists.
- [x] `/health` endpoint exists.
- [x] SQLite WAL persistence exists.
- [x] Messages create durable queued jobs.
- [x] Worker claims jobs transactionally.
- [x] User text is never passed directly to a shell.
- [ ] Add named specialist adapters for real GOX capabilities.
- [ ] Add leases/recovery for a worker that dies while a job is `running`.
- [ ] Add bounded retry policy and quarantine/dead-letter state.

## 3. Security
- [x] App service defaults to loopback only.
- [x] Example TLS/auth reverse-proxy boundary documented.
- [x] systemd hardening baseline included.
- [ ] Create production credentials outside Git/repo.
- [ ] Verify firewall exposes only required ports.
- [ ] Verify no secrets are committed or logged.
- [ ] Add request/session authentication inside the app before multi-user use.
- [ ] Add CSRF/session protections if cookie-based auth is introduced.

## 4. Operations
- [x] Separate web and worker service definitions exist.
- [ ] Add SQLite backup/restore procedure and test restore.
- [ ] Add disk-space/log rotation checks.
- [ ] Add service health monitoring/restart alert.
- [ ] Define data retention policy.

## 5. Testing
- [x] Repeatable smoke-test script exists.
- [ ] Run smoke test on target VPS.
- [ ] Test service restart with queued jobs preserved.
- [ ] Test worker crash/recovery.
- [ ] Test malformed requests and oversized input.
- [ ] Test authentication failure/success.
- [ ] Run repeated tests after every major integration.

## 6. User acceptance
- [ ] User can open Chat Dev from their normal device.
- [ ] User can submit a real safe task.
- [ ] User can visibly see queued/running/testing/blocked/complete state.
- [ ] Result is returned and history remains after restart.
- [ ] User personally confirms the workflow is understandable and useful.

## Current blocking dependency
We need authenticated administrative access to the active deployment host (or another approved deployment target) to install the branch, run host-level tests, configure TLS/auth, and perform user acceptance testing.
