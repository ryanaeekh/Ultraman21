"""Shared CSS + HTML helper module for the Ultraman21 Streamlit app redesign."""

import streamlit as st

# ── Design Token Constants ──────────────────────────────────────────
ACCENT = "#4F7C82"
POS = "#4F7C82"
NEG = "#c97a8a"
BG = "#0B2E33"
BG2 = "#0e3a40"
CARD_BG = "#0e3a40"
TEXT = "#B8E3E9"
TEXT2 = "#7fbcc4"
BORDER = "#4F7C82"

# ── CSS Strings ─────────────────────────────────────────────────────
_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;500;700;900&family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
    --bg:          #0B2E33;
    --bg2:         #0e3a40;
    --card-bg:     #0e3a40;
    --card-hover:  #135058;
    --accent:      #4F7C82;
    --accent-soft: rgba(79,124,130,0.15);
    --accent-glow: 0 4px 20px rgba(79,124,130,0.25);
    --pos:         #4F7C82;
    --neg:         #c97a8a;
    --text:        #B8E3E9;
    --text2:       #7fbcc4;
    --text3:       #7fbcc4;
    --border:      #4F7C82;
    --border-strong: #B8E3E9;
    --shadow-sm:   0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.3);
    --shadow-md:   0 4px 12px rgba(0,0,0,0.3), 0 2px 4px rgba(0,0,0,0.3);
    --shadow-lg:   0 8px 30px rgba(0,0,0,0.3), 0 2px 8px rgba(0,0,0,0.3);
    --radius-lg:   14px;
    --radius-md:   8px;
    --font-display:'Zen Kaku Gothic New', sans-serif;
    --font-body:   'Outfit', sans-serif;
}

/* ─── Foundation ─────────────────────────────────── */
html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}
/* Warm textured background — workshop bench grain */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: -1;
    background:
        radial-gradient(ellipse at 20% 0%, rgba(79,124,130,0.12) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 100%, rgba(201,122,138,0.06) 0%, transparent 50%),
        var(--bg);
}

.block-container {
    max-width: 1200px !important;
    padding: 2rem 2rem 4rem !important;
}

/* ─── Typography ─────────────────────────────────── */
h1, h2, h3, .page-title, .section-title {
    font-family: var(--font-display) !important;
    color: var(--text) !important;
}
.page-title {
    font-size: 26px; font-weight: 900;
    letter-spacing: 0.01em; margin-bottom: 4px;
    color: var(--text) !important;
}
.page-subtitle {
    font-size: 13px; color: var(--text2);
    font-weight: 400; margin-bottom: 8px;
}
.section-title {
    font-size: 16px; font-weight: 700;
    margin-bottom: 14px; letter-spacing: 0.01em;
    color: var(--text) !important;
}
.divider {
    height: 2px;
    background: linear-gradient(90deg, var(--accent), transparent 60%);
    margin: 14px 0 24px; opacity: 0.3;
}

/* ─── Cards ──────────────────────────────────────── */
.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.3s ease, border-color 0.3s ease;
}
.card:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--border-strong);
}

/* ─── Metric Cards ───────────────────────────────── */
.metric-card { text-align: center; }
.metric-label {
    font-family: var(--font-display);
    font-size: 11px; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.1em;
    color: var(--text2); margin-bottom: 8px;
}
.metric-value {
    font-family: var(--font-body);
    font-size: 34px; font-weight: 700;
    line-height: 1.1; margin-bottom: 6px;
    color: var(--text);
}
.metric-sub { font-size: 13px; color: var(--text2); font-weight: 400; }

/* ─── Detail Rows ────────────────────────────────── */
.detail-row {
    display: flex; justify-content: space-between;
    align-items: center; padding: 10px 0;
    border-bottom: 1px solid var(--border);
}
.detail-row:last-child { border-bottom: none; }
.detail-key { font-size: 14px; color: var(--text2); font-weight: 400; }
.detail-val { font-size: 14px; font-weight: 600; color: var(--text); }
.detail-val.positive { color: var(--pos); }
.detail-val.negative { color: var(--neg); }

/* ─── Progress Bar ───────────────────────────────── */
.progress-track {
    width: 100%; height: 4px;
    background: var(--bg2);
    border-radius: 2px; overflow: hidden; margin: 8px 0;
}
.progress-fill {
    height: 100%; border-radius: 2px;
    transition: width 0.5s ease;
}

