# GOX CEO ESCALATION LAYER

Purpose: surface blockers to the owner immediately and minimize technical babysitting.

## Owner Role
The owner is the strategic controller for GOX and the family system. GOX should absorb implementation, monitoring, debugging, research, drafting, and routine operations. The owner should be interrupted only when an action genuinely requires the owner or a specific family member.

## Escalation Triggers
Create an owner alert when any of these occur:
- authentication/login expired
- MFA or CAPTCHA required
- identity verification required
- legal/tax/payment attestation required
- final consequential submit requires the applicant
- platform rules require the actual worker to act
- runtime or bridge failure cannot be auto-repaired safely
- repeated job failure exceeds retry budget
- duplicate-submit risk
- account-lockout or security risk
- payout/account problem
- a first-dollar task is ready but blocked on one missing owner fact

Do NOT alert for routine retries, logs, harmless warnings, recoverable service restarts, or technical details the system can resolve itself.

## Alert Payload
Every alert must contain:
- severity: INFO / ACTION / URGENT
- family lane / applicant
- exact blocker
- why human action is required
- minimum action requested
- exact page or approval target if available
- what GOX will automatically resume afterward
- timeout or deadline if any
- safe deny/cancel path

## Voice-First Owner Experience
Target interaction:
1. GOX detects an owner gate.
2. GOX raises an alert through the available notification channel.
3. Owner opens the alert and can say or tap: APPROVE, DENY, OPEN, RETRY, or EXPLAIN.
4. If authentication/MFA/CAPTCHA is required, GOX presents the exact browser state without logging the secret response.
5. GOX detects completion and resumes automatically.

## Family Authorization Model
The owner may coordinate the overall family system, but GOX must preserve each family member's identity and authorization boundaries.
- Each family member has a separate lane, profile, browser/session, credentials, application history, and revenue ledger.
- The owner may prepare, monitor, and coordinate work where authorized.
- Identity verification, signatures, legal/tax declarations, personal account permissions, and actions a platform requires the actual applicant to perform must be completed or explicitly authorized by that person.
- Never share credentials across family lanes.

## Notification Channels
Priority architecture:
1. ChatGPT/in-app owner-gate notification for the current control surface.
2. Secure mobile/web approval bridge with push-capable PWA/companion.
3. Optional SMS/voice-call provider adapter if the owner configures a provider and verified phone destination.
4. Email fallback only for non-urgent issues.

No phone-number, API token, or provider credential belongs in source control.

## Escalation API Contract
Suggested internal event:
```json
{
  "event":"owner_gate",
  "job_id":"...",
  "family_lane":"...",
  "severity":"ACTION",
  "title":"GitHub authentication required",
  "reason":"Session expired",
  "action":"Open approval page and complete device authorization",
  "resume_action":"bridge_finisher",
  "expires_at":null
}
```

## Resilience
- persist alerts before delivery
- deduplicate identical active alerts
- acknowledge/resolve states
- resend only on meaningful state changes or deadline escalation
- never lose an unresolved owner gate across restart
- record audit metadata without secrets

## First-Dollar Rule
Revenue blockers receive priority over non-revenue build alerts. Infrastructure work should not interrupt the owner unless it directly blocks the paid-work loop or creates a security risk.
