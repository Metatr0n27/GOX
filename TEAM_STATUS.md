# GOX Team Status

_Last updated: 2026-08-17_

## Revenue Sprint Goal
**Target:** $5,000 contractually secured in one day.

## Visible Team

| Agent | State | Current Job | Next Trigger |
|---|---|---|---|
| Opportunity Hunter | 🟢 BUILDING | Find fresh $1k-$5k buyer requests matching verified GOX capabilities | Strong actionable lead found |
| Qualifier | 🟢 BUILDING | Reject scams, bad-fit, low-probability, or unverified-stack jobs | New lead enters pipeline |
| Pricing Lead | 🟢 BUILDING | Optimize bid and milestone structure for secured revenue | Qualified lead |
| Proposal Lead | 🟢 BUILDING | Prepare truthful ready-to-submit proposals | Qualified lead |
| Technical Lead | 🟢 BUILDING | Define smallest reliable implementation and dependencies | Qualified lead |
| QA Lead | 🟢 BUILDING | Define acceptance tests before delivery | Technical plan ready |
| Gap Closer | 🟢 BUILDING | Detect and remove missing tools, integrations, scripts, repo mistakes, and setup gaps | Any blocker appears |
| Chat Dev | 🟢 BUILDING | Prebuild reusable delivery kits and implement revenue work immediately | Buyer-specific inputs or reusable kit need |
| GitHub Pattern Team | 🟢 BUILDING | Find proven open-source patterns, audit licenses, rebuild useful architecture cleanly | New capability gap |
| Browser Team | 🟡 WAITING ON OWNER LOGIN | Persistent Playwright profiles for Upwork/Freelancer and service workflow automation | First authenticated session created |
| Closer | 🟡 WAITING ON INPUT | Reduce unavoidable marketplace/account actions to one smallest step | Award/submission/account action required |

## Active Revenue Stack
- `agents/chat-dev.md` — visible development agent.
- `agents/revenue-team.md` — opportunity, pricing, proposal, technical, QA, and closing workflow.
- `agents/gap-closer.md` — proactive dependency/blocker resolution.
- `agents/github-pattern-team.md` — proven GitHub pattern discovery and clean-room adaptation.
- `agents/browser-team.md` — authenticated browser/session/workflow team.
- `browser_stack/auth_browser.py` — persistent Playwright browser launcher.
- `browser_stack/README.md` — one-time authentication and session-reuse instructions.
- `revenue/PIPELINE.md` — inspectable $5,000/day pipeline board.
- `revenue/PREFLIGHT_TEMPLATE.md` — mandatory bid preflight before promising delivery.

## Current Blocker
The browser stack now exists in GOX. The remaining blocker is the first real account login/MFA/CAPTCHA in a visible browser, which must be performed by the authorized account owner. After that, GOX can reuse the persistent local browser profile where the site permits session persistence.

## Current Reality
- Revenue work belongs in the active GOX umbrella repository unless a product-specific active repository is explicitly selected.
- `project-gox-workforce` was superseded and must not be used for new active revenue work.
- Revenue and blocker handling must be visible here rather than existing only as chat promises.

## Owner Escalation Rule
Only escalate when an authenticated account-owner action, identity check, financial/legal authorization, unavailable external capability, or buyer-specific secret/input is genuinely required.
