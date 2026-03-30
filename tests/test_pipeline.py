"""
Tests for src.pipeline.
"""

from src.pipeline import (
    get_status,
    get_missing_fields,
    build_record,
    recalculate_after_correction,
    CORE_FIELDS,
    OPTIONAL_FIELDS,
)


class TestGetMissingFields:
    def test_returns_empty_when_all_present(self):
        fields = {
            "invoice_number": "INV-001",
            "date": "2024-03-15",
            "total_due": "100.00",
        }
        assert get_missing_fields(fields, CORE_FIELDS) == []

    def test_returns_missing_keys(self):
        fields = {"invoice_number": "INV-001", "date": None, "total_due": None}
        missing = get_missing_fields(fields, CORE_FIELDS)
        assert "date" in missing
        assert "total_due" in missing
        assert "invoice_number" not in missing

    def test_empty_string_counts_as_missing(self):
        fields = {"invoice_number": "", "date": "2024-03-15", "total_due": "100.00"}
        assert "invoice_number" in get_missing_fields(fields, CORE_FIELDS)


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


class TestBuildRecord:
    def test_schema_has_all_expected_keys(self):
        fields = {
            "invoice_number": "INV-001",
            "date": "2024-03-15",
            "total_due": "100.00",
            "due_date": None,
            "subtotal": None,
            "sales_tax": None,
            "shipping_handling": None,
        }
        record = build_record("test.pdf", fields, "OK")
        expected_keys = {
            "file",
            "invoice_number",
            "date",
            "due_date",
            "subtotal",
            "sales_tax",
            "shipping_handling",
            "total_due",
            "status",
            "notes",
            "missing_core",
            "missing_optional",
        }
        assert set(record.keys()) == expected_keys

    def test_missing_core_populated_correctly(self):
        fields = {
            "invoice_number": "INV-001",
            "date": None,
            "total_due": None,
            "due_date": None,
            "subtotal": None,
            "sales_tax": None,
            "shipping_handling": None,
        }
        record = build_record("test.pdf", fields, "NEEDS REVIEW")
        assert "date" in record["missing_core"]
        assert "total_due" in record["missing_core"]
        assert "invoice_number" not in record["missing_core"]

    def test_record_key_is_file_not_source_file(self):
        fields = {
            "invoice_number": "X",
            "date": "2024-01-01",
            "total_due": "50.00",
            "due_date": None,
            "subtotal": None,
            "sales_tax": None,
            "shipping_handling": None,
        }
        record = build_record("invoice.pdf", fields, "OK")
        assert record["file"] == "invoice.pdf"
        assert "source_file" not in record


class TestRecalculateAfterCorrection:
    def _base_record(self):
        return {
            "file": "test.pdf",
            "invoice_number": None,
            "date": None,
            "total_due": None,
            "due_date": None,
            "subtotal": None,
            "sales_tax": None,
            "shipping_handling": None,
            "status": "FAILED",
            "notes": "",
            "missing_core": "invoice_number, date, total_due",
            "missing_optional": "",
        }

    def test_becomes_reviewed_when_all_core_filled(self):
        record = self._base_record()
        record["invoice_number"] = "INV-001"
        record["date"] = "2024-03-15"
        record["total_due"] = "100.00"
        recalculate_after_correction(record)
        assert record["status"] == "REVIEWED"
        assert record["missing_core"] == ""

    def test_stays_needs_review_when_core_still_missing(self):
        record = self._base_record()
        record["invoice_number"] = "INV-001"
        record["date"] = "2024-03-15"
        # total_due still None
        recalculate_after_correction(record)
        assert record["status"] == "NEEDS REVIEW"
        assert "total_due" in record["missing_core"]

    def test_missing_optional_updated_correctly(self):
        record = self._base_record()
        record["invoice_number"] = "INV-001"
        record["date"] = "2024-03-15"
        record["total_due"] = "200.00"
        record["subtotal"] = "180.00"
        # sales_tax, due_date, shipping_handling still None
        recalculate_after_correction(record)
        assert record["status"] == "REVIEWED"
        assert "sales_tax" in record["missing_optional"]
        assert "subtotal" not in record["missing_optional"]
