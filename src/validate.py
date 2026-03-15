def validate_fields(fields: dict) -> dict:
    """Run simple validation rules over extracted fields."""
    validation = {}

    validation["invoice_number_present"] = fields.get("invoice_number") is not None
    validation["date_present"] = fields.get("date") is not None
    validation["subtotal_present"] = fields.get("subtotal") is not None
    validation["total_due_present"] = fields.get("total_due") is not None

    return validation