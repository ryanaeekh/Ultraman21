"""Shared CSS + HTML helper module for the Ultraman21 Streamlit app redesign."""

import streamlit as st

# ── Design Token Constants ──────────────────────────────────────────
ACCENT = "#00d4ff"
POS = "#00e68a"
NEG = "#ff4d6a"
BG = "#0d0d0d"
BG2 = "#111111"
CARD_BG = "rgba(255,255,255,0.04)"
TEXT = "#f0f0f0"
TEXT2 = "rgba(255,255,255,0.55)"
BORDER = "rgba(255,255,255,0.06)"

# ── CSS Strings ─────────────────────────────────────────────────────
_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap');

:root {
    --bg:          #0d0d0d;
    --bg2:         #111111;
    --card-bg:     rgba(255,255,255,0.04);
    --card-hover:  rgba(255,255,255,0.07);
    --accent:      #00d4ff;
    --accent-glow: 0 0 20px rgba(0,212,255,0.15);
    --pos:         #00e68a;
    --neg:         #ff4d6a;
    --text:        #f0f0f0;
    --text2:       rgba(255,255,255,0.55);
    --border:      rgba(255,255,255,0.06);
    --radius-lg:   16px;
    --radius-md:   10px;
    --font-display:'Syne', sans-serif;
    --font-body:   'DM Sans', sans-serif;
}

html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}
.block-container {
    max-width: 1200px !important;
    padding: 2rem 2rem 4rem !important;
}

h1, h2, h3, .page-title, .section-title {
    font-family: var(--font-display) !important;
    color: var(--text) !important;
}
.page-title {
    font-size: 28px; font-weight: 700;
    letter-spacing: -0.02em; margin-bottom: 4px;
}
.page-subtitle {
    font-size: 13px; color: var(--text2);
    margin-bottom: 8px;
}
.section-title {
    font-size: 18px; font-weight: 600;
    margin-bottom: 16px; letter-spacing: -0.01em;
}
.divider {
    height: 1px; background: var(--border);
    margin: 16px 0 24px;
}

.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    padding: 24px;
    margin-bottom: 16px;
    transition: all 0.3s ease;
}
.card:hover {
    background: var(--card-hover);
    border-color: rgba(0,212,255,0.2);
    box-shadow: var(--accent-glow);
}

.metric-card { text-align: center; }
.metric-label {
    font-size: 11px; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--text2); margin-bottom: 8px;
}
.metric-value {
    font-family: var(--font-body);
    font-size: 36px; font-weight: 700;
    line-height: 1.1; margin-bottom: 6px;
    color: var(--text);
}
.metric-sub { font-size: 13px; color: var(--text2); }

.detail-row {
    display: flex; justify-content: space-between;
    align-items: center; padding: 10px 0;
    border-bottom: 1px solid var(--border);
}
.detail-row:last-child { border-bottom: none; }
.detail-key { font-size: 14px; color: var(--text2); }
.detail-val { font-size: 14px; font-weight: 600; color: var(--text); }
.detail-val.positive { color: var(--pos); }
.detail-val.negative { color: var(--neg); }

.progress-track {
    width: 100%; height: 4px;
    background: rgba(255,255,255,0.08);
    border-radius: 2px; overflow: hidden; margin: 8px 0;
}
.progress-fill {
    height: 100%; border-radius: 2px;
    transition: width 0.5s ease;
    box-shadow: 0 0 8px rgba(0,212,255,0.3);
}

.badge {
    display: inline-block;
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.06em;
    padding: 4px 12px; border-radius: 20px;
}

div.stButton > button {
    font-family: var(--font-body) !important;
    background: transparent !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    border-radius: var(--radius-md) !important;
    padding: 8px 24px !important;
    font-weight: 600 !important;
    transition: all 0.25s ease !important;
}
div.stButton > button:hover {
    background: var(--accent) !important;
    color: #0d0d0d !important;
    box-shadow: var(--accent-glow) !important;
}

div[data-testid="stForm"] {
    background: transparent !important;
    border: none !important; padding: 0 !important;
}
input, textarea, select,
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] > div > div {
    font-family: var(--font-body) !important;
    background: transparent !important;
    color: var(--text) !important;
    border: none !important;
    border-bottom: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 0 !important;
    padding: 8px 0 !important;
    transition: border-color 0.25s ease !important;
}
input:focus, textarea:focus {
    border-bottom-color: var(--accent) !important;
    box-shadow: none !important;
}
label, .stSelectbox label, .stTextInput label, .stNumberInput label, .stTextArea label {
    font-family: var(--font-body) !important;
    font-size: 11px !important; font-weight: 500 !important;
    text-transform: uppercase !important; letter-spacing: 0.08em !important;
    color: var(--text2) !important;
}

div[data-testid="stSelectbox"] > div > div {
    border-bottom: 1px solid rgba(255,255,255,0.15) !important;
}
[data-baseweb="popover"] {
    background: #1a1a1a !important;
    border: 1px solid var(--border) !important;
}
[data-baseweb="popover"] li {
    color: var(--text) !important; background: transparent !important;
}
[data-baseweb="popover"] li:hover {
    background: rgba(0,212,255,0.1) !important;
}

