#!/usr/bin/env python3
"""GOX family profile intake.

Runs in any basic terminal, including Termux on Android or a laptop terminal.
Produces one portable JSON profile per consenting person.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or default


def scale(prompt: str) -> int:
    while True:
        raw = ask(f"{prompt} (1=low, 5=high)")
        if raw in {"1", "2", "3", "4", "5"}:
            return int(raw)
        print("Please enter 1, 2, 3, 4, or 5.")


def yes_no(prompt: str) -> bool:
    while True:
        raw = ask(f"{prompt} (y/n)").lower()
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print("Please enter y or n.")


def choice(prompt: str, options: list[str]) -> str:
    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    while True:
        raw = ask("Choose a number")
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print("Choose one of the listed numbers.")


def slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value or "profile"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a GOX family behavioral profile")
    parser.add_argument("--output-dir", default="family_profiles")
    args = parser.parse_args()

    print("\nGOX FAMILY PROFILE")
    print("This describes how YOU prefer to think, communicate, learn, and receive help.")
    print("Skip private information you do not want stored. Do not enter passwords, account numbers, medical records, or secrets.\n")

    if not yes_no("Do you agree to create this profile"):
        print("No profile created.")
        return 0
    share = yes_no("May this profile be imported into your family's GOX system")
    if not share:
        print("No shared profile created because sharing was not approved.")
        return 0

    name = ask("What name should GOX call you")
    relation = ask("Optional family/relationship label")

    behavior = {
        "decision_speed": scale("How quickly do you prefer to make decisions"),
        "risk_tolerance": scale("How comfortable are you taking calculated risks"),
        "structure_need": scale("How much structure/checklists do you prefer"),
        "directness": scale("How direct should communication be"),
        "social_energy": scale("How much interaction/collaboration do you prefer"),
        "change_tolerance": scale("How comfortable are you changing plans quickly"),
        "conflict_style": choice("When disagreement happens, what is most like you?", ["avoid", "calm-discuss", "direct", "mediate", "compete", "mixed"]),
        "stress_response": ask("When stressed, what do you usually do or need from other people"),
        "trust_style": ask("What makes you trust a person, system, or recommendation"),
        "learning_style": ask("How do you learn best (examples, video, reading, hands-on, explanation, other)"),
        "communication_preferences": ask("How should GOX communicate with you"),
        "motivators": ask("What tends to motivate you"),
        "friction_points": ask("What behavior from a helper/system frustrates you most"),
    }

    goals = {
        "top_priority": ask("What is the biggest thing you want help accomplishing"),
        "what_help_should_do": ask("What should GOX actively do for you instead of only explaining"),
        "what_help_should_not_do": ask("What should GOX avoid doing"),
        "skills_to_build": ask("What would you like to learn or become better at"),
        "projects_or_income_goals": ask("Any projects, work, or income goals you want the system to support"),
    }

    examples = {
        "when_things_go_well": ask("Describe how you act when things are going well"),
        "when_frustrated": ask("Describe how you act when frustrated or blocked"),
        "how_they_make_decisions": ask("Give an example of how you make an important decision"),
        "how_they_ask_for_help": ask("How do you normally ask for help"),
        "what_makes_them_feel_respected": ask("What makes you feel listened to and respected"),
        "real_example": ask("Optional: describe one real situation that shows what you are like"),
    }

    profile = {
        "schema_version": "1.0",
        "profile_id": slug(name),
        "display_name": name,
        "relationship_label": relation,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "consent": {"agreed": True, "share_with_family_system": True, "notes": "Self-entered profile"},
        "behavior": behavior,
        "goals": goals,
        "examples": examples,
        "private_notes": "",
    }

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{profile['profile_id']}.json"
    path.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nSaved: {path}")
    print("Send only this JSON file to the family GOX operator for import.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