/* ─── Badge ──────────────────────────────────────── */
.badge {
    display: inline-block;
    font-family: var(--font-display);
    font-size: 11px; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.06em;
    padding: 4px 12px; border-radius: 20px;
}

/* ─── Buttons ────────────────────────────────────── */
div.stButton > button {
    font-family: var(--font-body) !important;
    background: #4F7C82 !important;
    color: #B8E3E9 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 6px 12px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    letter-spacing: 0.02em !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25) !important;
    cursor: pointer !important;
}
div.stButton > button:hover {
    background: #c97a8a !important;
    color: #0B2E33 !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important;
    transform: translateY(-1px);
}
div.stButton > button:active {
    transform: translateY(0);
    box-shadow: 0 1px 4px rgba(0,0,0,0.25) !important;
}

/* ─── Forms & Inputs ─────────────────────────────── */
div[data-testid="stForm"] {
    background: transparent !important;
    border: none !important; padding: 0 !important;
}
textarea, select,
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea {
    font-family: var(--font-body) !important;
    background: var(--bg2) !important;
    color: var(--text) !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: var(--radius-md) var(--radius-md) 0 0 !important;
    padding: 10px 12px !important;
    transition: border-color 0.25s ease, background 0.25s ease !important;
    caret-color: var(--accent) !important;
}
div[data-testid="stSelectbox"] > div > div {
    font-family: var(--font-body) !important;
    color: var(--text) !important;
}
input:focus, textarea:focus {
    border-bottom-color: var(--accent) !important;
    background: #135058 !important;
    box-shadow: none !important;
    outline: none !important;
}
input::placeholder, textarea::placeholder {
    color: var(--text3) !important;
}
div[data-testid="stTextInput"] > div,
div[data-testid="stNumberInput"] > div,
div[data-testid="stTextArea"] > div,
div[data-testid="stDateInput"] > div {
    background: transparent !important;
}
div[data-testid="stTextInput"] > div > div,
div[data-testid="stNumberInput"] > div > div,
div[data-testid="stTextArea"] > div > div {
    background: transparent !important;
}
label, .stSelectbox label, .stTextInput label, .stNumberInput label, .stTextArea label {
    font-family: var(--font-display) !important;
    font-size: 11px !important; font-weight: 500 !important;
    text-transform: uppercase !important; letter-spacing: 0.1em !important;
    color: var(--text2) !important;
}

div[data-testid="stSelectbox"] > div > div {
    border-bottom: 2px solid transparent !important;
}
/* Ensure selectbox selected value text is visible */
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: var(--bg2) !important;
    color: var(--text) !important;
}
div[data-testid="stSelectbox"] [data-baseweb="select"] > div > div {
    background: transparent !important;
    color: var(--text) !important;
}
div[data-testid="stSelectbox"] [data-baseweb="select"] span {
    color: var(--text) !important;
}
div[data-testid="stSelectbox"] [data-baseweb="select"] input {
    background: transparent !important;
    color: var(--text) !important;
    caret-color: var(--accent) !important;
}

/* ─── Checkbox / Caption / Markdown ──────────────── */
div[data-testid="stCheckbox"] label span,
div[data-testid="stCheckbox"] label p,
.stCheckbox label span {
    color: var(--text) !important;
}
div[data-testid="stCaptionContainer"],
div[data-testid="stCaptionContainer"] p,
.stCaption, .stCaption p {
    color: var(--text2) !important;
}
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] span,
div[data-testid="stMarkdownContainer"] li {
    color: var(--text) !important;
}

/* ─── Form Submit ────────────────────────────────── */
div[data-testid="stFormSubmitButton"] button {
    font-family: var(--font-body) !important;
    background: #4F7C82 !important;
    color: #B8E3E9 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 6px 12px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25) !important;
    transition: all 0.25s ease !important;
    cursor: pointer !important;
}
div[data-testid="stFormSubmitButton"] button:hover {
    background: #B4D6E3 !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important;
    transform: translateY(-1px);
}
div[data-testid="stFormSubmitButton"] button:active {
    transform: translateY(0);
    box-shadow: 0 1px 4px rgba(0,0,0,0.25) !important;
}

