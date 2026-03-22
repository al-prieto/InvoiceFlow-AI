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


SAMPLES_DIR = Path("data/samples")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

VERBOSE = False

CORE_FIELDS = ("invoice_number", "date", "total_due")
OPTIONAL_FIELDS = ("due_date", "subtotal", "sales_tax", "shipping_handling")


def get_missing_fields(fields: dict, field_names: tuple[str, ...]) -> list[str]:
    return [field for field in field_names if not fields.get(field)]


def get_status(fields: dict) -> str:
    missing_core = get_missing_fields(fields, CORE_FIELDS)

    if len(missing_core) == len(CORE_FIELDS):
        return "FAILED"

    if missing_core:
        return "REVIEW NEEDED"

    return "OK"


def build_record(source_file: str, fields: dict, status: str) -> dict:
    missing_core = get_missing_fields(fields, CORE_FIELDS)
    missing_optional = get_missing_fields(fields, OPTIONAL_FIELDS)

    return {
        "source_file": source_file,
        "invoice_number": fields.get("invoice_number"),
        "date": fields.get("date"),
        "due_date": fields.get("due_date"),
        "subtotal": fields.get("subtotal"),
        "sales_tax": fields.get("sales_tax"),
        "shipping_handling": fields.get("shipping_handling"),
        "total_due": fields.get("total_due"),
        "status": status,
        "missing_core_fields": ", ".join(missing_core) if missing_core else "",
        "missing_optional_fields": (
            ", ".join(missing_optional) if missing_optional else ""
        ),
    }


def print_file_summary(index: int, total: int, file_name: str, record: dict) -> None:
    print(f"\n[{index}/{total}] {file_name}")
    print(f"  Status: {record['status']}")

    if record["missing_core_fields"]:
        print(f"  Missing required: {record['missing_core_fields']}")

    if record["missing_optional_fields"]:
        print(f"  Missing optional: {record['missing_optional_fields']}")


def main():
    pdf_files = sorted(SAMPLES_DIR.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in data/samples")
        return

    print(f"Found {len(pdf_files)} PDF(s) in {SAMPLES_DIR}")

    invoice_records = []
    counts = {
        "OK": 0,
        "REVIEW NEEDED": 0,
        "FAILED": 0,
    }

    for index, pdf_path in enumerate(pdf_files, start=1):
        try:
            full_text, raw_tables = extract_from_pdf(pdf_path)
            fields = parse_fields(full_text, PATTERNS)
            validation = validate_fields(fields)

            status = get_status(fields)
            record = build_record(pdf_path.name, fields, status)
            invoice_records.append(record)
            counts[status] += 1

            print_file_summary(index, len(pdf_files), pdf_path.name, record)

            if VERBOSE:
                print("\n--- STRUCTURED DATA ---")
                for key, value in fields.items():
                    print(f"{key}: {value}")

                print("\n--- VALIDATION ---")
                for key, value in validation.items():
                    print(f"{key}: {value}")

                print("\n--- TEXT PREVIEW ---")
                print(full_text[:1500])

                print("\n--- TABLES ---")
                dataframes = tables_to_dataframes(raw_tables)
                for i, df in enumerate(dataframes, start=1):
                    print(f"\nTable {i}:")
                    print(df.head(3))

        except Exception as error:
            record = {
                "source_file": pdf_path.name,
                "invoice_number": None,
                "date": None,
                "due_date": None,
                "subtotal": None,
                "sales_tax": None,
                "shipping_handling": None,
                "total_due": None,
                "status": "FAILED",
                "missing_core_fields": "processing_error",
                "missing_optional_fields": "",
            }
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
    print(f"  Processed: {len(pdf_files)}")
    print(f"  OK: {counts['OK']}")
    print(f"  Review needed: {counts['REVIEW NEEDED']}")
    print(f"  Failed: {counts['FAILED']}")


if __name__ == "__main__":
    main()
