"""Paper-backed SOP definitions for the GOX Creator Engine.

This module is deliberately deterministic. It defines the contract that an LLM or
other model may later fill, while keeping agent roles, handoffs, approvals, and
acceptance criteria explicit and testable.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class AgentSOP:
    role: str
    objective: str
    inputs: List[str]
    outputs: List[str]
    acceptance: List[str]
    human_gate: bool = False


AGENT_SOPS: Dict[str, AgentSOP] = {
    "creator_ceo": AgentSOP(
        role="Creator CEO / Planner",
        objective="Choose the content goal and coordinate bounded specialist work.",
        inputs=["creator_identity", "audience", "goal", "memory", "constraints"],
        outputs=["brief", "success_metrics", "handoff_plan"],
        acceptance=["one primary goal", "measurable success criteria", "no conflicting handoffs"],
    ),
    "scout": AgentSOP(
        role="Audience & Trend Scout",
        objective="Collect current audience questions, trend signals, and competitor outliers.",
        inputs=["audience", "platform", "topic_space"],
        outputs=["signals", "sources", "outliers"],
        acceptance=["source provenance", "separate trend from evergreen demand", "avoid unsupported claims"],
    ),
    "researcher": AgentSOP(
        role="Evidence Researcher",
        objective="Gather factual and multimodal evidence for the selected idea.",
        inputs=["brief", "signals", "source_assets"],
        outputs=["evidence_pack", "claim_source_map", "video_moments"],
        acceptance=["claims trace to sources", "video evidence is not transcript-only when visuals matter"],
    ),
    "packager": AgentSOP(
        role="Hook & Packaging Strategist",
        objective="Develop distinct title, hook, and thumbnail directions before production.",
        inputs=["brief", "evidence_pack", "creator_identity"],
        outputs=["title_options", "hook_options", "thumbnail_concepts"],
        acceptance=["multiple genuinely distinct options", "promise matches content", "no deceptive packaging"],
    ),
    "writer": AgentSOP(
        role="Story / Script Agent",
        objective="Turn the evidence and packaging promise into a creator-voice narrative.",
        inputs=["brief", "evidence_pack", "selected_hook", "creator_memory"],
        outputs=["script", "shot_notes", "repurpose_markers"],
        acceptance=["creator voice preserved", "key claims sourced", "opening pays off packaging promise"],
    ),
    "reviewer": AgentSOP(
        role="Reviewer / Devil's Advocate",
        objective="Challenge weak assumptions and block risky or low-quality publication.",
        inputs=["script", "evidence_pack", "packaging", "creator_identity"],
        outputs=["review", "required_fixes", "approval_recommendation"],
        acceptance=["factual risk checked", "brand drift checked", "duplication checked", "audience fit checked"],
        human_gate=True,
    ),
    "publisher": AgentSOP(
        role="Publisher",
        objective="Prepare platform-ready metadata and execute only approved publication actions.",
        inputs=["approved_asset", "platform", "schedule", "metadata"],
        outputs=["publish_package", "publication_record"],
        acceptance=["correct destination", "approval present for irreversible publish", "links and metadata validated"],
        human_gate=True,
    ),
    "analyst": AgentSOP(
        role="Analytics Agent",
        objective="Measure content performance against the predeclared success metrics.",
        inputs=["publication_record", "analytics", "success_metrics"],
        outputs=["performance_report", "anomalies", "experiment_result"],
        acceptance=["compare against baseline", "separate observation from inference", "record metric window"],
    ),
    "memory": AgentSOP(
        role="Reflection & Memory Agent",
        objective="Convert outcomes and audience feedback into reusable episodic and reflective memory.",
        inputs=["performance_report", "comments", "previous_memory"],
        outputs=["episode", "reflection", "next_experiment"],
        acceptance=["lesson tied to evidence", "avoid overgeneralizing one result", "retain failed experiments"],
    ),
}


def build_creator_plan(payload: dict) -> dict:
    """Validate a creator request and return a bounded multi-agent workflow plan."""
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")

    creator = str(payload.get("creator", "")).strip()
    goal = str(payload.get("goal", "")).strip()
    platform = str(payload.get("platform", "")).strip().lower()
    topic = str(payload.get("topic", "")).strip()

    if not creator:
        raise ValueError("creator is required")
    if not goal:
        raise ValueError("goal is required")
    if not platform:
        raise ValueError("platform is required")

    workflow = [
        "creator_ceo",
        "scout",
        "researcher",
        "packager",
        "writer",
        "reviewer",
        "publisher",
        "analyst",
        "memory",
    ]

    return {
        "accepted": True,
        "capability": "creator_plan",
        "creator": creator,
        "goal": goal,
        "platform": platform,
        "topic": topic or None,
        "workflow": workflow,
        "human_gates": [name for name in workflow if AGENT_SOPS[name].human_gate],
        "agents": {name: asdict(AGENT_SOPS[name]) for name in workflow},
        "loop": "observe -> plan -> produce -> review -> approve -> publish -> measure -> reflect -> remember",
        "exploration_rule": "Do not allocate all future ideas to prior winners; preserve room for novel hypotheses.",
    }
