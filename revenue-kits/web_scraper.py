#!/usr/bin/env python3
"""Reusable web scraping scaffold for fast client delivery."""
from __future__ import annotations

import argparse
import csv
import json
import logging
from pathlib import Path
from urllib.parse import urlparse
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


def extract_record(url: str, html: str) -> dict[str, str]:
    """Buyer-specific selectors/parsing rules should be implemented here after award."""
    return {
        "url": url,
        "domain": urlparse(url).netloc,
        "status": "adapter_required",
        "html_bytes": str(len(html.encode("utf-8"))),
    }


def write_csv(records: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for record in records for key in record})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", type=Path, help="TXT file containing one URL per line")
    parser.add_argument("output", type=Path)
    parser.add_argument("--log", type=Path, default=Path("logs/web_scraper.log"))
    args = parser.parse_args()
    configure_logging(args.log)

    records: list[dict[str, str]] = []
    failures = 0
    for line in args.urls.read_text(encoding="utf-8").splitlines():
        url = line.strip()
        if not url or url.startswith("#"):
            continue
        try:
            html = fetch(url)
            records.append(extract_record(url, html))
            LOG.info("fetched %s", url)
        except Exception:
            failures += 1
            LOG.exception("failed %s", url)

    if args.output.suffix.lower() == ".json":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(records, indent=2), encoding="utf-8")
    else:
        write_csv(records, args.output)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