.stDataFrame, div[data-testid="stDataFrame"] {
    border-radius: var(--radius-md) !important; overflow: hidden;
}
div[data-testid="stDataFrame"] table { background: transparent !important; }
div[data-testid="stDataFrame"] th {
    font-size: 11px !important; text-transform: uppercase;
    letter-spacing: 0.06em; color: var(--text2) !important;
    background: rgba(255,255,255,0.03) !important;
    border-bottom: 1px solid var(--border) !important;
}
div[data-testid="stDataFrame"] td {
    color: var(--text) !important;
    border-bottom: 1px solid var(--border) !important;
    background: transparent !important;
}
div[data-testid="stDataFrame"] tr:hover td {
    background: rgba(255,255,255,0.03) !important;
}

.stPlotlyChart, div[data-testid="stVegaLiteChart"] {
    background: transparent !important;
}

button[data-baseweb="tab"] {
    font-family: var(--font-body) !important;
    color: var(--text2) !important; background: transparent !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

header[data-testid="stHeader"] { background: var(--bg) !important; }
div[data-testid="stToolbar"] { display: none !important; }
.stAlert { border-radius: var(--radius-md) !important; }
div[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    background: var(--card-bg) !important;
}
div[data-testid="stExpander"] summary {
    font-family: var(--font-display) !important;
    color: var(--text) !important;
}

.exec-pills { display: flex; gap: 10px; margin: 12px 0; }
.exec-pill {
    font-size: 12px; font-weight: 600;
    padding: 6px 16px; border-radius: 20px;
    text-transform: uppercase; letter-spacing: 0.04em;
}
.exec-pill.done {
    color: var(--pos); background: rgba(0,230,138,0.12);
    box-shadow: 0 0 10px rgba(0,230,138,0.15);
}
.exec-pill.pending {
    color: var(--text2); background: rgba(255,255,255,0.05);
}

.score-ring {
    width: 140px; height: 140px;
    border-radius: 50%; margin: 0 auto 12px;
    display: flex; align-items: center; justify-content: center;
    background: conic-gradient(
        var(--accent) calc(var(--pct) * 3.6deg),
        rgba(255,255,255,0.06) 0deg
    );
    position: relative;
}
.score-ring::after {
    content: ''; position: absolute;
    width: 120px; height: 120px; border-radius: 50%;
    background: var(--bg);
}
.score-ring-value {
    position: relative; z-index: 1;
    font-family: var(--font-body);
    font-size: 42px; font-weight: 700;
    color: var(--text);
}

.accent-left-card { border-left: 3px solid var(--accent) !important; }

.c-pos { color: var(--pos) !important; }
.c-neg { color: var(--neg) !important; }
.c-accent { color: var(--accent) !important; }
.c-muted { color: var(--text2) !important; }

section[data-testid="stSidebar"] {
    background: #0a0a0a !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-family: var(--font-body) !important;
    color: var(--text2) !important; transition: color 0.2s ease;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: var(--text) !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: var(--text2) !important;
}

div[data-testid="stChatMessage"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text) !important;
}
div[data-testid="stChatInput"] { border-color: var(--border) !important; }
div[data-testid="stChatInput"] textarea {
    color: var(--text) !important; background: transparent !important;
}

.hist-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    backdrop-filter: blur(16px);
    padding: 20px 24px; margin-bottom: 12px;
    transition: all 0.3s ease;
}
.hist-card:hover {
    background: var(--card-hover);
    border-color: rgba(0,212,255,0.15);
}

.j-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    backdrop-filter: blur(16px);
    padding: 24px; margin-bottom: 12px;
}
.j-date {
    font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--text2); margin-bottom: 8px;
}
.j-text {
    font-size: 15px; line-height: 1.8;
    color: var(--text); white-space: pre-wrap;
}

.news-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    backdrop-filter: blur(16px);
    padding: 20px; margin-bottom: 10px;
    transition: all 0.3s ease;
}
.news-card:hover {
    background: var(--card-hover);
    border-color: rgba(0,212,255,0.15);
    transform: translateY(-2px);
}
.news-source {
    font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.06em; color: var(--accent); margin-bottom: 6px;
}
.news-title a {
    font-family: var(--font-display);
    font-size: 16px; font-weight: 600;
    color: var(--text) !important; text-decoration: none;
}
.news-title a:hover { color: var(--accent) !important; }
.news-desc {
    font-size: 13px; color: var(--text2);
    margin: 8px 0; line-height: 1.5;
}
.news-meta { font-size: 11px; color: var(--text2); opacity: 0.6; }

.section-label {
    font-family: var(--font-display);
    font-size: 18px; font-weight: 600;
    color: var(--text); padding-bottom: 8px;
    border-bottom: 2px solid var(--accent);
    margin: 24px 0 16px; display: inline-block;
}

