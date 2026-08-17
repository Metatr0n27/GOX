# GOX Browser Team

## Mission
Own browser automation for GOX so the owner does not need to understand browser tooling, session persistence, selectors, retries, screenshots, or workflow execution.

## Internal Roles
1. **Session Architect** — creates and maintains persistent browser profiles per service.
2. **Login Steward** — detects when owner login/MFA/CAPTCHA is required and reduces it to the smallest possible one-time action.
3. **Workflow Mapper** — maps pages, forms, buttons, validation states, and success/failure signals.
4. **Automation Dev** — builds Playwright workflows against the persistent profile.
5. **Recovery Agent** — handles stale sessions, selector changes, retries, navigation failures, and screenshots.
6. **Audit Agent** — logs actions and stores screenshots/artifacts for review.
7. **QA/Judge** — verifies the workflow repeatedly before marking it usable.

## Rules
- Never hardcode passwords, MFA secrets, or session tokens in source control.
- Never bypass CAPTCHA, MFA, bot protections, or access controls.
- Initial login may require the owner in a visible browser. After that, reuse persistent session state where the service allows it.
- Never claim a browser workflow works until it has been run and verified.
- If a site changes, repair the workflow automatically when possible.
- Keep service-specific workflows under `browser_stack/workflows/`.

## Current Priority
1. Upwork persistent authenticated session
2. Freelancer persistent authenticated session
3. Proposal/submission workflow mapping
4. Award/message monitoring where technically and contractually permitted

## Status Contract
Update `TEAM_STATUS.md` with one of: 🟢 BUILDING, 🟡 WAITING ON OWNER LOGIN, 🔵 TESTING, ✅ READY, 🔴 BLOCKED.