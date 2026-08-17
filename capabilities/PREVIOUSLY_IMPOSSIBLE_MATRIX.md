# GOX Previously Impossible -> Buildable -> Owner-Only Matrix

Purpose: convert old 'can't do that' answers into concrete engineering work wherever possible.

| Capability | Previous State | New State | What GOX Builds | Owner-Only Gate | Done When |
|---|---|---|---|---|---|
| Authenticated marketplace browsing | No authenticated browser tool in chat | BUILDABLE | Persistent Playwright/browser-use session layer, service profiles, session verification, recovery | First login/MFA/CAPTCHA when required | Session persists and real authenticated page is verified |
| Proposal submission workflows | Could prepare but not submit | BUILDABLE AFTER AUTH | Service-specific browser operator, form mapping, validation, screenshots, submission evidence | Contract/terms acceptance if platform requires explicit owner action | Proposal submitted and platform confirmation captured |
| Marketplace job monitoring | Search only / manual account state | BUILDABLE | Authenticated watcher, normalized job ingestion, dedupe, ranking, alerts | Initial account login if private feed needed | New jobs are ingested/deduped automatically |
| File upload to buyer/platform | No browser session | BUILDABLE AFTER AUTH | Browser uploader with file validation and receipt evidence | Owner approval if upload creates irreversible commitment | Correct file visible on platform and receipt/screenshot stored |
| Buyer-message handling | Limited to connected channels | BUILDABLE BY CHANNEL | Gmail/API/browser adapters; read-first response workflow | Owner action only for sensitive commitments | Message read, response sent, thread evidence captured |
| Payment-account readiness | Could inspect connected evidence only | PARTLY BUILDABLE | Payment-provider API/browser checks, status diagnostics, checkout tests | Identity/KYC, banking, financial authorization | Real payment path passes live/sandbox verification as appropriate |
| Accepting contracts/terms | Cannot impersonate owner assent | OWNER-ONLY | Everything before/after acceptance automated | Explicit owner legal assent | Owner accepts; GOX captures confirmation and resumes |
| MFA/CAPTCHA/identity checks | Cannot bypass | OWNER-ONLY | Detect gate, preserve session, resume automatically after completion | Owner completes challenge | Authenticated state verified after challenge |
| Browser task automation | No authenticated session | BUILDABLE | browser-use/Playwright-inspired operator, task plans, retries, screenshot logging | Initial login for protected sites | Repeatable real task succeeds in test |
| Multi-agent orchestration | Mostly conceptual agent files | BUILDABLE | Stateful supervisor-worker graph with role routing, evidence requirements, retries, checkpoints | None for internal orchestration | Agents execute tools/workflows with inspectable state and tests |
| Autonomous coding/repair | Partial Chat Dev, failing CI | BUILDABLE | Planner -> coder -> tester -> reviewer -> repair loop | Owner only for consequential release/production gates | Code change passes CI and acceptance tests |
| Secrets/session handling | Risk of accidental commit | BUILDABLE | .gitignore, secret scanning, environment isolation, session vault path | Owner provides credentials only through secure login/config paths | No secrets in Git; secret/session tests pass |
| External result verification | Claims could outrun evidence | BUILDABLE | Evidence collector and authenticity verifier | None except owner-only external gates | Every success state has external evidence |

## Priority Order by Revenue Impact
1. Authenticated marketplace/browser session verification.
2. Proposal submission operator.
3. Buyer reply/message operator.
4. Payment readiness and payment evidence.
5. Fulfillment agent loop and CI repair.
6. Delivery/upload operator.
7. Lower-value admin automation.

## Governing Rule
A capability moves from BLOCKED to BUILDABLE whenever GOX can create a legitimate connector, API, persistent browser session, local/VPS runtime, or tested open-source-derived implementation. Owner-only gates remain owner-only; GOX automates everything immediately before and after them.