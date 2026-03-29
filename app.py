import warnings

warnings.filterwarnings(
    "ignore",
    message="Signature b'.*longdouble.*does not match any known type.*",
    category=UserWarning,
)

from pathlib import Path

from src.extract import extract_from_pdf
from src.parse import parse_fields, PATTERNS
from src.validate import validate_fields
from src.export import tables_to_dataframes, export_invoices_summary
from src.pipeline import (
    CORE_FIELDS,
    OPTIONAL_FIELDS,
    get_missing_fields,
    get_status,
    build_record,
    build_error_record,
)


SAMPLES_DIR = Path("data/samples")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

VERBOSE = False


def print_file_summary(index: int, total: int, file_name: str, record: dict) -> None:
    print(f"\n[{index}/{total}] {file_name}")
    print(f"  Status: {record['status']}")
    if record["missing_core"]:
        print(f"  Missing required: {record['missing_core']}")
    if record["missing_optional"]:
        print(f"  Missing optional: {record['missing_optional']}")


def main():
    pdf_files = sorted(SAMPLES_DIR.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in data/samples")
        return

    print(f"Found {len(pdf_files)} PDF(s) in {SAMPLES_DIR}")

    invoice_records = []
    counts = {"OK": 0, "NEEDS REVIEW": 0, "FAILED": 0}

    for index, pdf_path in enumerate(pdf_files, start=1):
        try:
            full_text, raw_tables = extract_from_pdf(pdf_path)
            fields = parse_fields(full_text, PATTERNS)
            validation = validate_fields(fields)

            status = get_status(fields)
            record = build_record(pdf_path.name, fields, status)
            invoice_records.append(record)
            counts[status] = counts.get(status, 0) + 1

            print_file_summary(index, len(pdf_files), pdf_path.name, record)

            if not validation["valid"] and VERBOSE:
                print(f"  Validation issues: {'; '.join(validation['issues'])}")

            if VERBOSE:
                print("\n--- STRUCTURED DATA ---")
                for key, value in fields.items():
                    print(f"{key}: {value}")

                print("\n--- TEXT PREVIEW ---")
                print(full_text[:1500])

                print("\n--- TABLES ---")
                dataframes = tables_to_dataframes(raw_tables)
                for i, df in enumerate(dataframes, start=1):
                    print(f"\nTable {i}:")
                    print(df.head(3))

        except Exception as error:
            record = build_error_record(pdf_path.name, error)
            invoice_records.append(record)
            counts["FAILED"] += 1
            print(f"\n[{index}/{len(pdf_files)}] {pdf_path.name}")
            print("  Status: FAILED")
            print(f"  Error: {error}")

    output_file = OUTPUT_DIR / "invoice_summary.xlsx"
    export_invoices_summary(invoice_records, output_file)

    print("\nExported:")
    print(f"  Excel -> {output_file}")

    print("\nSummary:")
    print(f"  Processed : {len(pdf_files)}")
    print(f"  OK        : {counts.get('OK', 0)}")
    print(f"  Needs review: {counts.get('NEEDS REVIEW', 0)}")
    print(f"  Failed    : {counts.get('FAILED', 0)}")


if __name__ == "__main__":
    main()
