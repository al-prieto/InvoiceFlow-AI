"""
Core pipeline logic shared between app.py (CLI) and streamlit_app.py (UI).
"""

CORE_FIELDS = ("invoice_number", "date", "total_due")
OPTIONAL_FIELDS = ("due_date", "subtotal", "sales_tax", "shipping_handling")


def get_missing_fields(fields: dict, field_names: tuple) -> list[str]:
    return [f for f in field_names if not fields.get(f)]


def get_status(fields: dict) -> str:
    """
    OK           → all core fields present
    NEEDS REVIEW → at least one core field missing, but not all
    FAILED       → all core fields missing (extraction likely failed entirely)
    """
    missing = get_missing_fields(fields, CORE_FIELDS)
    if len(missing) == len(CORE_FIELDS):
        return "FAILED"
    if missing:
        return "NEEDS REVIEW"
    return "OK"


def build_record(source_file: str, fields: dict, status: str, notes: str = "") -> dict:
    missing_core = get_missing_fields(fields, CORE_FIELDS)
    missing_opt = get_missing_fields(fields, OPTIONAL_FIELDS)
    return {
        "file": source_file,
        "invoice_number": fields.get("invoice_number"),
        "date": fields.get("date"),
        "due_date": fields.get("due_date"),
        "subtotal": fields.get("subtotal"),
        "sales_tax": fields.get("sales_tax"),
        "shipping_handling": fields.get("shipping_handling"),
        "total_due": fields.get("total_due"),
        "status": status,
        "notes": notes,
        "missing_core": ", ".join(missing_core) if missing_core else "",
        "missing_optional": ", ".join(missing_opt) if missing_opt else "",
    }


def build_error_record(source_file: str, error: Exception) -> dict:
    """Uniform record shape for files that raise during processing."""
    return {
        "file": source_file,
        "invoice_number": None,
        "date": None,
        "due_date": None,
        "subtotal": None,
        "sales_tax": None,
        "shipping_handling": None,
        "total_due": None,
        "status": "FAILED",
        "notes": "",
        "missing_core": f"processing_error: {error}",
        "missing_optional": "",
    }


def recalculate_after_correction(record: dict) -> dict:
    """
    After a manual edit, recompute status and the two missing-field lists.

    Record keys match CORE_FIELDS and OPTIONAL_FIELDS exactly, so the record
    can be passed directly without key remapping.
    Returns the mutated record for convenience.
    """
    core_snapshot = {k: record.get(k) for k in CORE_FIELDS}
    opt_snapshot = {k: record.get(k) for k in OPTIONAL_FIELDS}

    missing_core = get_missing_fields(core_snapshot, CORE_FIELDS)
    missing_opt = get_missing_fields(opt_snapshot, OPTIONAL_FIELDS)

    new_status = get_status(core_snapshot)
    # REVIEWED is auditable: means a human confirmed this is complete
    record["status"] = "REVIEWED" if new_status == "OK" else new_status
    record["missing_core"] = ", ".join(missing_core) if missing_core else ""
    record["missing_optional"] = ", ".join(missing_opt) if missing_opt else ""
    return record
