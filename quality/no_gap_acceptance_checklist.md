# GOX NO-GAP ACCEPTANCE CHECKLIST

Status: ENFORCED

GOX is not considered production-ready or first-dollar-ready until every CRITICAL item below is PASS with evidence.

## CRITICAL PATH

### 1. Voice / Owner Control
- [ ] Wake companion can alert owner when a real gate exists.
- [ ] Voice acknowledgement is received.
- [ ] Pending gate is shown clearly.
- [ ] Approve / deny / explain / open actions work.
- [ ] CAPTCHA/MFA stays human-only.
- [ ] System resumes after gate completion.

### 2. Approval Bridge
- [ ] Approval API reachable through intended secure path.
- [ ] Owner authentication works.
- [ ] Internal automation authentication works.
- [ ] Pending / approved / denied states persist across restart.
- [ ] No secrets appear in logs, URLs, repo, or alerts.

### 3. Remote Steward
- [ ] Service active.
- [ ] GitHub pull works.
- [ ] Command file is detected.
- [ ] Allowlisted command executes.
- [ ] Result JSON is written.
- [ ] Result JSON is pushed back to GitHub.
- [ ] Redaction verified.
- [ ] Duplicate command is not re-executed unsafely.

### 4. Agent Runtime
- [ ] Claude/runtime authentication valid.
- [ ] Noninteractive smoke test completes within timeout.
- [ ] Canonical prompt can launch agent run.
- [ ] Three independent agents complete.
- [ ] Outputs persist.
- [ ] Synthesis completes.
- [ ] Judge returns PASS or repair instruction.

### 5. Execution Bridge
- [x] Unit tests previously passed.
- [ ] Real end-to-end run completes on VPS.
- [ ] Failure path creates useful evidence.
- [ ] Retry/repair does not duplicate consequential actions.

### 6. ChatDev Cockpit
- [ ] PM role visible.
- [ ] Developer role visible.
- [ ] Tester role visible.
- [ ] Reviewer role visible.
- [ ] Live state/logs visible.
- [ ] Repair loop visible.
- [ ] PASS/BLOCKED result visible.
- [ ] Owner gate routes to approval bridge.

### 7. Easy Jobs / First-Dollar Pipeline
- [ ] Current legitimate opportunity source connected.
- [ ] Platform rules checked.
- [ ] Family member eligibility checked.
- [ ] Correct resume packet selected.
- [ ] Resume tailored truthfully.
- [ ] Application answers generated from verified facts only.
- [ ] Owner/applicant authorization boundary respected.
- [ ] Submission confirmation recorded.
- [ ] Paid work completed under platform rules.
- [ ] First verified net dollar recorded.

### 8. Family Identity Separation
- [ ] Separate profile per person.
- [ ] Separate account/session per person.
- [ ] Separate credentials/secrets per person.
- [ ] Separate application history.
- [ ] Separate earnings ledger.
- [ ] No cross-account impersonation.

### 9. Revenue Ledger
- [ ] Gross amount recorded.
- [ ] Fees recorded.
- [ ] Net amount recorded.
- [ ] Owner minutes recorded.
- [ ] Compute/tool cost recorded when known.
- [ ] Payout status recorded.
- [ ] Expected revenue is separate from earned revenue.
- [ ] Evidence links/IDs recorded.

### 10. Recovery / Safety
- [ ] Restart resumes unfinished non-consequential jobs safely.
- [ ] Consequential actions require idempotency/deduplication.
- [ ] Kill switch works.
- [ ] Backups exist before destructive changes.
- [ ] Non-root production service plan exists.
- [ ] Secrets can be rotated.
- [ ] Alerts deduplicate and persist.

## CURRENT KNOWN GAPS
1. Remote Steward result directory / return channel is not currently visible in GitHub; end-to-end return path remains unproven.
2. Real Claude/runtime ensemble evidence is still missing.
3. Execution bridge real-run evidence is still missing.
4. ChatDev cockpit is not yet operational.
5. Wake companion is a prototype; production background/push behavior is not yet proven.
6. Approval bridge production mobile pairing/secure exposure is not yet proven.
7. Live first-dollar applications have not yet been submitted and paid.
8. Revenue remains $0 verified until actual payout evidence exists.

## RELEASE RULE
Do not report GOX as complete, autonomous, first-dollar-ready, or production-ready while any CRITICAL checkbox remains unverified. Report exact blockers instead.
