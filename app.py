from pathlib import Path

from src.extract import extract_from_pdf
from src.parse import parse_fields, PATTERNS
from src.validate import validate_fields
from src.export import tables_to_dataframes, export_invoices_summary


SAMPLES_DIR = Path("data/samples")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def main():
    pdf_files = sorted(SAMPLES_DIR.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in data/samples")
        return

    invoice_records = []

    for pdf_path in pdf_files:
        print(f"\n{'=' * 60}")
        print(f"Processing file: {pdf_path.name}")
        print(f"{'=' * 60}")

        full_text, raw_tables = extract_from_pdf(pdf_path)

        print("\n--- TEXT PREVIEW ---")
        print(full_text[:1500])

        print("\n--- STRUCTURED DATA ---")
        fields = parse_fields(full_text, PATTERNS)
        for key, value in fields.items():
            print(f"{key}: {value}")

        print("\n--- VALIDATION ---")
        validation = validate_fields(fields)
        for key, value in validation.items():
            print(f"{key}: {value}")

        print("\n--- TABLES ---")
        dataframes = tables_to_dataframes(raw_tables)
        for i, df in enumerate(dataframes, start=1):
            print(f"\nTable {i}:")
            print(df.head(3))

        record = {
            "source_file": pdf_path.name,
            "invoice_number": fields.get("invoice_number"),
            "date": fields.get("date"),
            "due_date": fields.get("due_date"),
            "subtotal": fields.get("subtotal"),
            "sales_tax": fields.get("sales_tax"),
            "shipping_handling": fields.get("shipping_handling"),
            "total_due": fields.get("total_due"),
        }
        invoice_records.append(record)

    output_file = OUTPUT_DIR / "invoice_summary.xlsx"
    export_invoices_summary(invoice_records, output_file)

    print(f"\nExcel summary created: {output_file}")


if __name__ == "__main__":
    main()