def validate_fields(fields: dict) -> dict:
    """Run simple validation rules over extracted fields."""
    validation = {}

    validation["invoice_number_present"] = fields.get("invoice_number") is not None
    validation["date_present"] = fields.get("date") is not None
    validation["due_date_present"] = fields.get("due_date") is not None
    validation["subtotal_present"] = fields.get("subtotal") is not None
    validation["sales_tax_present"] = fields.get("sales_tax") is not None
    validation["shipping_handling_present"] = fields.get("shipping_handling") is not None
    validation["total_due_present"] = fields.get("total_due") is not None

    return validation