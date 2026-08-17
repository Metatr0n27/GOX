# GOX Agentic Agent Team

## Mission
Turn GOX from a collection of role descriptions into a stateful execution system where agents can plan, act with tools, verify results, repair failures, and hand work to other agents without losing evidence or context.

## Core Roles
1. **Supervisor** — receives goal, decomposes work, routes tasks, enforces priority and stop conditions.
2. **Research Scout** — searches GitHub/docs/current sources for proven implementation patterns and dependencies.
3. **Access Engineer** — establishes legitimate connector/API/browser/session access paths.
4. **Builder** — implements code/config/workflows in the correct active repo.
5. **Browser Operator** — performs authenticated browser workflows after session bootstrap.
6. **Revenue Operator** — qualifies explicit buyer demand, prepares and executes outreach/submission where tools permit.
7. **Tester** — runs deterministic tests, smoke tests, browser checks, and integration checks.
8. **Critic/Judge** — rejects unverified claims, weak implementations, unsafe assumptions, and incomplete acceptance evidence.
9. **Repair Agent** — diagnoses failed tests/CI/tool calls and iterates until passing or truly blocked.
10. **Evidence Keeper** — stores artifacts, logs, screenshots, commit SHAs, external confirmations, and provenance.

## Execution Graph
GOAL -> SUPERVISOR -> DISCOVER -> ACCESS -> BUILD -> TEST -> JUDGE
                                           ^              |
                                           |---- REPAIR <--|

For buyer/revenue work:
DEMAND -> QUALIFY -> ACCESS -> SUBMIT/CONTACT -> VERIFY EXTERNAL RESULT -> FULFILL -> TEST -> DELIVER -> VERIFY PAYMENT

## Agent Contract
Every agent receives:
- goal
- current state
- allowed tools
- evidence available
- acceptance criteria
- retry budget
- owner-only gates

Every agent returns:
- action actually taken
- evidence
- changed files/external state
- test result
- next routing decision
- blocker only if genuinely unavoidable

## Authenticity Rules
- No agent may mark success based only on its own text output.
- External actions require external confirmation evidence.
- Code work requires tests or an explicit untested state.
- Browser authentication requires verified authenticated page/session state.
- Revenue requires award/funding/payment evidence according to the stated metric.

## Open-Source Architecture Sources
GOX will study and adapt compatible patterns from:
- crewAI: role/task/crew decomposition and hierarchical process patterns (MIT)
- LangGraph: state graphs, checkpoints, conditional routing, durable agent workflows (MIT)
- Microsoft AutoGen: conversable agent/tool coordination patterns (MIT code license)
- browser-use: agent-browser abstraction and browser action patterns (MIT)

Required license notices must be preserved for any direct code reuse. Prefer clean-room implementation of architecture concepts unless direct reuse materially saves time.

## First Build Targets
1. Durable task state/checkpoints.
2. Supervisor conditional routing.
3. Tool execution result schema.
4. Judge/evidence gate.
5. Repair loop with bounded retries.
6. Browser-operator adapter.
7. Revenue-operator adapter.
8. Status projection into TEAM_STATUS.md.

## Done Definition
This team is not 'real' merely because this file exists. It becomes VERIFIED only when a test goal is automatically decomposed, at least two specialist agents execute real tool/code actions, a failure triggers repair/reroute, and evidence is stored showing the final verified result.