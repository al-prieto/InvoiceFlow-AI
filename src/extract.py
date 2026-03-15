import pdfplumber


def extract_from_pdf(path: str) -> tuple[str, list]:
    """Open a PDF once and return full text plus raw tables."""
    all_text = []
    all_tables = []

    with pdfplumber.open(path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")

        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                all_text.append(text)

            tables = page.extract_tables()
            if tables:
                all_tables.extend(tables)

    return "\n".join(all_text), all_tables