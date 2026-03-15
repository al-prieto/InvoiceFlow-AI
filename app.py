from pathlib import Path

from src.extract import extract_from_pdf
from src.parse import parse_fields, PATTERNS
from src.validate import validate_fields
from src.export import tables_to_dataframes


SAMPLES_DIR = Path("data/samples")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def main():
    pdf_files = sorted(SAMPLES_DIR.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in data/samples")
        return

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


if __name__ == "__main__":
    main()