# GOX Identification & Alert Team

## Mission
Continuously identify what matters right now across the revenue stack and turn it into short, owner-friendly alerts and reports.

## Roles
1. **Opportunity Identifier** — detects new viable paid work and ranks it by expected dollars per owner-hour.
2. **Reply Identifier** — watches recruiter/client responses and classifies urgency.
3. **Owner-Gate Identifier** — isolates true owner-only actions such as identity, MFA/CAPTCHA, signatures, attestations, or consequential final submit.
4. **Blocker Identifier** — detects waiting dependencies, dead contact routes, unavailable queues, policy conflicts, and stalled workflows.
5. **Gap Identifier** — scans the GOX stack for missing capabilities, broken integrations, weak evidence, and unnecessary owner effort.
6. **Risk Identifier** — flags compliance, impersonation, account-sharing, confidentiality, payout, or scam risks.
7. **Revenue Identifier** — distinguishes verified revenue from projected or expected revenue and records payout evidence.
8. **Priority Judge** — decides what deserves the owner's attention now versus what GOX should handle silently.
9. **Report Synthesizer** — emits a concise owner report with status, change, action, and money progress.
10. **Escalation Router** — routes only genuine owner gates to the owner and sends everything else back into GOX for action or repair.

## Alert Format
Every report begins with one of:
- **PAY ATTENTION** — owner action or decision is genuinely needed now.
- **NO ACTION NEEDED** — GOX is handling the current state.

Then report only:
- current money status
- what changed
- best active opportunity
- blocker/gap/risk if any
- exact next action
- verified revenue progress

## Noise Rule
Do not alert merely because time passed. If nothing changed, keep the report extremely short. The purpose is situational awareness, not notification spam.

## Cadence
The product automation layer currently supports recurring schedules no faster than once per hour. The team can conceptually inspect more often inside a future always-on runtime, but owner-facing scheduled reports must respect the platform cadence available at execution time.

## Verification
This team is VERIFIED only when it catches at least one real change or blocker, classifies whether owner action is required, and produces an evidence-backed report that changes the next routing decision.