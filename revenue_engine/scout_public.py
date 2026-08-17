#!/usr/bin/env python3
"""Read-only public demand scout.

Initial source: Reddit public Atom feeds. No login, no posting, no messaging.
Filters for explicit hiring/buyer-demand language before producing opportunities.
"""
from __future__ import annotations
import hashlib
import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict
from typing import Iterable

from demand_to_cash import Opportunity

USER_AGENT = "GOX-DemandScout/0.1 (read-only public feed; contact via repository owner)"
ATOM = {"a": "http://www.w3.org/2005/Atom"}

HIRING_MARKERS = (
    "[hiring]", "hiring ", "looking for someone", "need someone", "need help with",
    "looking for an automation", "looking for a developer", "seeking ", "contractor needed",
)
REJECT_MARKERS = ("[for hire]", "for hire", "available for work", "hire me", "my services")

MONEY_RE = re.compile(r"\$\s?(\d{2,6})(?:\s*[-–—to]+\s*\$?\s?(\d{2,6}))?", re.I)
HOURLY_RE = re.compile(r"\$\s?(\d{2,4})(?:\s*[-–—to]+\s*\$?\s?(\d{2,4}))?\s*(?:/|per\s*)?(?:hr|hour)", re.I)
TAG_RE = re.compile(r"<[^>]+>")


def _clean(value: str | None) -> str:
    value = html.unescape(value or "")
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", value)).strip()


def explicit_demand(title: str, body: str) -> bool:
    text = f"{title} {body}".lower()
    if any(x in text for x in REJECT_MARKERS):
        return False
    return any(x in text for x in HIRING_MARKERS)


def extract_budget(text: str) -> tuple[float, float]:
    hourly = HOURLY_RE.search(text)
    if hourly:
        low = float(hourly.group(1)); high = float(hourly.group(2) or low)
        # Normalize a rough 4-hour paid task so hourly posts can be ranked without
        # pretending they are guaranteed full-time earnings.
        return low * 4.0, high * 4.0
    fixed = MONEY_RE.search(text)
    if fixed:
        low = float(fixed.group(1)); high = float(fixed.group(2) or low)
        return low, high
    return 0.0, 0.0


def parse_atom(xml_bytes: bytes, source: str) -> list[Opportunity]:
    root = ET.fromstring(xml_bytes)
    out: list[Opportunity] = []
    for entry in root.findall("a:entry", ATOM):
        title = _clean(entry.findtext("a:title", default="", namespaces=ATOM))
        content = _clean(entry.findtext("a:content", default="", namespaces=ATOM))
        link_el = entry.find("a:link", ATOM)
        url = link_el.attrib.get("href", "") if link_el is not None else ""
        external_id = _clean(entry.findtext("a:id", default=url, namespaces=ATOM)) or url
        if not explicit_demand(title, content):
            continue
        low, high = extract_budget(f"{title} {content}")
        out.append(Opportunity(
            source=source,
            external_id=external_id or hashlib.sha256((title + url).encode()).hexdigest()[:16],
            title=title,
            description=content[:4000],
            budget_min=low,
            budget_max=high,
            source_url=url,
            explicit_demand=True,
        ))
    return out


def fetch_atom(url: str, source: str, timeout: int = 10) -> list[Opportunity]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/atom+xml,application/xml;q=0.9,*/*;q=0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status != 200:
            raise RuntimeError(f"{source} returned HTTP {resp.status}")
        raw = resp.read(2_000_000)
    return parse_atom(raw, source)


def default_sources() -> list[tuple[str, str]]:
    return [
        ("reddit-forhire-new", "https://www.reddit.com/r/forhire/new/.rss"),
        ("reddit-freelance-forhire-new", "https://www.reddit.com/r/freelance_forhire/new/.rss"),
    ]


def scout(sources: Iterable[tuple[str, str]] | None = None) -> list[Opportunity]:
    seen = set(); out = []
    for source, url in (sources or default_sources()):
        try:
            items = fetch_atom(url, source)
        except Exception:
            continue
        for item in items:
            key = (item.source, item.external_id)
            if key in seen:
                continue
            seen.add(key); out.append(item)
    return out


if __name__ == "__main__":
    import json
    print(json.dumps([asdict(x) for x in scout()], indent=2))
