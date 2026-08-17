# GOX Upwork Revenue Team

Purpose: turn live Upwork demand into qualified, tailored, trackable applications with minimal owner involvement.

## Agent team

1. **Job Scout** — ingests live job listings and normalizes title, budget, skills, recency, client signals, and URL.
2. **Fit Scorer** — scores technical fit, proof fit, budget quality, urgency, competition risk, and probability of a credible proposal.
3. **Proof Matcher** — maps the job to concrete GOX repository evidence and never invents client history.
4. **Proposal Writer** — creates a short job-specific proposal with scope, acceptance criteria, price/bid recommendation, and one useful implementation insight.
5. **Bid Strategist** — chooses fixed-price vs hourly positioning and suggests a defensible bid from the posted range.
6. **Screening Answer Agent** — prepares concise answers to Upwork screening questions using verified GOX capabilities only.
7. **Application QA** — rejects generic, exaggerated, mismatched, or unsupported applications before submission.
8. **Submission Adapter** — sends through an approved Upwork API/integration when credentials and permitted endpoints are available. It must not use unapproved browser-bot interaction.
9. **Follow-up Agent** — tracks replies/interviews and prepares next actions.
10. **Revenue Supervisor** — ranks the queue by expected value and keeps the team focused on jobs most likely to convert quickly.

## Operating loop

Scout -> Score -> Match Proof -> Price -> Draft -> QA -> Submit/Queue -> Track -> Follow up -> Learn

## Current submission boundary

GOX can automate discovery, scoring, proposal generation, portfolio matching, QA, and tracking now. Direct Upwork submission is enabled only through an approved Upwork API/integration. Until that exists, the system produces a ready-to-submit application packet and marks it `submission_blocked: approved_upwork_interface_required` rather than pretending it was submitted.

## Revenue-first rules

- Prefer recently posted jobs with explicit budgets and a narrow deliverable.
- Prefer Python, n8n, APIs/webhooks, browser workflows, data extraction, AI agents, workflow automation, and creator/video automation.
- Do not claim client outcomes that GOX cannot prove.
- Avoid unpaid custom builds beyond a tiny diagnostic/sample when the expected conversion value is low.
- Every application must include one concrete implementation idea specific to the buyer's problem.
- Track application count, replies, interviews, offers, contracted value, and cash collected.
