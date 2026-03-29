"""
Tests for parsing and date normalization in InvoiceFlow-AI.

Run with: python -m pytest tests/ -v
"""

from src.parse import normalize_date, parse_fields, PATTERNS

# ── normalize_date ────────────────────────────────────────────────────────────


class TestNormalizeDate:
    def test_european_dot(self):
        assert normalize_date("15.03.2024") == "2024-03-15"

    def test_european_slash(self):
        assert normalize_date("15/03/2024") == "2024-03-15"

    def test_european_dash(self):
        assert normalize_date("15-03-2024") == "2024-03-15"

    def test_long_month(self):
        assert normalize_date("March 15, 2024") == "2024-03-15"

    def test_us_slash(self):
        # MM/DD/YYYY — day > 12 makes the format unambiguous
        assert normalize_date("03/15/2024") == "2024-03-15"

    def test_iso_passthrough(self):
        assert normalize_date("2024-03-15") == "2024-03-15"

    def test_none_returns_none(self):
        assert normalize_date(None) is None

    def test_unparseable_returns_original(self):
        # Should return the raw value, not None, so callers know a value exists
        raw = "not-a-date"
        assert normalize_date(raw) == raw


# ── parse_fields ──────────────────────────────────────────────────────────────

SAMPLE_INVOICE_TEXT = """
INVOICE NUMBER: INV-2024-001
DATE: 15/03/2024
TOTAL DUE: 1,250.00
SUBTOTAL: 1,150.00
SALES TAX: 100.00
"""

SAMPLE_INVOICE_US_DATE = """
INVOICE #: 98765
INVOICE DATE: 03/15/2024
AMOUNT DUE: 500.00
"""


class TestParseFields:
    def test_extracts_invoice_number(self):
        result = parse_fields(SAMPLE_INVOICE_TEXT, PATTERNS)
        assert result["invoice_number"] == "INV-2024-001"

    def test_extracts_and_normalises_date(self):
        result = parse_fields(SAMPLE_INVOICE_TEXT, PATTERNS)
        assert result["date"] == "2024-03-15"

    def test_extracts_total_due(self):
        result = parse_fields(SAMPLE_INVOICE_TEXT, PATTERNS)
        assert result["total_due"] == "1,250.00"

    def test_extracts_subtotal(self):
        result = parse_fields(SAMPLE_INVOICE_TEXT, PATTERNS)
        assert result["subtotal"] == "1,150.00"

    def test_missing_field_is_none(self):
        result = parse_fields(SAMPLE_INVOICE_TEXT, PATTERNS)
        assert result["due_date"] is None

    def test_us_date_format(self):
        result = parse_fields(SAMPLE_INVOICE_US_DATE, PATTERNS)
        assert result["date"] == "2024-03-15"
