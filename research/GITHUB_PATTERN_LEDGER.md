# GOX GitHub Pattern Ledger

This file records external open-source projects studied for GOX, what was learned, the license status, and whether any code was directly reused.

| Source | Purpose | License Status | GOX Use | Direct Code Reuse? | Notes |
|---|---|---|---|---|---|
| `mfahadrehan/upwork-discord-bot` | Upwork job ingestion, deduplication, persistence, notifications, token/session maintenance | No explicit license verified during initial review | Architecture reference only | No | Useful pattern: ingest -> normalize -> dedupe -> persist -> notify. Cloudflare/access-control bypass techniques are excluded from GOX. |
| `crewAIInc/crewAI` | Multi-agent role/task decomposition, hierarchical crews, tool-driven workflows | MIT verified | Architecture + compatible reusable patterns | Not yet | Strong source for supervisor/worker role structure and task handoffs. Preserve MIT notice for any direct reuse. |
| `langchain-ai/langgraph` | Stateful agent graphs, checkpoints, conditional routing, durable execution | MIT verified | Architecture + compatible reusable patterns | Not yet | Strong source for persistent state, branching, retries, and resumable workflows. Preserve MIT notice for any direct reuse. |
| `microsoft/autogen` | Multi-agent conversations, tool coordination, agent handoffs | MIT code license verified | Architecture + compatible reusable patterns | Not yet | Useful for agent contracts, tool calling, and multi-agent coordination. Preserve code license notice for any direct reuse. |
| `browser-use/browser-use` | Agent-controlled browser abstraction and action loops | MIT verified | Architecture + compatible reusable patterns | Not yet | Useful for browser operator design after legitimate authentication bootstrap. No CAPTCHA/access-control bypass use. |

## Required Review Before Adoption
For every future source:
1. Verify repository activity and completeness.
2. Inspect LICENSE/COPYING/NOTICE.
3. Classify direct reuse rights.
4. Extract architecture and test strategy.
5. Rebuild cleanly when license is absent/incompatible.
6. Add verification evidence before marking integrated.
