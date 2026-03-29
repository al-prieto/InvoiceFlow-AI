"""
Validation rules that run after field extraction.

Previously validate_fields() existed but its output was never used to
determine status or surface issues in the UI. Now it returns structured
findings that can be displayed and stored.
"""


def _parse_amount(value: str | None) -> float | None:
    """Convert a string like '1,234.56' to a float. Returns None on failure."""
    if not value:
        return None
    try:
        return float(value.replace(",", "").strip())
    except ValueError:
        return None


def validate_fields(fields: dict) -> dict:
    """
    Run validation rules over extracted fields.

    Returns:
        {
            "valid": bool,
            "issues": list[str]   # human-readable problem descriptions
        }
    """
    issues: list[str] = []

    # ── Core presence checks ──────────────────────────────────────────────────
    if not fields.get("invoice_number"):
        issues.append("Missing invoice number")

    if not fields.get("date"):
        issues.append("Missing invoice date")

    if not fields.get("total_due"):
        issues.append("Missing total due")

    # ── Numeric sanity checks ─────────────────────────────────────────────────
    total = _parse_amount(fields.get("total_due"))
    subtotal = _parse_amount(fields.get("subtotal"))
    tax = _parse_amount(fields.get("sales_tax"))

    if total is not None and total <= 0:
        issues.append(f"Total due is not positive ({total})")

    if subtotal is not None and tax is not None and total is not None:
        expected = round(subtotal + tax, 2)
        if abs(expected - total) > 0.02:
            issues.append(
                f"Subtotal + tax ({expected:.2f}) does not match total ({total:.2f})"
            )

    # ── Invoice number minimum quality check ──────────────────────────────────
    inv_num = fields.get("invoice_number")
    if inv_num and len(inv_num.strip()) < 2:
        issues.append(f"Invoice number looks too short: '{inv_num}'")

    return {"valid": len(issues) == 0, "issues": issues}