.day-table { width: 100%; border-collapse: collapse; margin-top: 16px; }
.day-table th {
    font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.06em; color: var(--text2);
    padding: 10px 12px; text-align: left;
    border-bottom: 1px solid var(--border);
}
.day-table td {
    padding: 10px 12px; font-size: 14px;
    border-bottom: 1px solid var(--border); color: var(--text);
}
.day-table tr:hover td { background: rgba(255,255,255,0.03); }

.record-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 12px 16px; margin-bottom: 8px;
    transition: background 0.2s ease;
}
.record-card:hover { background: rgba(255,255,255,0.04); }

.summary-row { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 20px; }
.summary-card {
    flex: 1; min-width: 140px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    backdrop-filter: blur(16px);
    padding: 18px; text-align: center;
    transition: all 0.3s ease;
}
.summary-card:hover {
    background: var(--card-hover);
    border-color: rgba(0,212,255,0.2);
}
.summary-label {
    font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--text2); margin-bottom: 6px;
}
.summary-value { font-size: 28px; font-weight: 700; font-family: var(--font-body); }

.insight-box, .focus-box {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 14px; margin-bottom: 10px;
}
.insight-box:hover, .focus-box:hover { background: rgba(255,255,255,0.04); }

.streak-pill {
    display: inline-block; font-size: 12px; font-weight: 600;
    padding: 4px 14px; border-radius: 20px;
    color: var(--accent); background: rgba(0,212,255,0.1); margin-left: 8px;
}

.hero-banner {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    backdrop-filter: blur(16px);
    padding: 28px; text-align: center; margin-bottom: 20px;
}
.hero-label {
    font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.1em; color: var(--text2); margin-bottom: 10px;
}
.hero-value {
    font-family: var(--font-display);
    font-size: 22px; font-weight: 700; color: var(--text);
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

.success-box {
    background: rgba(0,230,138,0.08);
    border-left: 3px solid var(--pos);
    border-radius: var(--radius-md);
    padding: 12px 16px; color: var(--pos); margin: 10px 0; font-size: 14px;
}
.warning-box {
    background: rgba(255,180,0,0.08);
    border-left: 3px solid #ffb400;
    border-radius: var(--radius-md);
    padding: 12px 16px; color: #ffb400; margin: 10px 0; font-size: 14px;
}
.error-box {
    background: rgba(255,77,106,0.08);
    border-left: 3px solid var(--neg);
    border-radius: var(--radius-md);
    padding: 12px 16px; color: var(--neg); margin: 10px 0; font-size: 14px;
}
</style>"""

_SIDEBAR_CSS = """<style>
section[data-testid="stSidebar"] {
    width: 70px !important;
    min-width: 70px !important;
    transition: width 0.3s ease, min-width 0.3s ease !important;
    overflow: hidden !important;
}
section[data-testid="stSidebar"]:hover {
    width: 240px !important;
    min-width: 240px !important;
}
section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem !important;
}
button[data-testid="stSidebarCollapse"] { display: none !important; }
</style>"""


# ── Injection Functions ─────────────────────────────────────────────
def inject_theme():
    """Inject the full theme CSS into the Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)


def inject_sidebar():
    """Inject sidebar icon-rail CSS into the Streamlit page."""
    st.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)


# ── HTML Helper Functions ───────────────────────────────────────────
def metric_card(label: str, value: str, sub: str = "", color: str = "") -> str:
    """Return HTML string for a trading-dashboard metric card."""
    color_style = f' style="color:{color}"' if color else ""
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="card metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value"{color_style}>{value}</div>'
        f'{sub_html}'
        f'</div>'
    )


def detail_row(key: str, value: str, cls: str = "") -> str:
    """Return HTML string for a key-value row."""
    cls_attr = f" {cls}" if cls else ""
    return (
        f'<div class="detail-row">'
        f'<span class="detail-key">{key}</span>'
        f'<span class="detail-val{cls_attr}">{value}</span>'
        f'</div>'
    )


def section_card(title: str, content: str) -> str:
    """Return HTML string for a glass card with section header."""
    return (
        f'<div class="card">'
        f'<div class="section-title">{title}</div>'
        f'{content}'
        f'</div>'
    )


def status_badge(text: str, color: str) -> str:
    """Return HTML string for a pill badge."""
    return (
        f'<span class="badge" style="color:{color};'
        f'background:{color}20">{text}</span>'
    )


def progress_bar(pct: float, color: str = "") -> str:
    """Return HTML string for a 4px progress bar (pct 0-100)."""
    pct = max(0, min(100, pct))
    bar_color = color if color else ACCENT
    return (
        f'<div class="progress-track">'
        f'<div class="progress-fill" style="width:{pct}%;'
        f'background:{bar_color}"></div>'
        f'</div>'
    )


def page_header(title: str, subtitle: str = "") -> str:
    """Return HTML string for page title + subtitle + divider."""
    sub_html = f'<div class="page-subtitle">{subtitle}</div>' if subtitle else ""
    return (
        f'<div class="page-title">{title}</div>'
        f'{sub_html}'
        f'<div class="divider"></div>'
    )
