from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path

BUCKETS = {"NOW", "LATER", "EXPERIMENT", "DO_NOT_TOUCH_YET"}

@dataclass
class Idea:
    idea: str
    why_it_matters: str
    affects: list[str]
    expected_upside: str
    bucket: str = "LATER"

    def __post_init__(self):
        if self.bucket not in BUCKETS:
            raise ValueError(f"invalid bucket: {self.bucket}")


def save_idea(root: Path, idea: Idea) -> Path:
    path = root / ".gox" / "idea_vault.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(idea), sort_keys=True) + "\n")
    return path
