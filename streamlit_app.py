import warnings

warnings.filterwarnings(
    "ignore",
    message="Signature b'.*longdouble.*does not match any known type.*",
    category=UserWarning,
)

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import streamlit as st

from src.extract import extract_from_pdf
from src.parse import parse_fields, PATTERNS
from src.export import export_invoices_summary


# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InvoiceFlow",
    page_icon="📄",
    layout="centered",
)

CORE_FIELDS = ("invoice_number", "date", "total_due")
OPTIONAL_FIELDS = ("due_date", "subtotal", "sales_tax", "shipping_handling")


# ── CSS ───────────────────────────────────────────────────────────────────────
def inject_css() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');

            html, body, [class*="css"] {
                font-family: 'DM Sans', sans-serif;
            }

            .stApp {
                background: #f7f7f8;
            }

            .block-container {
                max-width: 680px;
                padding-top: 4rem;
                padding-bottom: 4rem;
            }

            /* Hide Streamlit chrome */
            #MainMenu, footer, header { visibility: hidden; }

            /* Title block */
            .app-header {
                text-align: center;
                margin-bottom: 2.5rem;
            }
            .app-title {
                font-size: 2.4rem;
                font-weight: 700;
                color: #111;
                letter-spacing: -0.03em;
                margin-bottom: 0.4rem;
            }
            .app-sub {
                font-size: 1rem;
                color: #777;
            }

            /* Upload zone */
            [data-testid="stFileUploaderDropzone"] {
                background: #fff;
                border: 2px dashed #d0d0d5;
                border-radius: 16px;
                padding: 2rem 1.5rem;
                transition: border-color 0.2s;
            }
            [data-testid="stFileUploaderDropzone"]:hover {
                border-color: #4c7ef3;
            }

            /* Process button */
            .stButton > button {
                width: 100%;
                height: 3.5rem;
                border-radius: 12px;
                border: none;
                background: #4c7ef3;
                color: white;
                font-family: 'DM Sans', sans-serif;
                font-weight: 700;
                font-size: 1rem;
                margin-top: 1rem;
                margin-bottom: 1rem;
                transition: background 0.15s;
            }

            .stButton > button p {
    font-size: 1.25rem !important;
    margin: 0 !important;
    line-height: 1 !important;
    color: white !important;
}
            .stButton > button:hover {
                background: #3a6ae0;
                color: white;
            }

            /* Metrics row */
            .metrics-row {
                display: flex;
                gap: 1rem;
                margin: 2rem 0 1rem;
            }
            .metric-box {
                flex: 1;
                background: #fff;
                border: 1px solid #e8e8ec;
                border-radius: 14px;
                padding: 1rem;
                text-align: center;
            }
            .metric-num {
                font-size: 2rem;
                font-weight: 700;
                color: #111;
                line-height: 1;
            }
            .metric-lbl {
                font-size: 0.8rem;
                color: #888;
                margin-top: 0.3rem;
            }

           

            /* Download button */
            .stDownloadButton > button {
                width: 100%;
                height: 3rem;
                border-radius: 12px;
                border: 1.5px solid #d0d0d5;
                background: #fff;
                color: #111;
                font-family: 'DM Sans', sans-serif;
                font-weight: 600;
                font-size: 0.95rem;
            }
            .stDownloadButton > button:hover {
                border-color: #4c7ef3;
                color: #4c7ef3;
                background: #fff;
            }

            /* Status chips in dataframe */
            .chip {
                display: inline-block;
                padding: 2px 10px;
                border-radius: 999px;
                font-size: 0.75rem;
                font-weight: 600;
            }

            /* Warning */
[data-testid="stAlert"] {
    border-radius: 12px;
}

[data-testid="stAlertContentWarning"] p {
    color: #111;
    font-weight: 500;
}

/* --- FIX UPLOADER Y LISTA DE ARCHIVOS --- */

/* Forzar color oscuro para TODO el texto dentro del uploader (incluye la lista de archivos) */
[data-testid="stFileUploader"] div,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] small {
    color: #111111 !important;
}

