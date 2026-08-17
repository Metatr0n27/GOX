# GOX Creator Engine — Research Stack

This stack turns published agent research into concrete GOX design rules. The goal is not to copy papers verbatim; it is to use demonstrated architectural patterns and keep each creator workflow inspectable, testable, and human-controllable.

## Core multi-agent architecture

1. **ChatDev: Communicative Agents for Software Development** — Qian et al., 2023 — arXiv:2307.07924
   - Pattern: specialized roles coordinated through explicit communication chains.
   - GOX use: creator pipeline handoffs (Scout → Strategist → Researcher → Writer → Reviewer → Publisher → Analyst).

2. **MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework** — Hong et al., 2023 — arXiv:2308.00352
   - Pattern: encode Standard Operating Procedures instead of relying on free-form agent chat.
   - GOX use: every creator agent receives defined inputs, outputs, acceptance criteria, and downstream recipient.

3. **AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation** — Wu et al., 2023 — arXiv:2308.08155
   - Pattern: customizable agents combining LLMs, humans, and tools.
   - GOX use: preserve human approval gates for identity, factual claims, irreversible publishing, and monetization actions.

4. **CAMEL: Communicative Agents for Mind Exploration of Large Language Model Society** — Li et al., 2023 — arXiv:2303.17760
   - Pattern: role-playing and inception prompts maintain task/role consistency.
   - GOX use: creator-specific identity contracts and stable role charters.

## Memory, reflection, and learning

5. **Generative Agents: Interactive Simulacra of Human Behavior** — Park et al., 2023 — arXiv:2304.03442
   - Pattern: observation → memory → reflection → planning.
   - GOX use: retain creator history, audience signals, previous experiments, successful phrases, failed formats, and lessons.

6. **Reflexion: Language Agents with Verbal Reinforcement Learning** — Shinn et al., 2023 — arXiv:2303.11366
   - Pattern: convert task feedback into textual reflection stored in episodic memory.
   - GOX use: after every published asset, generate a structured postmortem from analytics and comments; use it in the next plan.

7. **Perceive, Reflect, and Plan** — Zeng et al., 2024 — arXiv:2408.04168
   - Pattern: perception and memory-backed reflection precede long-range planning.
   - GOX use: do not let the next-content planner react to one metric in isolation; retrieve relevant prior evidence first.

## Planning and reliability

8. **DEVIL'S ADVOCATE: Anticipatory Reflection for LLM Agents** — 2024 — arXiv:2405.16334
   - Pattern: challenge plans before execution, evaluate after action, backtrack when necessary.
   - GOX use: Reviewer agent runs a pre-publish adversarial check for factual risk, weak hook, audience mismatch, duplication, and brand drift.

9. **Two-level planning for autonomous agents** — CoLLAs 2024, arXiv:2405.02749
   - Pattern: separate high-level subgoal planning from low-level action execution.
   - GOX use: Creator CEO chooses campaign/content goals; specialist agents execute bounded tasks.

## Video and multimodal evidence

10. **Understanding Long Videos with Multimodal Language Models** — Ranasinghe et al., 2024 — arXiv:2403.16998
    - Pattern: inject video-specific visual/object information rather than depending on language-model priors alone.
    - GOX use: video analysis should combine transcript, sampled frames/scenes, OCR/onscreen text when needed, and engagement timestamps.

11. **Temporal Sentence Grounding in Videos: A Survey and Future Directions** — Zhang et al., 2022/2024 journal version — arXiv:2201.08071
    - Pattern: map language queries to exact moments in untrimmed video.
    - GOX use: repurposing agent should locate evidence-backed clip boundaries instead of clipping solely from transcript paragraphs.

## Recommendation/growth safeguards

12. **Popularity-Aware Alignment and Contrast for Mitigating Popularity Bias** — Cai et al., KDD 2024 — arXiv:2405.20718
    - Pattern: recommender feedback can reinforce popularity and reduce diversity.
    - GOX use: Idea Scorer must reserve exploration budget for novel topics/formats and not only imitate previous winners.

## GOX design rules derived from the stack

- Use **SOP handoffs**, not an unstructured group chat.
- Separate **strategy/planning** from **execution**.
- Every agent has an explicit role, permitted tools, input schema, output schema, and acceptance criteria.
- Maintain **episodic memory** (what happened) and **reflection memory** (what was learned).
- Use **human approval** for identity changes, material factual/legal risk, irreversible publishing, spending, and external commitments.
- Require a **pre-publish reviewer** and a **post-publish postmortem**.
- Ground video work in **multimodal evidence**, not transcript-only inference.
- Keep an **exploration budget** so optimization does not collapse into copying old winners.
- Record provenance for research facts, source assets, generated claims, and analytics.
- Treat creator growth as a closed loop: Observe → Plan → Produce → Review → Publish → Measure → Reflect → Remember → Plan again.

## Initial agent roster

- Creator CEO / Planner
- Audience & Trend Scout
- Outlier / Competitor Researcher
- Evidence Researcher
- Idea Scorer
- Hook & Packaging Strategist
- Story / Script Agent
- Video / Clip Producer
- Reviewer / Devil's Advocate
- Publisher (human-gated for irreversible actions)
- Community Signal Agent
- Analytics Agent
- Reflection & Memory Agent
- Monetization Strategist

## Missing capabilities this branch is intended to close

The existing Chat Dev release already has a job queue, persistent SQLite state, authentication boundary, worker leases/retries, and an allowlisted capability registry. The creator gap is that the registry does not yet expose creator-specific planning or structured creator-agent SOPs. This branch adds the first bounded `creator_plan` capability plus the paper-backed workflow specification and tests.
