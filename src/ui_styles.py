"""
UI styles for the InvoiceFlow Streamlit app.

Kept in a separate module so streamlit_app.py stays focused on logic and layout.
To update the design, edit only this file.
"""

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #111111 !important;
}

.stApp {
    background: #f7f7f8;
    color: #111111 !important;
}

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

/* Main button + form submit button */
.stButton > button,
.stFormSubmitButton > button {
    width: 100%;
    height: 3.5rem;
    border-radius: 12px;
    border: none !important;
    background: #4c7ef3 !important;
    color: #ffffff !important;
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    font-size: 1.08rem;
    margin-top: 1rem;
    margin-bottom: 1rem;
    box-shadow: none !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #3a6ae0 !important;
    color: #ffffff !important;
    border: none !important;
}

.stButton > button p,
.stFormSubmitButton > button p,
.stButton > button span,
.stFormSubmitButton > button span {
    color: #ffffff !important;
    font-size: 1.08rem !important;
    line-height: 1 !important;
    margin: 0 !important;
}

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


/* Inputs / textarea / date / select - target Streamlit/BaseWeb wrappers */
div[data-baseweb="base-input"],
div[data-baseweb="input"],
div[data-baseweb="textarea"],
div[data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1px solid #d7d9df !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    outline: none !important;
}

/* Remove inner borders/shadows that BaseWeb adds */
div[data-baseweb="base-input"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}

/* Actual text fields */
div[data-baseweb="base-input"] input,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-testid="stTextArea"] textarea {
    background: transparent !important;
    color: #111111 !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}

/* Focus on wrapper */
div[data-baseweb="base-input"]:focus-within,
div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="select"] > div:focus-within {
    border: 1px solid #4c7ef3 !important;
    box-shadow: 0 0 0 1px #4c7ef3 !important;
    outline: none !important;
}

/* Labels */
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stDateInput"] label,
div[data-testid="stSelectbox"] label {
    color: #111111 !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}



div[data-baseweb="select"] input,
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
}

/* Selectbox icon */
div[data-baseweb="select"] svg {
    fill: #111111 !important;
}

/* General spacing for form blocks */
div[data-testid="stTextInput"],
div[data-testid="stTextArea"],
div[data-testid="stDateInput"],
div[data-testid="stSelectbox"] {
    margin-bottom: 0.75rem;
}
"""


def inject_css() -> None:
    """Inject app styles into the Streamlit page. Call once at app startup."""
    import streamlit as st

    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)
