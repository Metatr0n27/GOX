#!/usr/bin/env python3
"""Deterministic core for the GOX Upwork Revenue Team."""
from dataclasses import dataclass, asdict
from typing import List, Dict

GOX_SKILLS = {
    "python", "n8n", "api", "apis", "webhook", "webhooks", "automation",
    "openai", "ai", "agents", "agent", "browser", "scraping", "csv",
    "excel", "workflow", "workflows", "youtube", "video", "make.com", "make"
}

@dataclass
class Job:
    title: str
    description: str
    budget: str = ""
    source_url: str = ""
    posted_recently: bool = True

@dataclass
class ApplicationPacket:
    job_title: str
    score: int
    bid_strategy: str
    proof: List[str]
    proposal: str
    submission_status: str


def _tokens(text: str):
    return {t.strip(".,:;()[]{}!?/\\").lower() for t in text.split()}


def score_job(job: Job) -> int:
    text = f"{job.title} {job.description}".lower()
    tokens = _tokens(text)
    skill_hits = len(GOX_SKILLS & tokens)
    score = min(55, skill_hits * 7)
    if job.posted_recently:
        score += 10
    if any(x in text for x in ("n8n", "python", "openai", "api", "workflow")):
        score += 15
    if any(x in text for x in ("youtube", "creator", "video")):
        score += 8
    if job.budget:
        score += 7
    if any(x in text for x in ("senior", "expert only", "10+ years")):
        score -= 12
    return max(0, min(100, score))


def proof_match(job: Job) -> List[str]:
    text = f"{job.title} {job.description}".lower()
    proof = ["GOX public build repository: https://github.com/Metatr0n27/GOX"]
    if "agent" in text or "ai" in text:
        proof.append("GOX agent orchestration and allowlisted worker architecture")
    if "workflow" in text or "n8n" in text or "automation" in text:
        proof.append("GOX persistent automation job queue, retries, status tracking, and adapters")
    if "youtube" in text or "video" in text or "creator" in text:
        proof.append("GOX Creator Engine research/SOP branch for creator and video automation")
    if "python" in text:
        proof.append("Python automation modules and tests in GOX")
    return proof


def bid_strategy(job: Job) -> str:
    text = job.budget.lower()
    if "$150" in text:
        return "Bid the posted $150 fixed price; constrain delivery to a tested MVP with explicit acceptance criteria."
    if "/hour" in text or "hour" in text:
        return "Bid near the lower-middle of the posted range for the first bounded milestone, then raise after proof."
    return "Propose a small paid milestone first, priced to the narrowest useful deliverable."


def proposal(job: Job) -> str:
    text = f"{job.title} {job.description}".lower()
    implementation = "I would start by mapping the workflow into explicit inputs, failure states, retries, logs, and acceptance tests before wiring the automation."
    if "youtube" in text or "video" in text:
        implementation = "I would split the pipeline into research/script, asset generation, render/QA, and publish-ready stages so failures can be retried without rerunning the entire video workflow."
    elif "property" in text or "maintenance" in text:
        implementation = "I would normalize AppFolio/email requests into one intake schema, classify urgency/category, then route work orders with retries, audit logs, and human escalation for ambiguous cases."
    elif "marketing" in text or "subscriber" in text:
        implementation = "I would centralize lead/subscriber events, deduplicate them, score intent, and keep AI generation behind deterministic routing and logging so the workflow stays auditable."
    return (
        f"Hi — I can take this on as a bounded paid build.\n\n"
        f"{implementation}\n\n"
        "My strongest fit is Python automation, APIs/webhooks, n8n-style workflows, agent orchestration, browser automation, logging/retries, and testable handoff. "
        "I won't invent client history; I'd rather prove fit on the actual task.\n\n"
        "If you send the current workflow, credentials/integration constraints, and the acceptance criteria, I can return a concrete implementation plan and fixed first milestone.\n\n"
        "Portfolio: https://github.com/Metatr0n27/GOX\n\nNaomi — GOX Automation"
    )


def build_packet(job: Job) -> ApplicationPacket:
    return ApplicationPacket(
        job_title=job.title,
        score=score_job(job),
        bid_strategy=bid_strategy(job),
        proof=proof_match(job),
        proposal=proposal(job),
        submission_status="submission_blocked: approved_upwork_interface_required",
    )


def rank_jobs(jobs: List[Job]) -> List[Dict]:
    packets = [build_packet(job) for job in jobs]
    packets.sort(key=lambda p: p.score, reverse=True)
    return [asdict(p) for p in packets]
