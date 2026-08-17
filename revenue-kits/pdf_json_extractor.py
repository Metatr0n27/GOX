#!/usr/bin/env python3
"""Reusable PDF-to-JSON extraction scaffold for fast client delivery.

Buyer-specific parsing rules and schemas are injected after award.
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

LOG = logging.getLogger("gox.pdf_json")


def configure_logging(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8"), logging.StreamHandler()],
    )


def extract_pdf(pdf_path: Path, schema: dict[str, Any] | None = None) -> dict[str, Any]:
    """Adapter boundary for buyer-specific PDF parsing."""
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    return {
        "source_file": pdf_path.name,
        "status": "adapter_required",
        "schema": schema or {},
        "data": {},
    }


def validate_result(result: dict[str, Any]) -> None:
    required = {"source_file", "status", "data"}
    missing = required - result.keys()
    if missing:
        raise ValueError(f"Missing required output keys: {sorted(missing)}")


def process_directory(input_dir: Path, output_dir: Path, schema_path: Path | None) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    schema = json.loads(schema_path.read_text(encoding="utf-8")) if schema_path else None
    failures = 0
    for pdf_path in sorted(input_dir.glob("*.pdf")):
        try:
            result = extract_pdf(pdf_path, schema)
            validate_result(result)
            out = output_dir / f"{pdf_path.stem}.json"
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            LOG.info("processed %s -> %s", pdf_path, out)
        except Exception:
            failures += 1
            LOG.exception("failed processing %s", pdf_path)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--log", type=Path, default=Path("logs/pdf_json_extractor.log"))
    args = parser.parse_args()
    configure_logging(args.log)
    return 1 if process_directory(args.input_dir, args.output_dir, args.schema) else 0


if __name__ == "__main__":
    raise SystemExit(main())