/* Estilizar el botón nativo de "Browse files" */
[data-testid="stFileUploaderDropzone"] button {
    background-color: #111111 !important;
    color: #ffffff !important; /* Este texto sí va en blanco */
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

/* Hover del botón de "Browse files" */
[data-testid="stFileUploaderDropzone"] button:hover {
    background-color: #4c7ef3 !important;
    color: #ffffff !important;
}

/* Quitar el borde al enfocar */
[data-testid="stFileUploaderDropzone"] button:focus:not(:focus-visible) {
    color: #ffffff !important;
}

/* Asegurar que el ícono "X" para eliminar archivos se vea oscuro */
[data-testid="stUploadedFile"] svg {
    fill: #111111 !important;
}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_missing_fields(fields: dict, field_names: tuple) -> list[str]:
    return [f for f in field_names if not fields.get(f)]


def get_status(fields: dict) -> str:
    missing = get_missing_fields(fields, CORE_FIELDS)
    if len(missing) == len(CORE_FIELDS):
        return "FAILED"
    if missing:
        return "NEEDS REVIEW"
    return "OK"


def build_record(source_file: str, fields: dict, status: str) -> dict:
    missing_core = get_missing_fields(fields, CORE_FIELDS)
    missing_opt = get_missing_fields(fields, OPTIONAL_FIELDS)
    return {
        "file": source_file,
        "invoice_number": fields.get("invoice_number"),
        "date": fields.get("date"),
        "due_date": fields.get("due_date"),
        "subtotal": fields.get("subtotal"),
        "sales_tax": fields.get("sales_tax"),
        "shipping": fields.get("shipping_handling"),
        "total_due": fields.get("total_due"),
        "status": status,
        "missing_core": ", ".join(missing_core) if missing_core else "",
        "missing_optional": ", ".join(missing_opt) if missing_opt else "",
    }


def process_files(uploaded_files) -> tuple[list[dict], bytes]:
    records = []
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for f in uploaded_files:
            dest = tmp_path / f.name
            dest.write_bytes(f.getbuffer())
            try:
                full_text, _ = extract_from_pdf(dest)
                fields = parse_fields(full_text, PATTERNS)
                status = get_status(fields)
                record = build_record(f.name, fields, status)
            except Exception:
                record = {
                    k: None
                    for k in (
                        "invoice_number",
                        "date",
                        "due_date",
                        "subtotal",
                        "sales_tax",
                        "shipping",
                        "total_due",
                        "missing_core",
                        "missing_optional",
                    )
                }
                record.update(
                    {
                        "file": f.name,
                        "status": "FAILED",
                        "missing_core": "processing_error",
                    }
                )
            records.append(record)

        out = tmp_path / "invoice_summary.xlsx"
        export_invoices_summary(records, out)
        xlsx = out.read_bytes()

    return records, xlsx


# ── Session state ─────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "xlsx" not in st.session_state:
    st.session_state.xlsx = None


# ── UI ────────────────────────────────────────────────────────────────────────
inject_css()

st.markdown(
    """
    <div class="app-header">
        <div class="app-title">InvoiceFlow</div>
        <div class="app-sub">Upload invoice PDFs · Extract key fields · Export to Excel</div>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded = st.file_uploader(
    "Upload PDF invoices",
    type=["pdf"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if uploaded:
    file_count = len(uploaded)
    st.markdown(
        f"""
        <p style="margin: 0.75rem 0 0.25rem; color: #555; font-size: 0.95rem;">
            {file_count} PDF{"s" if file_count != 1 else ""} selected
        </p>
        """,
        unsafe_allow_html=True,
    )


process = st.button(
    "Process invoices",
    use_container_width=True,
    disabled=not uploaded,
)

if process:
    with st.spinner("Extracting fields…"):
        records, xlsx = process_files(uploaded)
        st.session_state.df = pd.DataFrame(records)
        st.session_state.xlsx = xlsx

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.df is not None:
    df = st.session_state.df

    ok = int((df["status"] == "OK").sum())
    review = int((df["status"] == "NEEDS REVIEW").sum())
    failed = int((df["status"] == "FAILED").sum())

    review_text = "needs manual review" if review == 1 else "need manual review"

    st.markdown(
        f"""
<p style="margin: 0.5rem 0 1rem; color: #555; font-size: 0.95rem;">
    Processed <strong>{len(df)}</strong> invoices —
    <strong>{ok}</strong> complete,
    <strong>{review}</strong> {review_text},
    <strong>{failed}</strong> failed.
</p>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="metrics-row">
            <div class="metric-box">
                <div class="metric-num">{len(df)}</div>
                <div class="metric-lbl">Total</div>
            </div>
            <div class="metric-box">
                <div class="metric-num" style="color:#16a34a">{ok}</div>
                <div class="metric-lbl">OK</div>
            </div>
            <div class="metric-box">
                <div class="metric-num" style="color:#d97706">{review}</div>
                <div class="metric-lbl">Needs review</div>
            </div>
            <div class="metric-box">
                <div class="metric-num" style="color:#dc2626">{failed}</div>
                <div class="metric-lbl">Failed</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    status_order = {"NEEDS REVIEW": 0, "FAILED": 1, "OK": 2}

    df_display = df.copy()
    df_display["status_order"] = df_display["status"].map(status_order).fillna(99)
    df_display = df_display.sort_values(
        by=["status_order", "file"], ascending=[True, True]
    ).drop(columns=["status_order"])

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.download_button(
        label="↓  Download Excel summary",
        data=st.session_state.xlsx,
        file_name="invoice_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