/* ─── Popover / Dropdown ─────────────────────────── */
[data-baseweb="popover"] {
    background: #0e3a40 !important;
    border: 1px solid var(--border-strong) !important;
    box-shadow: var(--shadow-lg) !important;
    border-radius: var(--radius-md) !important;
}
[data-baseweb="popover"] li {
    color: var(--text) !important; background: transparent !important;
    font-family: var(--font-body) !important;
}
[data-baseweb="popover"] li:hover {
    background: var(--accent-soft) !important;
}

/* ─── DataFrames ─────────────────────────────────── */
.stDataFrame, div[data-testid="stDataFrame"] {
    border-radius: var(--radius-md) !important; overflow: hidden;
}
div[data-testid="stDataFrame"] table { background: transparent !important; }
div[data-testid="stDataFrame"] th {
    font-family: var(--font-display) !important;
    font-size: 11px !important; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--text2) !important;
    background: var(--bg2) !important;
    border-bottom: 1px solid var(--border-strong) !important;
}
div[data-testid="stDataFrame"] td {
    color: var(--text) !important;
    border-bottom: 1px solid var(--border) !important;
    background: transparent !important;
}
div[data-testid="stDataFrame"] tr:hover td {
    background: var(--accent-soft) !important;
}

/* ─── Charts ─────────────────────────────────────── */
.stPlotlyChart, div[data-testid="stVegaLiteChart"] {
    background: transparent !important;
}

/* ─── Tabs ───────────────────────────────────────── */
button[data-baseweb="tab"] {
    font-family: var(--font-display) !important;
    color: var(--text2) !important; background: transparent !important;
    font-weight: 500 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* ─── Header & Navigation ────────────────────────── */
header[data-testid="stHeader"] {
    background: var(--bg) !important;
    border-bottom: 1px solid var(--border) !important;
}
/* Hide sidebar, its toggle, and ALL native page navigation */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] *,
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavSeparator"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavLink"],
[data-testid="stSidebarNavLinkContainer"],
[data-testid="stSidebarNavViewButton"],
[data-testid="stSidebarContent"],
[data-testid="stSidebarHeader"],
[data-testid="stSidebarCollapsed"],
[data-testid="stNavigation"],
[data-testid="stPageNavigation"],
[data-testid="stNavSectionHeader"],
[data-testid="stPageLink"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    position: absolute !important;
    left: -9999px !important;
}

/* Hide ALL header children EXCEPT the toolbar (Deploy + 3-dot menu) */
header[data-testid="stHeader"] > *:not([data-testid="stToolbar"]):not([data-testid="stHeaderActionElements"]) {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
    position: absolute !important;
    left: -9999px !important;
}

/* ─── Nav Selectbox ─────────────────────────────── */
.st-key-nav_menu_container {
    position: fixed !important;
    top: 72px;
    right: 32px;
    z-index: 999990;
    width: 155px !important;
    margin: 0 !important;
    padding: 0 !important;
}
.st-key-nav_menu_container > div {
    margin: 0 !important;
    padding: 0 !important;
    min-height: 0 !important;
}
.st-key-nav_menu_container > div > div {
    margin: 0 !important;
    padding: 0 !important;
    min-height: 0 !important;
}
.st-key-nav_menu_container .stSelectbox label {
    display: none !important;
}
.st-key-nav_menu_container .stSelectbox [data-baseweb="select"] > div {
    background: var(--card-bg) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 10px !important;
    cursor: pointer !important;
    box-shadow: var(--shadow-sm) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    padding: 6px 12px !important;
    min-height: 0 !important;
    height: auto !important;
}
.st-key-nav_menu_container .stSelectbox [data-baseweb="select"] > div:hover {
    border-color: var(--accent) !important;
    box-shadow: 0 4px 20px rgba(79,124,130,0.3) !important;
}
.st-key-nav_menu_container .stSelectbox [data-baseweb="select"] > div > div,
.st-key-nav_menu_container .stSelectbox [data-baseweb="select"] span {
    font-family: var(--font-body) !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    color: var(--text) !important;
    padding: 0 !important;
    background: var(--card-bg) !important;
}
.st-key-nav_menu_container .stSelectbox > div,
.st-key-nav_menu_container .stSelectbox > div > div,
.st-key-nav_menu_container .stSelectbox > div > div > div,
.st-key-nav_menu_container .stSelectbox [data-baseweb="select"] {
    background-color: var(--card-bg) !important;
}
.st-key-nav_menu_container .stSelectbox [data-baseweb="select"] svg {
    fill: var(--text2) !important;
}

