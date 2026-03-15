from src.extract import extract_from_pdf
from src.parse import parse_fields, PATTERNS
from src.validate import validate_fields
from src.export import tables_to_dataframes
from pathlib import Path

PDF_PATH = "data/samples/sample_invoice.pdf"

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def main():
    full_text, raw_tables = extract_from_pdf(PDF_PATH)

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
    for i, df in enumerate(dataframes):
        print(f"\nTable {i + 1}:")
        print(df.head(3))


if __name__ == "__main__":
    main()