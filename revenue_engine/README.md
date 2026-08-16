# Easy Prompts — Demand-to-Cash

Goal: turn explicit buyer demand into verified collected revenue with as little owner busywork as possible.

## Agent team

1. **Scout** — ingests public, permitted buyer-demand sources and deduplicates opportunities.
2. **Qualifier** — rejects weak/no-budget demand and matches jobs only to verified GOX capabilities.
3. **Closer** — drafts a truthful, tailored proposal and price. Marketplace submission remains owner-gated where account/platform action is required.
4. **Builder** — creates the fulfillment job only after the opportunity is won.
5. **QA** — tests deliverables against the buyer's stated acceptance criteria before release.
6. **Cashkeeper** — records revenue only when payment is actually collected; proposals/invoices do not count as revenue.

## State machine

`DISCOVERED -> QUALIFIED -> PROPOSAL_READY -> SUBMITTED -> WON -> BUILDING -> QA -> DELIVERED -> PAID`

Failure/rejection states are explicit and auditable.

## Safety / operating rules

- Prefer explicit purchase intent over unsolicited mass outreach.
- Never fabricate portfolio items, credentials, testimonials, delivery history, or capabilities.
- Do not auto-submit through a user's marketplace identity unless the platform integration and authorization explicitly permit it.
- Do not start costly fulfillment before a job is won/authorized.
- Count only collected funds as revenue.
- Keep existing GOX services isolated from revenue experiments.

## Initial implementation

`demand_to_cash.py` contains the deterministic core for opportunity intake, verified-capability qualification, proposal drafting, fulfillment gating, and collected-revenue accounting.

Next integration boundary: connect Scout adapters to permitted demand feeds and route `PROPOSAL_READY` items into Easy Prompts for owner approval/submission when required.