/* ─── Alerts & Expanders ─────────────────────────── */
.stAlert { border-radius: var(--radius-md) !important; }
div[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    background: var(--card-bg) !important;
    box-shadow: var(--shadow-sm) !important;
}
div[data-testid="stExpander"] summary {
    font-family: var(--font-display) !important;
    color: var(--text) !important;
}

/* ─── Execution Pills ────────────────────────────── */
.exec-pills { display: flex; gap: 10px; margin: 12px 0; }
.exec-pill {
    font-family: var(--font-display);
    font-size: 12px; font-weight: 500;
    padding: 6px 16px; border-radius: 20px;
    text-transform: uppercase; letter-spacing: 0.04em;
}
.exec-pill.done {
    color: var(--pos); background: rgba(79,124,130,0.2);
}
.exec-pill.pending {
    color: var(--text3); background: var(--bg2);
}

/* ─── Score Ring ─────────────────────────────────── */
.score-ring {
    width: 140px; height: 140px;
    border-radius: 50%; margin: 0 auto 12px;
    display: flex; align-items: center; justify-content: center;
    background: conic-gradient(
        var(--accent) calc(var(--pct) * 3.6deg),
        var(--bg2) 0deg
    );
    position: relative;
    box-shadow: var(--shadow-md);
}
.score-ring::after {
    content: ''; position: absolute;
    width: 120px; height: 120px; border-radius: 50%;
    background: var(--card-bg);
}
.score-ring-value {
    position: relative; z-index: 1;
    font-family: var(--font-body);
    font-size: 42px; font-weight: 700;
    color: var(--text);
}

/* ─── Utility Classes ────────────────────────────── */
.accent-left-card { border-left: 3px solid var(--accent) !important; }

.c-pos { color: var(--pos) !important; }
.c-neg { color: var(--neg) !important; }
.c-accent { color: var(--accent) !important; }
.c-muted { color: var(--text2) !important; }

/* ─── Chat ───────────────────────────────────────── */
div[data-testid="stChatMessage"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text) !important;
    box-shadow: var(--shadow-sm) !important;
}
div[data-testid="stChatInput"] { border-color: var(--border-strong) !important; }
div[data-testid="stChatInput"] textarea {
    color: var(--text) !important; background: transparent !important;
}

/* ─── History Cards ──────────────────────────────── */
.hist-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px 24px; margin-bottom: 12px;
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease;
}
.hist-card:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--border-strong);
}

/* ─── Journal Cards ──────────────────────────────── */
.j-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 24px; margin-bottom: 12px;
    box-shadow: var(--shadow-sm);
}
.j-date {
    font-family: var(--font-display);
    font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.1em; color: var(--text2); margin-bottom: 8px;
}
.j-text {
    font-size: 15px; line-height: 1.8;
    color: var(--text); white-space: pre-wrap;
}

/* ─── News Cards ─────────────────────────────────── */
.news-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px; margin-bottom: 10px;
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease;
}
.news-card:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--border-strong);
    transform: translateY(-2px);
}
.news-source {
    font-family: var(--font-display);
    font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--accent); margin-bottom: 6px;
}
.news-title a {
    font-family: var(--font-display);
    font-size: 16px; font-weight: 700;
    color: var(--text) !important; text-decoration: none;
}
.news-title a:hover { color: var(--accent) !important; }
.news-desc {
    font-size: 13px; color: var(--text2);
    margin: 8px 0; line-height: 1.5;
}
.news-meta { font-size: 11px; color: var(--text3); }

/* ─── Section Label ──────────────────────────────── */
.section-label {
    font-family: var(--font-display);
    font-size: 16px; font-weight: 700;
    color: var(--text); padding-bottom: 8px;
    border-bottom: 2px solid var(--accent);
    margin: 24px 0 16px; display: inline-block;
}

