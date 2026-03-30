from src.validate import validate_fields


class TestValidateFields:
    def test_valid_when_all_core_present_and_amounts_match(self):
        fields = {
            "invoice_number": "INV-001",
            "date": "2024-03-15",
            "total_due": "1,150.00",
            "subtotal": "1,050.00",
            "sales_tax": "100.00",
        }
        result = validate_fields(fields)
        assert result["valid"] is True
        assert result["issues"] == []

    def test_flags_missing_invoice_number(self):
        fields = {"invoice_number": None, "date": "2024-03-15", "total_due": "100.00"}
        result = validate_fields(fields)
        assert not result["valid"]
        assert any("invoice number" in i.lower() for i in result["issues"])

    def test_flags_zero_total(self):
        fields = {
            "invoice_number": "INV-001",
            "date": "2024-03-15",
            "total_due": "0.00",
        }
        result = validate_fields(fields)
        assert not result["valid"]
        assert any("positive" in i.lower() for i in result["issues"])

    def test_flags_subtotal_tax_mismatch(self):
        fields = {
            "invoice_number": "INV-001",
            "date": "2024-03-15",
            "total_due": "200.00",
            "subtotal": "100.00",
            "sales_tax": "50.00",
        }
        result = validate_fields(fields)
        assert not result["valid"]
        assert any("match" in i.lower() for i in result["issues"])

    def test_flags_single_char_invoice_number(self):
        fields = {"invoice_number": "1", "date": "2024-03-15", "total_due": "100.00"}
        result = validate_fields(fields)
        assert not result["valid"]
        assert any("short" in i.lower() for i in result["issues"])
