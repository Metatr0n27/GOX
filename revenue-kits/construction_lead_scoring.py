from __future__ import annotations

import csv
import math
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

PHONE_RE = re.compile(r"\D+")


def normalize_phone(value: str | None) -> str:
    digits = PHONE_RE.sub("", value or "")
    if not digits:
        return ""
    if len(digits) == 10:
        return f"+1{digits}"
    if digits.startswith("1") and len(digits) == 11:
        return f"+{digits}"
    return f"+{digits}"


def parse_amount(value: str | None) -> float:
    cleaned = re.sub(r"[^0-9.\-]", "", value or "")
    try:
        return max(0.0, float(cleaned)) if cleaned else 0.0
    except ValueError:
        return 0.0


def parse_date(value: str | None) -> date | None:
    text = (value or "").strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def classify_lead(
    owner_phone: str,
    contractor_phone: str,
    contractor_name: str,
    subcontractor_keywords: Iterable[str],
    unfit_owner_types: Iterable[str] = (),
    owner_type: str = "",
) -> str:
    owner_type_l = owner_type.lower()
    if any(term.lower() in owner_type_l for term in unfit_owner_types):
        return "Unfit"
    contractor_l = contractor_name.lower()
    if any(term.lower() in contractor_l for term in subcontractor_keywords):
        return "Acquire Number"
    if normalize_phone(owner_phone) or normalize_phone(contractor_phone):
        return "Calling Queue"
    return "Visit In-Person"


@dataclass(frozen=True)
class ScoreWeights:
    timing: float = 0.25
    regional_conversion: float = 0.20
    project_value: float = 0.20
    project_type: float = 0.20
    completeness: float = 0.15

    def normalized(self) -> "ScoreWeights":
        total = self.timing + self.regional_conversion + self.project_value + self.project_type + self.completeness
        if total <= 0:
            raise ValueError("Score weights must sum to a positive value")
        return ScoreWeights(
            self.timing / total,
            self.regional_conversion / total,
            self.project_value / total,
            self.project_type / total,
            self.completeness / total,
        )


def score_lead(
    *,
    issue_date: date | None,
    today: date,
    ideal_months: float,
    regional_conversion: float,
    project_amount: float,
    project_type_conversion: float,
    has_phone: bool,
    has_email: bool,
    weights: ScoreWeights = ScoreWeights(),
) -> int:
    w = weights.normalized()
    if issue_date is None:
        timing = 0.0
    else:
        age_months = max(0.0, (today - issue_date).days / 30.4375)
        distance = abs(age_months - max(0.0, ideal_months))
        timing = max(0.0, 1.0 - distance / max(1.0, ideal_months + 3.0))

    region = min(1.0, max(0.0, regional_conversion))
    project_type = min(1.0, max(0.0, project_type_conversion))
    value_score = 0.0 if project_amount <= 0 else min(1.0, math.log1p(project_amount) / math.log1p(5_000_000))
    completeness = (0.6 if has_phone else 0.0) + (0.4 if has_email else 0.0)

    raw = 100.0 * (
        timing * w.timing
        + region * w.regional_conversion
        + value_score * w.project_value
        + project_type * w.project_type
        + completeness * w.completeness
    )
    return max(0, min(100, round(raw)))


def iter_csv(path: Path) -> Iterable[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        yield from csv.DictReader(handle)
