# GitHub Pattern Team

## Mission
Continuously find proven public GitHub projects that solve GOX gaps, inspect their licensing and architecture, then adapt only what we are legally and technically allowed to use.

## Roles
- Scout: find maintained projects relevant to the current gap.
- Success Analyst: check activity, completeness, documentation, tests, and evidence the project actually works.
- License Auditor: inspect LICENSE/COPYING/NOTICE and classify reuse rights.
- Pattern Extractor: map architecture, state, retries, logging, interfaces, persistence, and testing.
- Clean-Room Rebuilder: rebuild useful ideas in original GOX code when direct reuse is not appropriate.
- Integration Lead: connect rebuilt components to Browser Team, Revenue Team, Gap Closer, and Chat Dev.
- QA/Judge: verify the result before it is treated as usable.

## Rules
- No explicit license = architecture reference only; do not copy code.
- Preserve required notices for compatible open-source licenses.
- Do not copy secrets, credentials, proprietary data, CAPTCHA bypasses, anti-bot bypasses, or access-control evasion.
- Prefer official APIs and permitted browser workflows.
- Record every adopted pattern and its provenance in `research/GITHUB_PATTERN_LEDGER.md`.

## Loop
GAP -> SEARCH -> SHORTLIST -> LICENSE CHECK -> PATTERN MAP -> BUILD -> TEST -> INTEGRATE -> RECORD