/* ─── Day Table ──────────────────────────────────── */
.day-table { width: 100%; border-collapse: collapse; margin-top: 16px; }
.day-table th {
    font-family: var(--font-display);
    font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--text2);
    padding: 10px 12px; text-align: left;
    border-bottom: 2px solid var(--border-strong);
}
.day-table td {
    padding: 10px 12px; font-size: 14px;
    border-bottom: 1px solid var(--border); color: var(--text);
}
.day-table tr:hover td { background: var(--accent-soft); }

/* ─── Record Card ────────────────────────────────── */
.record-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 12px 16px; margin-bottom: 8px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s ease;
}
.record-card:hover { box-shadow: var(--shadow-md); }

/* ─── Summary Row ────────────────────────────────── */
.summary-row { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 20px; }
.summary-card {
    flex: 1; min-width: 140px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 18px; text-align: center;
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease;
}
.summary-card:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--border-strong);
}
.summary-label {
    font-family: var(--font-display);
    font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.1em; color: var(--text2); margin-bottom: 6px;
}
.summary-value { font-size: 28px; font-weight: 700; font-family: var(--font-body); }

/* ─── Insight / Focus Boxes ──────────────────────── */
.insight-box, .focus-box {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 14px; margin-bottom: 10px;
    box-shadow: var(--shadow-sm);
}
.insight-box:hover, .focus-box:hover {
    box-shadow: var(--shadow-md);
}

/* ─── Streak Pill ────────────────────────────────── */
.streak-pill {
    display: inline-block; font-size: 12px; font-weight: 600;
    font-family: var(--font-display);
    padding: 4px 14px; border-radius: 20px;
    color: var(--accent); background: var(--accent-soft); margin-left: 8px;
}

/* ─── Hero Banner ────────────────────────────────── */
.hero-banner {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 28px; text-align: center; margin-bottom: 20px;
    box-shadow: var(--shadow-sm);
}
.hero-label {
    font-family: var(--font-display);
    font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.12em; color: var(--text2); margin-bottom: 10px;
}
.hero-value {
    font-family: var(--font-display);
    font-size: 22px; font-weight: 900; color: var(--text);
}

/* ─── Scrollbar ──────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(79,124,130,0.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(79,124,130,0.6); }

/* ─── Status Boxes ───────────────────────────────── */
.success-box {
    background: rgba(79,124,130,0.15);
    border-left: 3px solid var(--pos);
    border-radius: var(--radius-md);
    padding: 12px 16px; color: var(--pos); margin: 10px 0; font-size: 14px;
}
.warning-box {
    background: rgba(201,122,138,0.1);
    border-left: 3px solid var(--neg);
    border-radius: var(--radius-md);
    padding: 12px 16px; color: var(--neg); margin: 10px 0; font-size: 14px;
}
.error-box {
    background: rgba(201,122,138,0.1);
    border-left: 3px solid var(--neg);
    border-radius: var(--radius-md);
    padding: 12px 16px; color: var(--neg); margin: 10px 0; font-size: 14px;
}
</style>"""

# ── Page Registry ──────────────────────────────────────────────────
_PAGES = {
    "Mission 21": "planner21.py",
    "Dashboard": "pages/dashboard.py",
    "Finance": "pages/finance.py",
    "Driving": "pages/driving.py",
    "Exercise": "pages/excercise.py",
    "Weekly Review": "pages/weekly_review.py",
    "Journal": "pages/journal.py",
    "News": "pages/news.py",
    "History": "pages/history.py",
    "Insights": "pages/insights.py",
    "Settings": "pages/settings.py",
}


# ── Injection Functions ─────────────────────────────────────────────
def inject_theme():
    """Inject the full theme CSS into the Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)


def inject_sidebar():
    """No-op kept for backwards compatibility."""
    pass


def nav_menu(current: str = ""):
    """Render a styled navigation selectbox."""
    page_names = list(_PAGES.keys())
    default_idx = page_names.index(current) if current in page_names else 0

    with st.container(key="nav_menu_container"):
        choice = st.selectbox(
            "nav",
            page_names,
            index=default_idx,
            label_visibility="collapsed",
            key="__nav_menu__",
        )

    if choice != current and choice in _PAGES:
        st.switch_page(_PAGES[choice])


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
        f'background:{color}15">{text}</span>'
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
        f'<div class="page-title" style="color:#000000 !important;">{title}</div>'
        f'{sub_html}'
        f'<div class="divider"></div>'
    )
