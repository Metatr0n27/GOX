# GOX Paper Stack — Truth Audit

Status vocabulary:
- **VERIFIED** — executed/tested with evidence in the intended environment.
- **BUILT / UNVERIFIED** — implementation exists but has not passed the required real-environment tests.
- **MISSING** — required implementation/process does not yet exist.
- **EXTERNAL BLOCK** — depends on access/approval/system unavailable to the current agent environment.

Nothing is promoted to VERIFIED merely because a file exists in GitHub.

| Layer | State | What exists | Main gap to next state |
|---|---|---|---|
| Product goal | BUILT / UNVERIFIED | Chat Dev requirements + release gates | Hands-on user acceptance |
| Source control | BUILT / UNVERIFIED | canonical GOX repo, feature branch, release branch | PR/review/branch protection/release evidence |
| Chat UI | BUILT / UNVERIFIED | browser chat + live status polling | deployed-device testing, UX/error refinement |
| HTTP/API | BUILT / UNVERIFIED | health/status/jobs/chat endpoints, size limits | deployed auth/abuse/concurrency tests |
| Job persistence | BUILT / UNVERIFIED | SQLite WAL durable queue/history | process/restart/concurrency tests |
| Worker resilience | BUILT / UNVERIFIED | leases, stale recovery, retries, quarantine | real worker-kill tests + idempotency |
| Capability boundary | BUILT / UNVERIFIED | allowlisted adapter registry | real specialist adapters + enforced timeout |
| Agent orchestration | MISSING | role/team design and older Orchestra reference | production-safe dispatcher, budgets, cancellation |
| Authentication | BUILT / UNVERIFIED | in-app Basic Auth + proxy example | production secret, brute-force protection, tests |
| Authorization | MISSING | single-user assumption | explicit permission model before multi-user/privileged adapters |
| Secrets | MISSING | documented boundary only | inventory, storage mechanism, rotation/revocation, leak scan |
| TLS/network | EXTERNAL BLOCK | nginx example + loopback default | configure/test DNS, certs, firewall on VPS |
| Deployment | BUILT / UNVERIFIED | systemd units + pull deploy + rollback design | one-time VPS bootstrap and real rollback test |
| Backups | BUILT / UNVERIFIED | SQLite online backup utility | off-host retention + restore drill |
| Database migrations | PARTIAL | additive column migration | schema versioning and tested forward migration |
| Observability | MISSING | health endpoint + systemd restart | structured logs, metrics, alerts, disk/resource monitoring |
| Incident response | PARTIAL | emergency worker/deploy stop | severity/runbook/recovery objectives/evidence policy |
| CI/release QA | MISSING | local test scripts | automated CI + release evidence artifact |
| Failure testing | PARTIAL | smoke/revenue tests | process kill, concurrency, corruption, restart, auth tests |
| Demand discovery | MISSING | Revenue Engine design/schema | live approved source adapters |
| Capability readiness | MISSING | conceptual capability matching | evidence-backed catalog of what GOX can deliver now |
| Opportunity scoring | BUILT / UNVERIFIED | deterministic EV scoring | calibration from real outcomes and net-cost inputs |
| Sales/bidding | MISSING | workflow definition | platform-specific compliant bid/approval adapters |
| Fulfillment routing | MISSING | Chat Dev job framework | qualified opportunity -> scoped job -> owner/deadline/QA |
| Deliverable QA | MISSING | QA role concept | evidence contract/test per work category |
| Delivery | MISSING | workflow definition | source-specific delivery adapters and acceptance state |
| Payments | MISSING | revenue evidence table | real payment-state verification integration |
| Revenue accounting | PARTIAL | collected-event gate | costs, fees, refunds, disputes, reconciliation, bookkeeping |
| Revenue dashboard | MISSING | UI target currently hard-coded | compute from persisted verified events |
| Learning loop | MISSING | metrics specified | actual outcome ingestion and source/capability optimization |
| Customer lifecycle | MISSING | repeat-client concept | CRM state, revisions, support, retention, recurring work |
| Platform compliance | MISSING | hard-gate principles | platform inventory + automation/API rules per source |
| Data governance | MISSING | basic security intent | classification, retention, deletion, customer isolation |
| Cost controls | MISSING | none enforced | per-job budget, model/API ceilings, kill conditions |
| Abuse/scam defense | MISSING | none implemented | opportunity/payment scam screening and suspicious-link handling |
| Business continuity | PARTIAL | deployment rollback + DB backup design | host-loss restore, alternate host plan, tested RTO/RPO |
| User acceptance | EXTERNAL BLOCK | acceptance criteria documented | deployed URL + real task + user's personal approval |

## Critical path to first usable Chat Dev
1. Add automated CI and finish high-value local tests.
2. Add at least one useful, safe specialist adapter.
3. Enforce adapter timeout/idempotency/resource ceilings.
4. Bootstrap deployment bridge on active VPS (external access boundary).
5. Configure/test TLS, authentication, firewall, monitoring and backups.
6. Run failure/restart/rollback/restore tests on host.
7. Put URL on user's normal device and complete hands-on acceptance.

## Critical path to $500+/day system
1. Build capability-readiness catalog from tested GOX abilities.
2. Connect approved live-demand sources where buyers already request work.
3. Deduplicate/expire/score demand using real net costs and payment timing.
4. Route only feasible wins into scoped fulfillment jobs.
5. Require QA evidence before delivery.
6. Verify payment before revenue is counted.
7. Track net margin, revisions/refunds/nonpayment and revenue per execution hour.
8. Feed outcomes back into source/capability prioritization.
9. Grow repeat/recurring work so each day does not restart at $0 pipeline.

## Definition of done
**Chat Dev:** user opens it from their normal device, submits a useful task, observes truthful state transitions, receives a verified result, and history survives restart.

**Revenue engine:** GOX repeatedly discovers legitimate demand, wins work truthfully, fulfills and QA-checks it, verifies collection, and sustains at least $500/day collected revenue with positive net margin. This is a performance target, not a guaranteed outcome.
