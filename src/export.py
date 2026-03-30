import io
from pathlib import Path

import pandas as pd


def records_to_xlsx_bytes(records: list[dict]) -> bytes:
    """
    Serialise a list of record dicts to an in-memory Excel file.
    Used by both the Streamlit UI (download button) and the CLI exporter.
    """
    df = pd.DataFrame(records)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="invoices", index=False)
    return buf.getvalue()


def export_invoices_summary(records: list[dict], output_path: Path) -> None:
    """Write records to an Excel file at output_path. CLI / offline use only."""
    output_path.write_bytes(records_to_xlsx_bytes(records))
