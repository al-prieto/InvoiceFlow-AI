"""
Core pipeline logic shared between app.py (CLI) and streamlit_app.py (UI).

Previously duplicated across both entry points with subtle differences
(e.g. "source_file" vs "file" key). Centralising here ensures a single
source of truth for status logic, field schema, and record construction.
"""

CORE_FIELDS = ("invoice_number", "date", "total_due")
OPTIONAL_FIELDS = ("due_date", "subtotal", "sales_tax", "shipping_handling")

# Canonical record keys — both CLI and UI must use this schema.
RECORD_KEYS = (
    "file",
    "invoice_number",
    "date",
    "due_date",
    "subtotal",
    "sales_tax",
    "shipping",
    "total_due",
    "status",
    "notes",
    "missing_core",
    "missing_optional",
)


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
        "shipping": fields.get("shipping_handling"),
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
        "shipping": None,
        "total_due": None,
        "status": "FAILED",
        "notes": "",
        "missing_core": f"processing_error: {error}",
        "missing_optional": "",
    }
