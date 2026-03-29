"""
Tests for src.pipeline.
"""

from src.pipeline import get_status

# TODO:
# Add tests for get_missing_fields() and build_record()

# ── get_status ────────────────────────────────────────────────────────────────


class TestGetStatus:
    def test_ok_when_all_core_present(self):
        fields = {
            "invoice_number": "INV-001",
            "date": "2024-03-15",
            "total_due": "100.00",
        }
        assert get_status(fields) == "OK"

    def test_needs_review_when_one_core_missing(self):
        fields = {"invoice_number": "INV-001", "date": "2024-03-15", "total_due": None}
        assert get_status(fields) == "NEEDS REVIEW"

    def test_failed_when_all_core_missing(self):
        fields = {"invoice_number": None, "date": None, "total_due": None}
        assert get_status(fields) == "FAILED"

    def test_optional_missing_does_not_affect_status(self):
        fields = {
            "invoice_number": "INV-001",
            "date": "2024-03-15",
            "total_due": "100.00",
            "subtotal": None,
            "sales_tax": None,
        }
        assert get_status(fields) == "OK"
