from __future__ import annotations

MODES = {
    "simple": "Explain in plain language with no jargon. Say what was made, why it matters, current status, and next action. Keep it short enough to show someone quickly.",
    "teacher": "Explain like a teacher to a student. Define terms, show the sequence, why each part exists, what was tested, what remains, and how the parts connect.",
    "business": "Explain for a business audience. Focus on value, revenue impact, time saved, owner effort, risks, verification status, and next commercial action.",
    "investor": "Explain for an investor. Focus on product thesis, differentiation, execution progress, evidence, scalability, revenue model, defensibility, risks, and milestones. Never exaggerate traction.",
    "technical": "Explain for a technical audience. Include architecture, files, tools, integrations, state, tests, evidence, blockers, deployment status, and exact next technical action.",
}


def make_instruction(mode: str, subject: str, time_window: str | None = None) -> str:
    key = mode.strip().lower()
    if key not in MODES:
        raise ValueError(f"unknown explain mode: {mode}")
    window = f" Time window: {time_window}." if time_window else ""
    return f"Subject: {subject}.{window} {MODES[key]} Use only verified facts; distinguish built, verified, blocked, forecast, and paid states."
