# GOX GitHub Pattern Ledger

This file records external open-source projects studied for GOX, what was learned, the license status, and whether any code was directly reused.

| Source | Purpose | License Status | GOX Use | Direct Code Reuse? | Notes |
|---|---|---|---|---|---|
| `mfahadrehan/upwork-discord-bot` | Upwork job ingestion, deduplication, persistence, notifications, token/session maintenance | No explicit license verified during initial review | Architecture reference only | No | Useful pattern: ingest -> normalize -> dedupe -> persist -> notify. Cloudflare/access-control bypass techniques are excluded from GOX. |

## Required Review Before Adoption
For every future source:
1. Verify repository activity and completeness.
2. Inspect LICENSE/COPYING/NOTICE.
3. Classify direct reuse rights.
4. Extract architecture and test strategy.
5. Rebuild cleanly when license is absent/incompatible.
6. Add verification evidence before marking integrated.
