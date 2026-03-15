import re


PATTERNS = {
    "invoice_number": r"INVOICE\s*#\s*([A-Z0-9-]+)",
    "date": r"DATE:\s*([0-9./-]+)",
    "subtotal": r"SUBTOTAL\s+([\d,]+\.\d{2})",
    "total_due": r"TOTAL\s+DUE\s+([\d,]+\.\d{2})",
}


def parse_fields(text: str, patterns: dict) -> dict:
    """Extract structured fields from text using regex patterns."""
    result = {}

    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        result[field] = match.group(1) if match else None

    return result