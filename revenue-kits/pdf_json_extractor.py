#!/usr/bin/env python3
"""Reusable PDF-to-JSON extractor for bounded client delivery.

Uses PyPDF2 when available. The output is useful immediately for searchable/text
PDFs and keeps a clean adapter boundary for buyer-specific schemas.
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


def _load_pdf_reader(pdf_path: Path):
    try:
        from PyPDF2 import PdfReader
    except ImportError as exc:
        raise RuntimeError("PyPDF2 is required: pip install PyPDF2") from exc
    return PdfReader(str(pdf_path))


def extract_pdf(pdf_path: Path, schema: dict[str, Any] | None = None) -> dict[str, Any]:
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    reader = _load_pdf_reader(pdf_path)
    pages: list[dict[str, Any]] = []
    full_text_parts: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        full_text_parts.append(text)
        pages.append({"page": index, "text": text, "chars": len(text)})

    full_text = "\n\n".join(full_text_parts)
    metadata = {str(k): str(v) for k, v in (reader.metadata or {}).items()}
    result: dict[str, Any] = {
        "source_file": pdf_path.name,
        "status": "extracted",
        "page_count": len(reader.pages),
        "text_chars": len(full_text),
        "metadata": metadata,
        "schema": schema or {},
        "data": {
            "text": full_text,
            "pages": pages,
        },
    }
    return result


def validate_result(result: dict[str, Any]) -> None:
    required = {"source_file", "status", "page_count", "data"}
    missing = required - result.keys()
    if missing:
        raise ValueError(f"Missing required output keys: {sorted(missing)}")
    if result["status"] != "extracted":
        raise ValueError("PDF extraction did not complete")


def process_directory(input_dir: Path, output_dir: Path, schema_path: Path | None) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    schema = json.loads(schema_path.read_text(encoding="utf-8")) if schema_path else None
    failures = 0
    pdfs = sorted(input_dir.glob("*.pdf"))
    if not pdfs:
        LOG.warning("no PDF files found in %s", input_dir)
    for pdf_path in pdfs:
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
    parser = argparse.ArgumentParser(description="Extract searchable PDF text into JSON")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--log", type=Path, default=Path("logs/pdf_json_extractor.log"))
    args = parser.parse_args()
    configure_logging(args.log)
    return 1 if process_directory(args.input_dir, args.output_dir, args.schema) else 0


if __name__ == "__main__":
    raise SystemExit(main())
