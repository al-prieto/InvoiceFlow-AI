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
from src.validate import validate_fields
from src.export import records_to_xlsx_bytes
from src.pipeline import (
    get_status,
    build_record,
    build_error_record,
)


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InvoiceFlow",
    page_icon="📄",
    layout="centered",
)

# Fields the user can correct manually. Order determines UI order.
EDITABLE_FIELDS = [
    ("invoice_number", "Invoice number"),
    ("date", "Date (YYYY-MM-DD)"),
    ("total_due", "Total due"),
    ("due_date", "Due date (YYYY-MM-DD)"),
    ("subtotal", "Subtotal"),
    ("sales_tax", "Sales tax"),
    ("shipping", "Shipping & handling"),
]


# ── CSS ───────────────────────────────────────────────────────────────────────
def inject_css() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');

            html, body, [class*="css"] {
                font-family: 'DM Sans', sans-serif;
            }
            .stApp { background: #f7f7f8; }
            .block-container {
                max-width: 720px;
                padding-top: 4rem;
                padding-bottom: 4rem;
            }
            #MainMenu, footer, header { visibility: hidden; }

            .app-header { text-align: center; margin-bottom: 2.5rem; }
            .app-title {
                font-size: 2.4rem; font-weight: 700; color: #111;
                letter-spacing: -0.03em; margin-bottom: 0.4rem;
            }
            .app-sub { font-size: 1rem; color: #777; }

            [data-testid="stFileUploaderDropzone"] {
                background: #fff; border: 2px dashed #d0d0d5;
                border-radius: 16px; padding: 2rem 1.5rem; transition: border-color 0.2s;
            }
            [data-testid="stFileUploaderDropzone"]:hover { border-color: #4c7ef3; }

            .stButton > button {
                width: 100%; height: 3.5rem; border-radius: 12px; border: none;
                background: #4c7ef3; color: white;
                font-family: 'DM Sans', sans-serif; font-weight: 700; font-size: 1rem;
                margin-top: 1rem; margin-bottom: 1rem; transition: background 0.15s;
            }
            .stButton > button p {
                font-size: 1.25rem !important; margin: 0 !important;
                line-height: 1 !important; color: white !important;
            }
            .stButton > button:hover { background: #3a6ae0; color: white; }

            .metrics-row { display: flex; gap: 1rem; margin: 2rem 0 1rem; }
            .metric-box {
                flex: 1; background: #fff; border: 1px solid #e8e8ec;
                border-radius: 14px; padding: 1rem; text-align: center;
            }
            .metric-num { font-size: 2rem; font-weight: 700; color: #111; line-height: 1; }
            .metric-lbl { font-size: 0.8rem; color: #888; margin-top: 0.3rem; }

            .stDownloadButton > button {
                width: 100%; height: 3rem; border-radius: 12px;
                border: 1.5px solid #d0d0d5; background: #fff; color: #111;
                font-family: 'DM Sans', sans-serif; font-weight: 600; font-size: 0.95rem;
            }
            .stDownloadButton > button:hover {
                border-color: #4c7ef3; color: #4c7ef3; background: #fff;
            }

            [data-testid="stAlert"] { border-radius: 12px; }
            [data-testid="stAlertContentWarning"] p { color: #111; font-weight: 500; }

            [data-testid="stFileUploader"] div,
            [data-testid="stFileUploader"] span,
            [data-testid="stFileUploader"] small { color: #111111 !important; }

            [data-testid="stFileUploaderDropzone"] button {
                background-color: #111111 !important; color: #ffffff !important;
                border: none !important; border-radius: 8px !important;
                font-weight: 600 !important; transition: all 0.2s ease !important;
            }
            [data-testid="stFileUploaderDropzone"] button:hover {
                background-color: #4c7ef3 !important; color: #ffffff !important;
            }
            [data-testid="stUploadedFile"] svg { fill: #111111 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Processing ────────────────────────────────────────────────────────────────
def process_files(uploaded_files) -> list[dict]:
    """
    Extract fields from uploaded PDFs and return a list of record dicts.
    Errors are captured per-file and stored in the record so processing
    continues for the remaining files.
    """
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
            except Exception as e:
                record = build_error_record(f.name, e)
                st.warning(f"⚠ Could not process **{f.name}**: {e}")
            records.append(record)
    return records


# ── Session state init ────────────────────────────────────────────────────────
if "records" not in st.session_state:
    st.session_state.records = []


# ── UI ────────────────────────────────────────────────────────────────────────
inject_css()

st.markdown(
    """
    <div class="app-header">
        <div class="app-title">InvoiceFlow</div>
        <div class="app-sub">Upload invoice PDFs · Extract key fields · Review & export</div>
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
    st.markdown(
        f'<p style="margin: 0.75rem 0 0.25rem; color: #555; font-size: 0.95rem;">'
        f'{len(uploaded)} PDF{"s" if len(uploaded) != 1 else ""} selected</p>',
        unsafe_allow_html=True,
    )

if st.button("Process invoices", use_container_width=True, disabled=not uploaded):
    with st.spinner("Extracting fields…"):
        st.session_state.records = process_files(uploaded)


# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.records:
    records = st.session_state.records
    df = pd.DataFrame(records)

    ok = int((df["status"] == "OK").sum())
    reviewed = int((df["status"] == "REVIEWED").sum())
    needs_review = int((df["status"] == "NEEDS REVIEW").sum())
    failed = int((df["status"] == "FAILED").sum())
    total = len(df)

    st.markdown(
        f"""
        <div class="metrics-row">
            <div class="metric-box">
                <div class="metric-num">{total}</div>
                <div class="metric-lbl">Total</div>
            </div>
            <div class="metric-box">
                <div class="metric-num" style="color:#16a34a">{ok + reviewed}</div>
                <div class="metric-lbl">Ready</div>
            </div>
            <div class="metric-box">
                <div class="metric-num" style="color:#d97706">{needs_review}</div>
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

    status_order = {"NEEDS REVIEW": 0, "FAILED": 1, "OK": 2, "REVIEWED": 3}
    df_display = df.copy()
    df_display["_order"] = df_display["status"].map(status_order).fillna(99)
    df_display = df_display.sort_values(["_order", "file"]).drop(columns=["_order"])
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ── Manual review section ─────────────────────────────────────────────────
    reviewable_idx = [
        i for i, r in enumerate(records) if r["status"] in ("NEEDS REVIEW", "FAILED")
    ]

    if reviewable_idx:
        st.markdown("---")
        st.markdown("### ✏️ Manual review")
        st.caption(
            "Correct missing fields for invoices flagged for review. "
            "Corrections are kept in memory — export before closing this tab."
        )

        reviewable_files = [records[i]["file"] for i in reviewable_idx]
        selected_file = st.selectbox("Select invoice to correct", reviewable_files)
        selected_idx = next(
            i for i in reviewable_idx if records[i]["file"] == selected_file
        )
        record = records[selected_idx]

        # Show any validation issues for context
        fields_snapshot = {
            "invoice_number": record.get("invoice_number"),
            "date": record.get("date"),
            "total_due": record.get("total_due"),
            "subtotal": record.get("subtotal"),
            "sales_tax": record.get("sales_tax"),
            "shipping_handling": record.get("shipping"),
        }
        validation = validate_fields(fields_snapshot)
        if validation["issues"]:
            for issue in validation["issues"]:
                st.warning(f"⚠ {issue}")

        with st.form(key=f"review_{selected_idx}"):
            corrected = {}
            col1, col2 = st.columns(2)
            for i, (field_key, field_label) in enumerate(EDITABLE_FIELDS):
                col = col1 if i % 2 == 0 else col2
                corrected[field_key] = col.text_input(
                    field_label,
                    value=record.get(field_key) or "",
                )
            notes = st.text_input("Notes", value=record.get("notes") or "")
            submitted = st.form_submit_button(
                "💾 Save corrections", use_container_width=True
            )

        if submitted:
            # Apply corrections — blank strings become None so status recalculates cleanly
            for field_key, _ in EDITABLE_FIELDS:
                val = corrected[field_key].strip()
                st.session_state.records[selected_idx][field_key] = val if val else None

            st.session_state.records[selected_idx]["notes"] = notes.strip()

            # Recalculate status from corrected fields
            updated = st.session_state.records[selected_idx]
            new_status = get_status(
                {
                    "invoice_number": updated.get("invoice_number"),
                    "date": updated.get("date"),
                    "total_due": updated.get("total_due"),
                }
            )
            # Mark as REVIEWED even if OK so it's auditable
            st.session_state.records[selected_idx]["status"] = (
                "REVIEWED" if new_status == "OK" else new_status
            )
            # Clear missing_core so the table reflects the corrected state
            st.session_state.records[selected_idx]["missing_core"] = (
                "" if new_status == "OK" else updated.get("missing_core", "")
            )
            st.success(
                f"✓ {selected_file} saved as {st.session_state.records[selected_idx]['status']}"
            )
            st.rerun()

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("---")
    xlsx_bytes = records_to_xlsx_bytes(st.session_state.records)
    st.download_button(
        label="↓  Download Excel summary",
        data=xlsx_bytes,
        file_name="invoice_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
