import base64
import streamlit as st

def get_base64_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ── Shared CSS injected on every page ─────────────────────────────────────────
_SHARED_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700&family=Exo+2:wght@300;400;500&display=swap');

/* Hide sidebar everywhere */
[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
    display: none !important;
}

/* Global font */
html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif !important;
}

/* Headings use Orbitron */
h1, h2, h3, .stTitle {
    font-family: 'Orbitron', monospace !important;
    letter-spacing: 0.05em;
}

/* Metric labels */
[data-testid="stMetricLabel"] {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    opacity: 0.8;
}
"""

# ── Login page ─────────────────────────────────────────────────────────────────
def set_login_background(image_path: str):
    try:
        img_b64 = get_base64_image(image_path)
        st.markdown(f"""
            <style>
            {_SHARED_CSS}

            .stApp {{
                background-image: url("data:image/jpeg;base64,{img_b64}");
                background-size: cover;
                background-position: center;
                background-attachment: scroll;
                background-color: rgba(0, 0, 0, 0.55);
                background-blend-mode: darken;
            }}
            .stTabs [data-baseweb="tab-panel"],
            div[data-testid="stForm"] {{
                background: rgba(0, 0, 0, 0.45) !important;
                border-radius: 12px;
                padding: 1rem;
            }}
            </style>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Background image not found. Proceeding with default theme.")


# ── Main app pages (home, dashboard, predictions) ─────────────────────────────
def set_app_background(image_path: str = "assets/app_bg.jpg"):
    """Apply the wavy blue background + hide sidebar for logged-in pages."""
    try:
        img_b64 = get_base64_image(image_path)
        bg_css = f"""
            .stApp {{
                background-image: url("data:image/jpeg;base64,{img_b64}");
                background-size: cover;
                background-position: center;
                background-attachment: scroll;
                background-color: rgba(5, 0, 20, 0.72);
                background-blend-mode: darken;
            }}
        """
    except FileNotFoundError:
        bg_css = """
            .stApp {
                background: linear-gradient(135deg, #05001a 0%, #0d0040 50%, #1a0070 100%) !important;
            }
        """

    st.markdown(f"""
        <style>
        {_SHARED_CSS}
        {bg_css}

        /* Card-style containers */
        div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"],
        div[data-testid="metric-container"] {{
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(120,80,255,0.2);
            border-radius: 10px;
            padding: 0.5rem;
        }}

        /* Dataframe background */
        div[data-testid="stDataFrame"] {{
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
        }}

        /* Divider color */
        hr {{
            border-color: rgba(120,80,255,0.3) !important;
        }}
        </style>
    """, unsafe_allow_html=True)


# ── Legacy alias so existing code that calls clear_background() still works ───
def clear_background():
    set_app_background()