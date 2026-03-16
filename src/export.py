import pandas as pd
from pathlib import Path


def tables_to_dataframes(tables: list) -> list[pd.DataFrame]:
    """Convert raw extracted tables into pandas DataFrames."""
    dataframes = []

    for table in tables:
        if table and len(table) > 1:
            df = pd.DataFrame(table[1:], columns=table[0])
            dataframes.append(df)

    return dataframes


def export_invoices_summary(records: list[dict], output_path: Path) -> None:
    """Export one row per invoice into a single Excel file."""
    summary_df = pd.DataFrame(records)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="invoices", index=False)