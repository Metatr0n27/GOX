# GOX Hourly Hunt + Job Cell Swarm

## Mission
Continuously hunt for paid opportunities and give every qualified opportunity its own parallel execution cell, so one job never blocks the rest of the system.

## Layer 1: Hourly Hunt Team
Run a fresh discovery cycle every hour when the system is active.

### Hourly Roles
- Today-Pay Scout: searches same-day and next-day payout opportunities.
- Soon-Pay Scout: searches 1-3 day payout opportunities.
- Contract Scout: searches remote contract/freelance work with better expected value.
- Direct-Service Scout: searches buyers who can pay directly for a GOX-deliverable service.
- Verification Scout: checks legitimacy, payout timing, eligibility, and whether GOX can help execute.
- Profit Controller: ranks new opportunities against the existing queue and kills duplicates.

### Hourly Output
Each cycle returns only net-new or materially improved opportunities with:
- expected gross payout
- estimated probability of success
- expected payout timing
- estimated owner minutes required
- estimated GOX effort
- expected value = payout x probability
- recommended next action

## Layer 2: One Job Cell Per Opportunity
For every opportunity above the acceptance threshold, spawn one dedicated Job Cell.

### Job Cell Roles
1. Job Captain — owns the opportunity end to end.
2. Authenticity/Access Agent — confirms real access, login/session state, and owner-only gates.
3. Fit Agent — checks truthful qualification and likely acceptance probability.
4. Application/Offer Agent — prepares the application, pitch, proposal, or bid.
5. Pricing Agent — chooses a competitive price/deposit strategy for direct services.
6. Fulfillment Agent — plans and prepares the deliverable if the job is won.
7. Follow-Up Agent — tracks response timing and prepares follow-ups.
8. Evidence Agent — records submission, acceptance, delivery, and payment evidence.
9. Repair Agent — fixes workflow/tool failures for this job.
10. Profit Agent — tracks estimated versus actual dollars and owner time.

## Parallelism Rules
- Job Cells run independently and simultaneously.
- A slow or blocked job cannot pause the hourly hunt.
- Duplicate jobs are merged into one cell.
- Low-value cells are paused when stronger opportunities appear.
- More compute/agent attention goes to jobs with highest expected dollars collected soonest.

## Acceptance Threshold
Spawn a Job Cell when an opportunity is legitimate and either:
- has meaningful same/next-day payout potential, or
- has expected value of at least $25, or
- can lead to a direct service worth $100+ or recurring revenue.

## Profit Metrics
Track:
- opportunities found/hour
- qualified cells/hour
- submissions/offers/hour
- response rate
- win rate
- dollars collected today
- dollars collected in 72 hours
- dollars collected in 14 days
- effective dollars per owner-hour
- expected pipeline value

## Prime Directive
Optimize for verified dollars collected per unit of owner effort. Agent count is not a success metric.
