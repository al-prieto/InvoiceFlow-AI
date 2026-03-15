import re


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
        r"INVOICE\s+NO\.?.*?\n\s*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
        r"INVOICE\s*#.*?\n\s*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
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


def parse_fields(text: str, patterns: dict) -> dict:
    """Extract structured fields from text using multiple regex patterns."""
    result = {}

    for field, pattern_list in patterns.items():
        result[field] = None

        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                result[field] = match.group(1).strip()
                break

    return result