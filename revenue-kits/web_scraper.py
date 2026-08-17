#!/usr/bin/env python3
"""Small dependency-free web scraper for bounded public-page extraction jobs.

The generic extractor captures useful page facts immediately and can be extended
with buyer-specific selectors when a project requires them.
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

LOG = logging.getLogger("gox.web_scraper")


def configure_logging(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(path, encoding="utf-8"), logging.StreamHandler()],
    )


def fetch(url: str, timeout: int = 20) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 GOX-Revenue-Kit/1.0"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")


class PageParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.title_parts: list[str] = []
        self.heading_parts: list[str] = []
        self.text_parts: list[str] = []
        self.links: list[str] = []
        self._in_title = False
        self._in_heading = False
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag in {"h1", "h2", "h3"}:
            self._in_heading = True
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                absolute = urljoin(self.base_url, href)
                if absolute.startswith(("http://", "https://")):
                    self.links.append(absolute)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag in {"h1", "h2", "h3"}:
            self._in_heading = False

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = " ".join(data.split())
        if not text:
            return
        self.text_parts.append(text)
        if self._in_title:
            self.title_parts.append(text)
        if self._in_heading:
            self.heading_parts.append(text)


def extract_record(url: str, html: str) -> dict[str, str]:
    parser = PageParser(url)
    parser.feed(html)
    text = " ".join(parser.text_parts)
    unique_links = list(dict.fromkeys(parser.links))
    return {
        "url": url,
        "domain": urlparse(url).netloc,
        "title": " ".join(parser.title_parts)[:500],
        "headings": " | ".join(parser.heading_parts[:20]),
        "link_count": str(len(unique_links)),
        "text_chars": str(len(text)),
        "text_preview": text[:1200],
        "html_bytes": str(len(html.encode("utf-8"))),
        "status": "extracted",
    }


def write_csv(records: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for record in records for key in record})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract useful fields from public web pages")
    parser.add_argument("urls", type=Path, help="TXT file containing one URL per line")
    parser.add_argument("output", type=Path, help="Output .json or .csv file")
    parser.add_argument("--log", type=Path, default=Path("logs/web_scraper.log"))
    args = parser.parse_args()
    configure_logging(args.log)

    records: list[dict[str, str]] = []
    failures = 0
    seen: set[str] = set()
    for line in args.urls.read_text(encoding="utf-8").splitlines():
        url = line.strip()
        if not url or url.startswith("#") or url in seen:
            continue
        seen.add(url)
        try:
            html = fetch(url)
            records.append(extract_record(url, html))
            LOG.info("fetched %s", url)
        except Exception:
            failures += 1
            LOG.exception("failed %s", url)

    if args.output.suffix.lower() == ".json":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        write_csv(records, args.output)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
