# GOX Revenue Launch Gap Register

## Objective
Move from repository architecture to verified revenue execution with minimum owner effort.

## P0 - Blocks Autonomous Revenue
1. **Repository visibility** — GOX is currently PUBLIC. Target policy is PRIVATE for proprietary core. Current GitHub connector does not expose repository-visibility mutation; owner/admin UI or another authenticated GitHub administration path is required once.
2. **VPS execution authentication** — SSH connector code exists, but runtime still needs GOX_VPS_HOST, GOX_VPS_USER and access to a VPS-authorized private key plus known-host verification.
3. **Running worker/scheduler** — hourly hunt/job cells must be launched by an actual persistent process on the VPS; Markdown team definitions do not execute themselves.
4. **Authenticated revenue channels** — each marketplace/research/direct-outreach channel needs a permitted logged-in session/API/connector before autonomous actions can occur.
5. **Payment collection path** — direct-service offers need an owner-controlled method to receive payment and payment evidence before GOX can mark revenue collected.

## P1 - Required for Reliable Scaling
6. Opportunity ingestion adapters for selected channels.
7. Durable job-cell state/queue so restarts do not lose work.
8. Submission/outreach rate limits and platform-specific policy constraints.
9. Central structured logs, incident IDs, and retry/dead-letter handling.
10. Revenue ledger separating advertised payout, expected value, invoiced value, and cash actually collected.
11. Fulfillment acceptance tests for each service sold.
12. Owner-action queue that batches MFA/CAPTCHA/identity/terms gates without stopping unrelated cells.
13. Secrets storage/rotation and no-secret-in-Git verification.
14. Backup/rollback for VPS worker and known-good GOX revision.

## P2 - Optimization
15. Conversion analytics by channel/offer/price.
16. A/B testing of proposals and service packages.
17. Recurring-client upsell and retention workflows.
18. Cost accounting for tools/agents versus collected revenue.
19. GitHub Pattern Mining comparisons before major rebuilds.
20. Periodic regression tests of all known-good revenue workflows.

## Launch Order
PRIVATE CORE -> VPS AUTH -> WORKER RUNNING -> AUTHENTICATED CHANNELS -> PAYMENT PATH -> HOURLY HUNT -> JOB CELLS -> FIRST PAYMENT -> MEASURE -> SCALE WINNER

## Definition of LIVE
GOX is LIVE only when a persistent worker has completed a real opportunity cycle, created at least one real Job Cell, performed the permitted external actions, recorded evidence, and can continue after restart. Revenue is EARNED only when payment evidence exists.
