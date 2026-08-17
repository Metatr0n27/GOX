# GOX Automation

**Ron Cole / GOX**

GOX is a practical automation and delivery system for turning clearly scoped digital work into tested, documented outputs. This repository is the working portfolio: real code, delivery kits, operating agents, browser tooling, QA evidence, and revenue systems.

## Verified delivery capabilities

- **Python automation** for repeatable business and data workflows
- **Public web scraping** to CSV/JSON with deduplication, page metadata, text extraction, and logging
- **Searchable PDF extraction** to structured JSON with page-level text and metadata
- **Spreadsheet/data-processing logic** including normalization, scoring, and classification
- **API/webhook integration patterns**
- **Email workflow automation**
- **Scheduled jobs, retries, logging, validation, and handoff documentation**
- **Headless/browser workflow foundations** where authenticated access is available
- **GitHub automation and CI workflows**

## Evidence-backed examples

### 1. Public-page web scraper
[`revenue-kits/web_scraper.py`](revenue-kits/web_scraper.py)

Working dependency-free scraper that:

- reads a URL list,
- fetches public pages,
- extracts title, headings, text preview, link counts, domain and byte counts,
- deduplicates repeated URLs,
- writes CSV or JSON,
- logs failures and returns a non-zero exit code when requests fail.

This is immediately usable for bounded public-page extraction jobs and can be extended with buyer-specific selectors when needed.

### 2. PDF-to-JSON extractor
[`revenue-kits/pdf_json_extractor.py`](revenue-kits/pdf_json_extractor.py)

Working searchable-PDF extractor that:

- processes folders of PDFs,
- extracts page-level and full-document text,
- preserves document metadata,
- writes structured JSON per file,
- validates output shape,
- logs failures for reproducible handoff.

Scanned/image-only PDFs may require a separate OCR stage; the portfolio does not claim otherwise.

### 3. Lead scoring and normalization
[`revenue-kits/construction_lead_scoring.py`](revenue-kits/construction_lead_scoring.py)

Reusable Python logic for:

- phone normalization,
- currency/amount parsing,
- date parsing,
- lead classification,
- weighted scoring,
- CSV ingestion.

The code is generic enough to adapt to other ranking and spreadsheet-cleanup jobs.

### 4. Browser automation foundation
[`browser_stack/`](browser_stack/)

GOX includes browser-automation work for persistent sessions, repeatable task execution, recovery, and external-result verification. Protected services can still require owner login, MFA, CAPTCHA, identity checks, or explicit legal/financial approval.

### 5. Agentic operating system
[`agents/`](agents/)

GOX uses specialized agents for opportunity discovery, execution, blocker removal, verification, QA, and revenue follow-up. The governing rule is:

> research is not delivery, a draft is not a submission, and a submission is not revenue.

## Delivery standard

For paid work, GOX aims to return:

1. working implementation,
2. configuration instructions,
3. tests or reproducible verification,
4. logging and failure handling where appropriate,
5. concise handoff documentation.

## Best-fit paid work

GOX is strongest on bounded jobs such as:

- scrape public pages into CSV/JSON,
- extract searchable PDF text into structured data,
- clean, normalize, score, or classify spreadsheet/CSV data,
- connect APIs or webhooks,
- build scheduled Python jobs,
- automate email/report workflows,
- add retries, logging, deduplication, and validation to brittle scripts,
- build small internal tools around explicit inputs, outputs, and acceptance criteria.

## Portfolio integrity

This repository does **not** invent client history, testimonials, revenue, certifications, production deployments, or enterprise experience. Public claims are limited to code, tests, CI evidence, or working implementation paths that actually exist.

## Work requests

For a serious project, send the **inputs, desired output, constraints, and acceptance criteria**. GOX is designed to scope bounded work quickly and prove fit through delivery rather than inflated claims.

---

**Portfolio owner:** Ron Cole / GOX
