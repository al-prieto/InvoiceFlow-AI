"""
CLI entry point for InvoiceFlow-AI.

Batch-processes all PDFs in data/samples/ and writes a summary Excel to outputs/.
This is a developer / offline tool. The main product interface is streamlit_app.py.

Usage:
    python app.py
    VERBOSE=1 python app.py   # prints extracted text and tables per invoice
"""

import warnings
import os

warnings.filterwarnings(
    "ignore",
    message="Signature b'.*longdouble.*does not match any known type.*",
    category=UserWarning,
)

from pathlib import Path

import pandas as pd

from src.extract import extract_from_pdf
from src.parse import parse_fields, PATTERNS
from src.validate import validate_fields
from src.export import export_invoices_summary
from src.pipeline import get_status, build_record, build_error_record


SAMPLES_DIR = Path("data/samples")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

VERBOSE = os.getenv("VERBOSE", "0") == "1"


def _tables_to_dataframes(tables: list) -> list[pd.DataFrame]:
    """Debug helper: convert raw pdfplumber tables to DataFrames for inspection."""
    return [pd.DataFrame(t[1:], columns=t[0]) for t in tables if t and len(t) > 1]


def _print_summary(index: int, total: int, file_name: str, record: dict) -> None:
    print(f"\n[{index}/{total}] {file_name}")
    print(f"  Status: {record['status']}")
    if record["missing_core"]:
        print(f"  Missing required : {record['missing_core']}")
    if record["missing_optional"]:
        print(f"  Missing optional : {record['missing_optional']}")


def main():
    pdf_files = sorted(SAMPLES_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {SAMPLES_DIR}")
        return

    print(f"Found {len(pdf_files)} PDF(s) in {SAMPLES_DIR}")

    invoice_records = []
    counts: dict[str, int] = {"OK": 0, "NEEDS REVIEW": 0, "FAILED": 0}

    for index, pdf_path in enumerate(pdf_files, start=1):
        try:
            full_text, raw_tables = extract_from_pdf(pdf_path)
            fields = parse_fields(full_text, PATTERNS)
            validation = validate_fields(fields)
            status = get_status(fields)
            record = build_record(pdf_path.name, fields, status)
            invoice_records.append(record)
            counts[status] = counts.get(status, 0) + 1

            _print_summary(index, len(pdf_files), pdf_path.name, record)

            if VERBOSE:
                if not validation["valid"]:
                    print(f"  Validation : {'; '.join(validation['issues'])}")
                print("\n--- STRUCTURED DATA ---")
                for key, value in fields.items():
                    print(f"  {key}: {value}")
                print("\n--- TEXT PREVIEW ---")
                print(full_text[:1500])
                print("\n--- TABLES ---")
                for i, df in enumerate(_tables_to_dataframes(raw_tables), start=1):
                    print(f"\nTable {i}:")
                    print(df.head(3))

        except Exception as error:
            record = build_error_record(pdf_path.name, error)
            invoice_records.append(record)
            counts["FAILED"] = counts.get("FAILED", 0) + 1
            print(f"\n[{index}/{len(pdf_files)}] {pdf_path.name}")
            print(f"  Status: FAILED — {error}")

    output_file = OUTPUT_DIR / "invoice_summary.xlsx"
    export_invoices_summary(invoice_records, output_file)

    print(f"\nExported → {output_file}")
    print(
        f"\nSummary: {len(pdf_files)} processed | "
        f"{counts.get('OK', 0)} OK | "
        f"{counts.get('NEEDS REVIEW', 0)} needs review | "
        f"{counts.get('FAILED', 0)} failed"
    )


if __name__ == "__main__":
    main()
