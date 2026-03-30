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
from src.ui_styles import inject_css
from src.pipeline import (
    get_status,
    build_record,
    build_error_record,
    recalculate_after_correction,
)


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InvoiceFlow",
    page_icon="📄",
    layout="centered",
)

# Fields exposed in the manual-review form.
# Keys must match the record schema in pipeline.py exactly.
EDITABLE_FIELDS = [
    ("invoice_number", "Invoice number"),
    ("date", "Date (YYYY-MM-DD)"),
    ("total_due", "Total due"),
    ("due_date", "Due date (YYYY-MM-DD)"),
    ("subtotal", "Subtotal"),
    ("sales_tax", "Sales tax"),
    ("shipping_handling", "Shipping & handling"),
]


# ── Processing ────────────────────────────────────────────────────────────────
def process_files(uploaded_files) -> list[dict]:
    """
    Write uploaded PDFs to a temp dir, extract fields, return record list.
    Errors are captured per-file so processing continues for the rest.
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


# ── Session state ─────────────────────────────────────────────────────────────
if "records" not in st.session_state:
    st.session_state.records = []


# ── UI ────────────────────────────────────────────────────────────────────────
inject_css()

st.markdown(
    """
    <div class="app-header">
        <div class="app-title">InvoiceFlow</div>
        <div class="app-sub">Upload invoice PDFs · Extract key fields · Review &amp; export</div>
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
    n = len(uploaded)
    st.markdown(
        f'<p style="margin:0.75rem 0 0.25rem;color:#555;font-size:0.95rem;">'
        f'{n} PDF{"s" if n != 1 else ""} selected</p>',
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
    needs = int((df["status"] == "NEEDS REVIEW").sum())
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
                <div class="metric-num" style="color:#d97706">{needs}</div>
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

    # ── Manual review ─────────────────────────────────────────────────────────
    reviewable = [
        i for i, r in enumerate(records) if r["status"] in ("NEEDS REVIEW", "FAILED")
    ]

    if reviewable:
        st.markdown("---")
        st.markdown("### ✏️ Manual review")
        st.caption(
            "Correct missing or wrong fields for flagged invoices. "
            "Changes live in memory — export before closing this tab."
        )

        selected_file = st.selectbox(
            "Select invoice to correct",
            [records[i]["file"] for i in reviewable],
        )
        idx = next(i for i in reviewable if records[i]["file"] == selected_file)
        record = records[idx]

        # validate_fields keys match record keys directly
        validation = validate_fields(record)
        for issue in validation["issues"]:
            st.warning(f"⚠ {issue}")

        with st.form(key=f"review_{idx}"):
            corrected: dict[str, str] = {}
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
            for field_key, _ in EDITABLE_FIELDS:
                val = corrected[field_key].strip()
                st.session_state.records[idx][field_key] = val or None
            st.session_state.records[idx]["notes"] = notes.strip()

            recalculate_after_correction(st.session_state.records[idx])
            final_status = st.session_state.records[idx]["status"]
            st.success(f"✓ {selected_file} saved as {final_status}")
            st.rerun()

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.download_button(
        label="↓  Download Excel summary",
        data=records_to_xlsx_bytes(st.session_state.records),
        file_name="invoice_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
