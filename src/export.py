import io
from pathlib import Path

import pandas as pd


def tables_to_dataframes(tables: list) -> list[pd.DataFrame]:
    """Convert raw extracted tables into pandas DataFrames."""
    dataframes = []
    for table in tables:
        if table and len(table) > 1:
            df = pd.DataFrame(table[1:], columns=table[0])
            dataframes.append(df)
    return dataframes


def records_to_xlsx_bytes(records: list[dict]) -> bytes:
    """
    Serialise a list of record dicts to an in-memory Excel file.

    Prefer this over export_invoices_summary() in the Streamlit UI so that
    no temporary files need to be written to disk.
    """
    df = pd.DataFrame(records)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="invoices", index=False)
    return buf.getvalue()


def export_invoices_summary(records: list[dict], output_path: Path) -> None:
    """Write records to an Excel file at output_path (CLI / offline use)."""
    output_path.write_bytes(records_to_xlsx_bytes(records))
