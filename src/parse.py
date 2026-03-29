import re
from datetime import datetime


PATTERNS = {
    "invoice_number": [
        r"INVOICE\s*NUMBER[:\s]*([A-Z0-9#-]*\d[A-Z0-9#-]*)",
        r"INVOICE\s+NO\.?[:\s]*([A-Z0-9#-]*\d[A-Z0-9#-]*)",
        r"INVOICE\s*#[:\s]*([A-Z0-9#-]*\d[A-Z0-9#-]*)",
        r"INVOICE\s*\n\s*([A-Z0-9#-]*\d[A-Z0-9#-]*)",
    ],
    "date": [
        r"DATE[:\s]*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
        r"DATE[:\s]*([A-Z][a-z]+\s+\d{1,2},\s+\d{4})",
        r"INVOICE\s+DATE[:\s]*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
        r"INVOICE\s+DATE[:\s]*([A-Z][a-z]+\s+\d{1,2},\s+\d{4})",
        # Note: these two use MULTILINE only (not DOTALL) to avoid cross-page matches
        r"INVOICE\s+NO\.?[^\n]*\n\s*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
        r"INVOICE\s*#[^\n]*\n\s*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
        r"DATE\s+TO\s+SHIP\s+TO\s*\n.*?\b([A-Z][a-z]+\s+\d{1,2},\s+\d{4})\b",
    ],
    "due_date": [
        r"ORDER\s+DATE\s+ORDER\s+NUMBER\s+DUE\s+DATE\s*\n[0-9./-]+\s+\S+\s+([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
        r"DUE[-\s]*DATE[:\s]*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
        r"DUE[-\s]*DATE[:\s]*([A-Z][a-z]+\s+\d{1,2},\s+\d{4})",
        r"TOTAL\s+DUE\s+BY[:\s]*([A-Z][a-z]+\s+\d{1,2},\s+\d{4})",
    ],
    "subtotal": [
        r"SUBTOTAL[:\s$]*([\d,]+(?:\.\d{2})?)",
    ],
    "sales_tax": [
        r"SALES\s+TAX[:\s$]*([\d,]+(?:\.\d{2})?)",
    ],
    "shipping_handling": [
        r"SHIPPING\s*(?:&|AND)\s*HANDLING[:\s$]*([\d,]+(?:\.\d{2})?)",
    ],
    "total_due": [
        r"TOTAL\s+DUE[:\s$]*([\d,]+(?:\.\d{2})?)",
        r"AMOUNT\s+DUE[:\s$]*([\d,]+(?:\.\d{2})?)",
        r"BALANCE\s+DUE[:\s$]*([\d,]+(?:\.\d{2})?)",
        r"TOTAL\s+DUE\s+BY[:\s]*[A-Z][a-z]+\s+\d{1,2},\s+\d{4}\s+([\d,]+(?:\.\d{2})?)",
    ],
}

# Date formats tried in order. The US format (MM/DD/YYYY) is added after the
# European ambiguous formats so that DD/MM/YYYY is attempted first for dates
# where both interpretations are valid (e.g. 01/06). For unambiguous US dates
# like 13/01 or month > 12, US_FALLBACK kicks in.
_DATE_FORMATS = [
    ("%d.%m.%Y", "DD.MM.YYYY"),
    ("%d/%m/%Y", "DD/MM/YYYY"),
    ("%d-%m-%Y", "DD-MM-YYYY"),
    ("%B %d, %Y", "Month DD, YYYY"),
    ("%m/%d/%Y", "MM/DD/YYYY"),  # US format — tried after European
    ("%m-%d-%Y", "MM-DD-YYYY"),
    ("%m.%d.%Y", "MM.DD.YYYY"),
    ("%Y-%m-%d", "YYYY-MM-DD"),  # ISO — already normalised, pass-through
]


def normalize_date(date_value: str | None) -> str | None:
    """
    Convert supported date string formats to YYYY-MM-DD.

    Returns the original string unchanged (not None) if no format matches,
    so callers can detect that the value exists but couldn't be parsed cleanly.
    """
    if not date_value:
        return None

    for fmt, _ in _DATE_FORMATS:
        try:
            return datetime.strptime(date_value.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Return raw value rather than silently dropping it.
    return date_value


def parse_fields(text: str, patterns: dict) -> dict:
    """Extract structured fields from text using multiple regex patterns."""
    result = {}

    for field, pattern_list in patterns.items():
        result[field] = None

        for pattern in pattern_list:
            # Use MULTILINE instead of DOTALL for patterns that should not
            # bleed across page boundaries.
            flags = re.IGNORECASE | re.MULTILINE
            match = re.search(pattern, text, flags)
            if match:
                result[field] = match.group(1).strip()
                break

    result["date"] = normalize_date(result.get("date"))
    result["due_date"] = normalize_date(result.get("due_date"))

    return result
