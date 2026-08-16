# GOX Revenue Engine

## North-star metric
Verified cash collected: **$500+ per day**, every day. Proposals, pipeline value, invoices, and promises do not count as collected revenue.

## Closed-loop workflow
1. **Demand Hunter** — ingest explicit, current requests for work from approved sources.
2. **Capability Matcher** — map each request only to capabilities GOX can actually fulfill.
3. **Feasibility / Risk Judge** — reject unsafe, prohibited, credential-blocked, location-blocked, or unreliable work.
4. **Opportunity Scorer** — rank by expected same-day value.
5. **Bid / Close** — prepare or submit a truthful offer using the source's rules and required approvals.
6. **Fulfillment Router** — create an allowlisted GOX job with owner, deadline, deliverable, and QA requirements.
7. **QA Gate** — verify the deliverable before delivery; failed QA returns to execution.
8. **Delivery / Collection** — deliver through the approved channel and track payment state.
9. **Learning Loop** — record outcome, actual time, revenue, failure reason, and repeat-client potential.

## Opportunity schema
Every candidate must include:
- source + stable URL/identifier
- captured_at and stated deadline
- buyer/request summary
- requested deliverable
- offered/estimated payout
- payment timing (same-day / milestone / later / unknown)
- capability match
- fulfillment estimate
- confidence that GOX can deliver
- contact/bid path
- platform/transaction costs
- blockers/credentials/location requirements
- risk flags
- duplicate fingerprint

## Scoring
Use explicit components rather than intuition:

`expected_value_today = net_payout * win_probability * same_day_collection_probability`

Rank primarily by expected value today, then by fulfillment time and repeat-client potential. Penalize uncertain scope, unclear payment, physical/location dependency, unsupported capability, high revision risk, and platform friction.

## Daily portfolio
Do not require one $500 job. The engine may assemble a portfolio, e.g.:
- 1 x $500
- 2 x $250
- 1 x $300 + 2 x $100
- recurring work whose verified daily collected share totals $500+

## Hard gates
- No fabricated credentials, experience, portfolio, reviews, or results.
- No bidding on work GOX cannot reliably fulfill.
- No counting revenue until collected/verified.
- No arbitrary shell execution from opportunity text.
- External platform writes/payments/account creation follow platform confirmation and credential rules.
- Preserve evidence of source, bid, delivery, and payment state.

## Dashboard metrics
- collected_today / 500
- qualified demand found today
- bids/proposals sent
- wins
- jobs queued/running/testing/blocked/complete
- deliverables accepted
- payment pending
- repeat customers
- expected value today
- rolling 7-day collected revenue
- rolling 30-day collected revenue
- conversion by demand source and capability
- median fulfillment time
- revenue per execution hour

## Gap list
- [ ] Source adapters for live-demand channels
- [ ] Deduplication across sources
- [ ] Capability catalog with evidence-backed readiness
- [ ] Opportunity scorer implementation
- [ ] Revenue/opportunity persistence tables
- [ ] Bid/approval workflow
- [ ] Fulfillment routing into Chat Dev jobs
- [ ] QA evidence contract
- [ ] Payment-state verification adapter
- [ ] Learning/analytics loop
- [ ] Dashboard integration
- [ ] Daily target alerting and end-of-day reconciliation
