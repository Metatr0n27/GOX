# Proposal Pack — PDF Extraction Specialist

## Target
Upwork — PDF Extraction Specialist — $1,000 fixed, budget negotiable.

## Recommended Bid
**$1,250 fixed** with milestones, because scope is ~1,000 PDFs and budget is explicitly negotiable.

## Suggested Milestones
1. **$250 funded** — validate extraction specification + 25-file sample run + field mapping.
2. **$500 funded** — production pipeline + robust parsing/OCR fallback + normalized outputs.
3. **$500 funded** — full corpus run + logs + QA + documentation + final handoff.

## Ready-to-Submit Proposal
Hi — I can build this as a reproducible Python extraction pipeline rather than a one-off manual conversion.

My approach would be:
- define and validate the field mapping against your extraction specification,
- parse machine-readable PDFs with a deterministic rules-based pipeline,
- use OCR only as a flagged fallback for scanned pages,
- normalize outputs to CSV/Parquet/SQL-ready tables,
- preserve provenance for every row (source filename/URL),
- log successes, failures, parsing notes, retries, and unparseable files,
- add deduplication and validation checks,
- deliver reproducible scripts plus a clear README for Linux/cluster execution.

I would start with a small validation subset before running the full ~1,000-file corpus so we can lock the mappings and expected outputs first.

For this scope I recommend a milestone structure: validation subset first, production pipeline second, full-corpus run and final QA last. That keeps the work measurable and gives you inspectable outputs at every stage.

I can begin with the provided extraction specification and sample PDFs immediately after award.

## Technical Plan
- Python 3.11+
- pypdf/pdfplumber first-line extraction
- table adapters as required by corpus structure
- OCR fallback boundary for scanned pages
- pandas normalization
- CSV/Parquet outputs; SQL export if requested
- structured extraction log
- deterministic retries and failure isolation
- validation report on sample subset before corpus run

## Acceptance Tests
- Required fields map correctly on validation subset.
- Source filename/URL provenance retained for every record.
- Scanned/unreliable files flagged rather than silently guessed.
- Duplicate records detected and handled.
- Full run can be reproduced from command line on Linux.
- Logs clearly identify success/failure and parsing notes.

## Owner Action Required
Authenticated Upwork proposal submission only. Buyer files/specification are needed after award.
