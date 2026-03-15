import pandas as pd


def tables_to_dataframes(tables: list) -> list[pd.DataFrame]:
    """Convert raw extracted tables into pandas DataFrames."""
    dataframes = []

    for table in tables:
        if table and len(table) > 1:
            df = pd.DataFrame(table[1:], columns=table[0])
            dataframes.append(df)

    return dataframes