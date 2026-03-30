# TODO — InvoiceFlow-AI

## Current state (as of this pass)

- [x] CLI batch processor (`app.py`)
- [x] Streamlit UI with upload, extraction, metrics, review, export
- [x] Shared pipeline logic in `src/pipeline.py`
- [x] Validation with meaningful issue messages (`src/validate.py`)
- [x] Manual correction form for NEEDS REVIEW / FAILED rows
- [x] Status recalculation after correction (`REVIEWED` status)
- [x] CSS extracted to `src/ui_styles.py`
- [x] Tests for parse, pipeline, validate

## Next (product)

- [ ] Show extracted text snippet next to the review form so the reviewer can see
      what the PDF actually says (helps verify corrections are right)
- [ ] After correction, re-run validate_fields and show updated issues inline
      without requiring a full rerun
- [ ] Export button shows count of still-unreviewed rows as a warning before download

## Next (tech)

- [ ] `normalize_date`: add a `date_format_hint` field to the record so the UI
      can show the original raw value alongside the normalized one
- [ ] Add integration test: process a real sample PDF end-to-end and assert
      the record schema is complete and status is not FAILED
- [ ] `parse.py`: DOTALL still used implicitly by some patterns — audit each
      pattern individually and document which ones need it vs MULTILINE only

## Out of scope for now (explicitly deferred)

- OCR for scanned invoices
- Persistent storage / database
- Auth / login
- Multi-user / multi-client
- Email ingestion
- Watchdog folder polling
