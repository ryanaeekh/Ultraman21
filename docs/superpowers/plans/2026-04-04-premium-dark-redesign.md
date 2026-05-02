# Premium Dark Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the Planner21 Streamlit app from warm-brown serif aesthetic to a premium dark SaaS trading-dashboard with glass-morphism cards, electric blue accents, Syne/DM Sans typography, and collapsed icon-rail sidebar.

**Architecture:** Create a shared `theme.py` module that all pages import. Strip planner21.py down to Today-only, extracting History/Insights/AI Coach/Settings into `pages/`. Restyle every page with the new component patterns. Remove dark mode toggle — app is always dark.

**Tech Stack:** Python, Streamlit, CSS3 (glass-morphism, backdrop-filter), Google Fonts (Syne, DM Sans)

**Spec:** `docs/superpowers/specs/2026-04-04-premium-dark-redesign-design.md`

---

## File Structure

### New Files
| File | Responsibility |
|------|---------------|
| `theme.py` | Shared CSS injection, design tokens, HTML helper functions |
| `pages/history.py` | Score history view (extracted from planner21.py:666-737) |
| `pages/insights.py` | Analytics/stats view (extracted from planner21.py:741-845) |
| `pages/ai_coach.py` | AI chat interface (extracted from planner21.py:850-1032) |
| `pages/settings.py` | App settings form (extracted from planner21.py:1037-1170) |

### Modified Files
| File | What Changes |
|------|-------------|
| `planner21.py` | Strip to Today page only, remove CSS/dark mode/sub-pages, import theme |
| `pages/dashboard.py` | Replace CSS + HTML with new design |
| `pages/finance.py` | Replace CSS + HTML with new design |
| `pages/excercise.py` | Replace CSS + HTML with new design |
| `pages/driving.py` | Replace CSS + HTML with new design |
| `pages/journal.py` | Replace CSS + HTML with new design |
| `pages/news.py` | Replace CSS + HTML with new design |
| `pages/weekly_review.py` | Replace CSS + HTML with new design |

### Unchanged
- `utils.py`, `data/` folder, all business logic

---

## Task 1: Create `theme.py` — Shared Theme Module

**Files:**
- Create: `theme.py`

This is the foundation. Every other task depends on this file.

- [ ] **Step 1: Create `theme.py` with design tokens and CSS**

```python
"""
Shared premium dark theme for Planner21.
Every page calls inject_theme() at the top.
"""
import streamlit as st

# ── Design Tokens (for use in Python-generated HTML) ──────────────────
ACCENT = "#00d4ff"
POS = "#00e68a"
NEG = "#ff4d6a"
BG = "#0d0d0d"
BG2 = "#111111"
CARD_BG = "rgba(255,255,255,0.04)"
TEXT = "#f0f0f0"
TEXT2 = "rgba(255,255,255,0.55)"
BORDER = "rgba(255,255,255,0.06)"


def inject_theme():
    """Inject the full premium dark CSS. Call at top of every page."""
    st.markdown(_CSS, unsafe_allow_html=True)


def inject_sidebar():
    """Inject sidebar icon-rail CSS. Call in the main entry point only."""
    st.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)


# ── HTML Helpers ──────────────────────────────────────────────────────

def metric_card(label: str, value: str, sub: str = "", color: str = "") -> str:
    """Trading-dashboard style metric card."""
    val_style = f"color:{color};" if color else ""
    return f'''<div class="card metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="{val_style}">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>'''


def detail_row(key: str, value: str, cls: str = "") -> str:
    """Key-value row for financial breakdowns."""
    return f'''<div class="detail-row">
        <span class="detail-key">{key}</span>
        <span class="detail-val {cls}">{value}</span>
    </div>'''


def section_card(title: str, content: str) -> str:
    """Glass card with section header."""
    return f'''<div class="card section-card">
        <div class="section-title">{title}</div>
        {content}
    </div>'''


def status_badge(text: str, color: str) -> str:
    """Pill-shaped status badge."""
    return f'<span class="badge" style="color:{color};background:{color}22;">{text}</span>'


def progress_bar(pct: float, color: str = "") -> str:
    """Thin 4px progress bar. pct is 0-100."""
    fill = color or ACCENT
    clamped = max(0, min(100, pct))
    return f'''<div class="progress-track">
        <div class="progress-fill" style="width:{clamped}%;background:{fill};"></div>
    </div>'''


def page_header(title: str, subtitle: str = "") -> str:
    """Page title + optional subtitle."""
    sub = f'<div class="page-subtitle">{subtitle}</div>' if subtitle else ""
    return f'<div class="page-title">{title}</div>{sub}<div class="divider"></div>'


# ── Main CSS ──────────────────────────────────────────────────────────

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

/* ── Base ───────────────────────────────────────── */
html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}
.block-container {
    max-width: 1200px !important;
    padding: 2rem 2rem 4rem !important;
}

/* ── Typography ─────────────────────────────────── */
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

/* ── Glass Cards ────────────────────────────────── */
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

/* ── Metric Card (Trading Dashboard) ────────────── */
.metric-card {
    text-align: center;
}
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
.metric-sub {
    font-size: 13px; color: var(--text2);
}

/* ── Detail Rows ────────────────────────────────── */
.detail-row {
    display: flex; justify-content: space-between;
    align-items: center; padding: 10px 0;
    border-bottom: 1px solid var(--border);
}
.detail-row:last-child { border-bottom: none; }
.detail-key {
    font-size: 14px; color: var(--text2);
}
.detail-val {
    font-size: 14px; font-weight: 600;
    color: var(--text);
}
.detail-val.positive { color: var(--pos); }
.detail-val.negative { color: var(--neg); }

/* ── Progress Bar ───────────────────────────────── */
.progress-track {
    width: 100%; height: 4px;
    background: rgba(255,255,255,0.08);
    border-radius: 2px; overflow: hidden;
    margin: 8px 0;
}
.progress-fill {
    height: 100%; border-radius: 2px;
    transition: width 0.5s ease;
    box-shadow: 0 0 8px rgba(0,212,255,0.3);
}

/* ── Status Badge ───────────────────────────────── */
.badge {
    display: inline-block;
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.06em;
    padding: 4px 12px; border-radius: 20px;
}

/* ── Buttons ────────────────────────────────────── */
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

/* ── Form Inputs ────────────────────────────────── */
div[data-testid="stForm"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
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

/* ── Selectbox dropdown ─────────────────────────── */
div[data-testid="stSelectbox"] > div > div {
    border-bottom: 1px solid rgba(255,255,255,0.15) !important;
}
[data-baseweb="popover"] {
    background: #1a1a1a !important;
    border: 1px solid var(--border) !important;
}
[data-baseweb="popover"] li {
    color: var(--text) !important;
    background: transparent !important;
}
[data-baseweb="popover"] li:hover {
    background: rgba(0,212,255,0.1) !important;
}

/* ── Tables ──────────────────────────────────────── */
.stDataFrame, div[data-testid="stDataFrame"] {
    border-radius: var(--radius-md) !important;
    overflow: hidden;
}
div[data-testid="stDataFrame"] table {
    background: transparent !important;
}
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

/* ── Charts ──────────────────────────────────────── */
.stPlotlyChart, div[data-testid="stVegaLiteChart"] {
    background: transparent !important;
}

/* ── Tabs ─────────────────────────────────────────── */
button[data-baseweb="tab"] {
    font-family: var(--font-body) !important;
    color: var(--text2) !important;
    background: transparent !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* ── Streamlit overrides ─────────────────────────── */
header[data-testid="stHeader"] {
    background: var(--bg) !important;
}
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

/* ── Execution pills ─────────────────────────────── */
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

/* ── Score ring ──────────────────────────────────── */
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

/* ── Accent-bordered card ────────────────────────── */
.accent-left-card {
    border-left: 3px solid var(--accent) !important;
}

/* ── Color utility classes ───────────────────────── */
.c-pos { color: var(--pos) !important; }
.c-neg { color: var(--neg) !important; }
.c-accent { color: var(--accent) !important; }
.c-muted { color: var(--text2) !important; }

/* ── Sidebar styling ─────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #0a0a0a !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-family: var(--font-body) !important;
    color: var(--text2) !important;
    transition: color 0.2s ease;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: var(--text) !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: var(--text2) !important;
}

/* ── Chat (AI Coach) ─────────────────────────────── */
div[data-testid="stChatMessage"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text) !important;
}
div[data-testid="stChatInput"] {
    border-color: var(--border) !important;
}
div[data-testid="stChatInput"] textarea {
    color: var(--text) !important;
    background: transparent !important;
}

/* ── History card ────────────────────────────────── */
.hist-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    backdrop-filter: blur(16px);
    padding: 20px 24px;
    margin-bottom: 12px;
    transition: all 0.3s ease;
}
.hist-card:hover {
    background: var(--card-hover);
    border-color: rgba(0,212,255,0.15);
}

/* ── Journal card ────────────────────────────────── */
.j-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    backdrop-filter: blur(16px);
    padding: 24px; margin-bottom: 12px;
}
.j-date {
    font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--text2);
    margin-bottom: 8px;
}
.j-text {
    font-size: 15px; line-height: 1.8;
    color: var(--text); white-space: pre-wrap;
}

/* ── News card ───────────────────────────────────── */
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
    letter-spacing: 0.06em; color: var(--accent);
    margin-bottom: 6px;
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
.news-meta {
    font-size: 11px; color: var(--text2);
    opacity: 0.6;
}

/* ── Section label (news) ────────────────────────── */
.section-label {
    font-family: var(--font-display);
    font-size: 18px; font-weight: 600;
    color: var(--text); padding-bottom: 8px;
    border-bottom: 2px solid var(--accent);
    margin: 24px 0 16px; display: inline-block;
}

/* ── Day table (weekly review) ───────────────────── */
.day-table { width: 100%; border-collapse: collapse; margin-top: 16px; }
.day-table th {
    font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.06em; color: var(--text2);
    padding: 10px 12px; text-align: left;
    border-bottom: 1px solid var(--border);
}
.day-table td {
    padding: 10px 12px; font-size: 14px;
    border-bottom: 1px solid var(--border);
    color: var(--text);
}
.day-table tr:hover td { background: rgba(255,255,255,0.03); }

/* ── Record card (finance) ───────────────────────── */
.record-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 12px 16px; margin-bottom: 8px;
    transition: background 0.2s ease;
}
.record-card:hover { background: rgba(255,255,255,0.04); }

/* ── Summary row (finance) ───────────────────────── */
.summary-row {
    display: flex; flex-wrap: wrap; gap: 12px;
    margin-bottom: 20px;
}
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
    letter-spacing: 0.08em; color: var(--text2);
    margin-bottom: 6px;
}
.summary-value {
    font-size: 28px; font-weight: 700;
    font-family: var(--font-body);
}

/* ── Quick insight / Focus boxes ─────────────────── */
.insight-box, .focus-box {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 14px; margin-bottom: 10px;
}
.insight-box:hover, .focus-box:hover {
    background: rgba(255,255,255,0.04);
}

/* ── Streak pill ─────────────────────────────────── */
.streak-pill {
    display: inline-block;
    font-size: 12px; font-weight: 600;
    padding: 4px 14px; border-radius: 20px;
    color: var(--accent);
    background: rgba(0,212,255,0.1);
    margin-left: 8px;
}

/* ── Hero banner (exercise) ──────────────────────── */
.hero-banner {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    backdrop-filter: blur(16px);
    padding: 28px; text-align: center;
    margin-bottom: 20px;
}
.hero-label {
    font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.1em; color: var(--text2);
    margin-bottom: 10px;
}
.hero-value {
    font-family: var(--font-display);
    font-size: 22px; font-weight: 700;
    color: var(--text);
}

/* ── Scrollbar ───────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.1); border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* ── Success/warning/error boxes ─────────────────── */
.success-box {
    background: rgba(0,230,138,0.08);
    border-left: 3px solid var(--pos);
    border-radius: var(--radius-md);
    padding: 12px 16px; color: var(--pos);
    margin: 10px 0; font-size: 14px;
}
.warning-box {
    background: rgba(255,180,0,0.08);
    border-left: 3px solid #ffb400;
    border-radius: var(--radius-md);
    padding: 12px 16px; color: #ffb400;
    margin: 10px 0; font-size: 14px;
}
.error-box {
    background: rgba(255,77,106,0.08);
    border-left: 3px solid var(--neg);
    border-radius: var(--radius-md);
    padding: 12px 16px; color: var(--neg);
    margin: 10px 0; font-size: 14px;
}
</style>"""

_SIDEBAR_CSS = """<style>
/* Icon-rail sidebar — narrow by default, expands on hover */
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
/* Hide sidebar collapse button */
button[data-testid="stSidebarCollapse"] { display: none !important; }
</style>"""
```

- [ ] **Step 2: Verify theme.py loads without error**

Run: `cd C:\Users\ryana\OneDrive\Desktop\Ultraman21 && python -c "import theme; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add theme.py
git commit -m "feat: add shared premium dark theme module"
```

---

## Task 2: Redesign `planner21.py` — Strip to Today Only

**Files:**
- Modify: `planner21.py` (currently 1170 lines → ~350 lines)

This task removes History, Insights, AI Coach, Settings sub-pages (they move to `pages/` in later tasks), removes all inline CSS, removes dark mode toggle, and restyles the Today page with the new design.

- [ ] **Step 1: Read the current `planner21.py` fully**

Read: `planner21.py`

- [ ] **Step 2: Rewrite `planner21.py`**

Keep all of these from the original:
- Imports (lines 1-8)
- Constants: `DATA_DIR`, `PLANNER_CSV`, `SETTINGS_FILE` (lines 11-18)
- Helper functions: `backup_csv` (24-33), `_ensure_columns` (54-59), `load_planner` (80-91), `load_settings` (94-96), `invalidate_cache` (99-101), `save_planner` (104-107), `save_settings` (110-113), `clean_text` (116-120), `get_row` (123-125), `calculate_score` (128-129), `get_execution_label` (132-140), `compute_streak` (143-153), `compute_weekly_avg` (156-161), `compute_habit_streak` (164-173)

Remove completely:
- Lines 179-472: entire CSS style block
- Lines 492-519: sidebar navigation (radio buttons for sub-pages)
- Lines 666-737: History page handler
- Lines 741-845: Insights page handler
- Lines 850-1032: AI Coach page handler
- Lines 1037-1170: Settings page handler
- All `st.session_state["dark_mode"]` references
- The `st.session_state["page"]` navigation logic

Add at the top after imports:
```python
from theme import inject_theme, inject_sidebar, metric_card, page_header, status_badge, progress_bar, ACCENT, POS, NEG
```

Replace the page layout with:
- `inject_theme()` + `inject_sidebar()` calls
- `st.set_page_config(page_title="Mission 21", page_icon="🎯", layout="wide")`
- Today page content only (lines 525-660), restyled with new HTML patterns:
  - Score displayed in a CSS conic-gradient ring using `.score-ring`
  - 3 execution pills using `.exec-pill.done` / `.exec-pill.pending`
  - Morning checklist in a glass `.card`
  - Daily entry form in a glass `.card` with bottom-border inputs
  - Focus quote in a subtle card with italic Syne

The Today page logic (data loading, form submission, score calculation) stays identical — only the HTML/CSS wrapping changes.

- [ ] **Step 3: Run the app and verify Today page renders**

Run: `python -m streamlit run planner21.py` and check `http://localhost:8501`
Expected: Dark background, blue accents, glass cards, score ring, no sidebar sub-pages

- [ ] **Step 4: Commit**

```bash
git add planner21.py
git commit -m "feat: redesign planner21 as Today-only with premium dark theme"
```

---

## Task 3: Extract `pages/history.py`

**Files:**
- Create: `pages/history.py`
- Source: `planner21.py` lines 666-737, plus helpers: `load_planner`, `clean_text`, `get_execution_label`, `backup_csv`, `save_planner`, `invalidate_cache`, `_ensure_columns`

- [ ] **Step 1: Create `pages/history.py`**

Structure:
- Import streamlit, pandas, os, datetime
- Import from theme: `inject_theme, page_header, status_badge, progress_bar, ACCENT, POS, NEG`
- Copy needed helpers locally (same pattern as other pages — local CSV loaders)
- Replicate the data paths: `DATA_DIR`, `PLANNER_CSV`, `PLANNER_COLUMNS`
- Copy `load_planner()`, `backup_csv()`, `save_planner()`, `clean_text()`, `get_execution_label()`, `_ensure_columns()`
- Page content: call `inject_theme()`, render `page_header("History", "Your daily scores")`, then the history cards loop from planner21.py:666-737
- Restyle history cards using `.hist-card` class from theme
- Status badges use `status_badge()` helper
- Progress bars use `progress_bar()` helper
- Delete button per card preserved

- [ ] **Step 2: Verify page loads in sidebar nav**

Run the app, click History in sidebar
Expected: Dark themed history cards with glass effect

- [ ] **Step 3: Commit**

```bash
git add pages/history.py
git commit -m "feat: extract history page with premium dark styling"
```

---

## Task 4: Extract `pages/insights.py`

**Files:**
- Create: `pages/insights.py`
- Source: `planner21.py` lines 741-845, plus helpers: `load_planner`, `compute_streak`, `compute_habit_streak`

- [ ] **Step 1: Create `pages/insights.py`**

Structure:
- Import streamlit, pandas, os, datetime
- Import from theme: `inject_theme, page_header, metric_card, progress_bar, section_card, ACCENT, POS`
- Copy needed helpers locally: `load_planner()`, `compute_streak()`, `compute_habit_streak()`, `_ensure_columns()`
- Page content from planner21.py:741-845 restyled:
  - 4 stat cards using `metric_card()`: Days Logged, Perfect Days, All-Time Avg, Streak
  - Score trend line chart (Streamlit native, keep as-is)
  - 3 habit cards with `progress_bar(pct, POS)` for completion rates
  - Streak cards
  - Last 7 days using styled table rows

- [ ] **Step 2: Verify page loads**

Expected: Stat grid, blue progress bars, clean trend chart on dark bg

- [ ] **Step 3: Commit**

```bash
git add pages/insights.py
git commit -m "feat: extract insights page with premium dark styling"
```

---

## Task 5: Extract `pages/ai_coach.py`

**Files:**
- Create: `pages/ai_coach.py`
- Source: `planner21.py` lines 850-1032, plus `_build_data_context()` (868-926)

- [ ] **Step 1: Create `pages/ai_coach.py`**

Structure:
- Import streamlit, os, datetime, pandas, dotenv
- Import from theme: `inject_theme, page_header, ACCENT`
- Copy `_build_data_context()` function (loads all CSV data for context)
- Copy the Anthropic API integration, system prompt, chat state, smart features buttons
- Restyle: `inject_theme()`, `page_header("AI Coach", "Your productivity assistant")`
- Chat messages styled by theme CSS (`.stChatMessage` overrides in theme.py)
- Smart feature buttons in a glass `.card`

- [ ] **Step 2: Verify page loads with API key prompt**

Expected: Dark themed chat interface, smart feature buttons in glass card

- [ ] **Step 3: Commit**

```bash
git add pages/ai_coach.py
git commit -m "feat: extract AI coach page with premium dark styling"
```

---

## Task 6: Extract `pages/settings.py`

**Files:**
- Create: `pages/settings.py`
- Source: `planner21.py` lines 1037-1170

- [ ] **Step 1: Create `pages/settings.py`**

Structure:
- Import streamlit, os, json, datetime
- Import from theme: `inject_theme, page_header`
- Copy `SETTINGS_FILE` path, `load_settings()`, `save_settings()`, `backup_csv()`
- All settings form fields from planner21.py:1037-1170:
  - Long-term goals textarea
  - Income/hourly rate/budget targets
  - Checklist items, expense categories
  - Export/reset, backup restore
- Restyle: `inject_theme()`, `page_header("Settings", "Configure your system")`
- Form inside a glass `.card`

- [ ] **Step 2: Verify settings save and load correctly**

Expected: All settings persist to JSON, dark glass card form

- [ ] **Step 3: Commit**

```bash
git add pages/settings.py
git commit -m "feat: extract settings page with premium dark styling"
```

---

## Task 7: Redesign `pages/dashboard.py`

**Files:**
- Modify: `pages/dashboard.py` (665 lines)

- [ ] **Step 1: Read current `pages/dashboard.py`**

Read the file fully to understand current helper functions and data logic.

- [ ] **Step 2: Rewrite the file**

Keep all of these unchanged:
- Imports (1-8)
- All helper functions (26-363) — `safe_read_csv`, `safe_float`, `safe_bool`, `clean_text`, `parse_date_column`, `get_days_in_month`, `load_*` functions, all calculation helpers (`get_today_income`, `get_today_variable_expense`, etc.), `build_insights`, `get_strongest_lever`, `get_recovery_action`
- Data loading block (369-413)

Remove:
- Lines 419-502: entire CSS style block
- Lines 492-502: dark mode CSS injection
- All `st.session_state["dark_mode"]` references

Replace with:
- `from theme import inject_theme, metric_card, detail_row, section_card, page_header, status_badge, progress_bar, ACCENT, POS, NEG`
- `inject_theme()` call at top
- `page_header("System Dashboard", "Daily overview")`
- Rewrite `detail_row()` and `section_card()` local functions to use theme helpers instead
- Top 3 metric cards using `metric_card()` — big numbers for Net, Exercise, Score
- Rule banner using `.accent-left-card` class
- 2-column layout preserved but with glass cards
- All HTML classes updated to match theme.py classes

- [ ] **Step 3: Verify dashboard renders**

Expected: 3 large metric cards, glass panels, blue accents, clean detail rows

- [ ] **Step 4: Commit**

```bash
git add pages/dashboard.py
git commit -m "feat: redesign dashboard with premium dark theme"
```

---

## Task 8: Redesign `pages/finance.py`

**Files:**
- Modify: `pages/finance.py` (903 lines)

- [ ] **Step 1: Read current `pages/finance.py`**

- [ ] **Step 2: Rewrite the file**

Keep unchanged:
- Imports (1-6)
- All helper functions (26-282): `backup_csv`, `clean_text`, `safe_float`, CSV loaders, financial calculations
- Session state setup (288-292)
- All form submission logic

Remove:
- Lines 297-453: entire CSS style block
- Dark mode references

Replace with:
- `from theme import inject_theme, page_header, metric_card, detail_row, section_card, ACCENT, POS, NEG`
- `inject_theme()` call
- `page_header("Finance", "Track income and expenses")`
- Summary cards using `.summary-card` / `.summary-row` classes
- Budget alerts using `.warning-box` / `.error-box` classes instead of `st.error`
- Record cards using `.record-card` class
- All forms in glass `.card` containers
- Finance dashboard and expense breakdown in glass cards

- [ ] **Step 3: Verify finance page — add/edit/delete expenses**

Expected: Glass cards, big summary numbers, clean record list, budget alerts styled

- [ ] **Step 4: Commit**

```bash
git add pages/finance.py
git commit -m "feat: redesign finance page with premium dark theme"
```

---

## Task 9: Redesign `pages/excercise.py`

**Files:**
- Modify: `pages/excercise.py` (591 lines)

- [ ] **Step 1: Read current `pages/excercise.py`**

- [ ] **Step 2: Rewrite the file**

Keep unchanged:
- Imports (1-5)
- All helpers (22-126): `backup_csv`, `safe_read_csv`, `ensure_columns`, `safe_float`, `safe_text`, `save_exercise_df`, `calculate_pace`, `get_today_row`, `get_status_badge`
- Data loading (132-140)
- All form submission logic

Remove:
- Lines 145-322: entire CSS style block

Replace with:
- `from theme import inject_theme, page_header, metric_card, section_card, status_badge as theme_badge, progress_bar, ACCENT, POS`
- `inject_theme()` call
- `page_header("Exercise", "Track your training")`
- Hero banner using `.hero-banner` / `.hero-label` / `.hero-value`
- 3 metric cards using `metric_card()` for distance, time, total
- Log form in glass `.card`
- Summary in glass `.card`
- History table styled by theme CSS
- Trend chart: blue line on dark (Streamlit native chart, styled by theme)

- [ ] **Step 3: Verify exercise tracking flow**

Expected: Hero banner, glass cards, blue trend chart

- [ ] **Step 4: Commit**

```bash
git add pages/excercise.py
git commit -m "feat: redesign exercise page with premium dark theme"
```

---

## Task 10: Redesign `pages/driving.py`

**Files:**
- Modify: `pages/driving.py` (304 lines)

- [ ] **Step 1: Read current `pages/driving.py`**

- [ ] **Step 2: Rewrite the file**

Keep unchanged:
- Imports (1-4)
- `backup_csv` (85-94), `parse_time` (157-163)
- Configuration/settings loading (77-107)
- File setup (123-131)
- All form submission logic
- Dashboard calculation logic

Remove:
- Lines 8-71: CSS style block
- Dark mode references (61-71)

Replace with:
- `from theme import inject_theme, page_header, metric_card, section_card, detail_row, status_badge, ACCENT, POS, NEG`
- `inject_theme()` call
- `page_header("Driving", "Income tracking")`
- 2-column layout: input form (left) in glass `.card`, dashboard (right) in glass `.card`
- Big earnings number (36px) in dashboard card
- Hourly rate below
- Target status as `status_badge()` with glow
- Time display styled clean (not digital-clock since that would need custom font)

- [ ] **Step 3: Verify driving data entry and dashboard display**

Expected: Glass cards, big earnings number, clean status badges

- [ ] **Step 4: Commit**

```bash
git add pages/driving.py
git commit -m "feat: redesign driving page with premium dark theme"
```

---

## Task 11: Redesign `pages/journal.py`

**Files:**
- Modify: `pages/journal.py` (160 lines)

- [ ] **Step 1: Read current `pages/journal.py`**

- [ ] **Step 2: Rewrite the file**

Keep unchanged:
- Imports (1-4)
- `backup_csv` (98-107), `load_journal` (109-114), `save_journal` (116-118)
- Form submission logic

Remove:
- Lines 8-75: CSS style block
- Dark mode references (78-88)

Replace with:
- `from theme import inject_theme, page_header`
- `inject_theme()` call
- `page_header("Journal", "Daily reflections")`
- `max-width: 900px` on `.block-container` (override inline)
- Entry form: glass `.card` with large textarea
- Past entries: `.j-card` class (defined in theme.py) with `.j-date` and `.j-text`

- [ ] **Step 3: Verify journal entry creation and display**

Expected: Glass cards, clean typography, comfortable reading

- [ ] **Step 4: Commit**

```bash
git add pages/journal.py
git commit -m "feat: redesign journal page with premium dark theme"
```

---

## Task 12: Redesign `pages/news.py`

**Files:**
- Modify: `pages/news.py` (180 lines)

- [ ] **Step 1: Read current `pages/news.py`**

- [ ] **Step 2: Rewrite the file**

Keep unchanged:
- Imports (1-6)
- `fetch_news` (75-104), `render_articles` (107-138)
- API key check and news section logic

Remove:
- Lines 18-69: CSS style block
- Dark mode references (59-69)

Replace with:
- `from theme import inject_theme, page_header`
- `inject_theme()` call
- `page_header("News", "Latest headlines")`
- `render_articles()` function updated to use `.news-card`, `.news-source`, `.news-title`, `.news-desc`, `.news-meta` classes from theme.py
- Section labels use `.section-label` class with accent underline
- Cards have hover lift animation (already in theme CSS)

- [ ] **Step 3: Verify news loads and cards display**

Expected: Glass news cards with hover lift, accent section labels

- [ ] **Step 4: Commit**

```bash
git add pages/news.py
git commit -m "feat: redesign news page with premium dark theme"
```

---

## Task 13: Redesign `pages/weekly_review.py`

**Files:**
- Modify: `pages/weekly_review.py` (402 lines)

- [ ] **Step 1: Read current `pages/weekly_review.py`**

- [ ] **Step 2: Rewrite the file**

Keep unchanged:
- Imports (1-6)
- All helpers (26-104): `safe_read_csv`, `safe_float`, `safe_bool`, `get_days_in_month`, all loaders
- Data loading and weekly calculations (110-192)

Remove:
- Lines 198-257: CSS style block
- Dark mode references (247-257)

Replace with:
- `from theme import inject_theme, page_header, metric_card, detail_row, section_card, ACCENT, POS, NEG`
- `inject_theme()` call
- `page_header("Weekly Review", f"{start_date.strftime('%b %d')} — {today_str}")`
- 4 metric cards using `metric_card()`: Income, Expenses, Net, Avg Score
- 2-column: Financial + Execution breakdowns using `section_card()` + `detail_row()`
- Day-by-day table using `.day-table` class from theme.py
- Color-coded cells using `.c-pos` / `.c-neg` utility classes

- [ ] **Step 3: Verify weekly data displays correctly**

Expected: 4 big metric cards, glass breakdown panels, colored table

- [ ] **Step 4: Commit**

```bash
git add pages/weekly_review.py
git commit -m "feat: redesign weekly review with premium dark theme"
```

---

## Task 14: Final Integration & Cleanup

**Files:**
- All files

- [ ] **Step 1: Run the full app and click through every page**

Run: `python -m streamlit run planner21.py`
Check each page: Planner, Dashboard, Finance, Exercise, Driving, Journal, News, Weekly Review, History, Insights, AI Coach, Settings

- [ ] **Step 2: Fix any rendering issues found**

Common issues to check:
- Font loading (Google Fonts import works)
- Glass-morphism renders (backdrop-filter support)
- Sidebar icon-rail animation works on hover
- All forms submit correctly
- All data displays correctly
- No leftover old CSS classes or dark mode references
- Charts readable on dark background

- [ ] **Step 3: Remove any dead code or unused imports across all files**

Grep for: `dark_mode`, old CSS variable names (`#8a7055`, `#f5f0e8`, `#ede8de`, `Georgia`), old class names that no longer exist

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete premium dark redesign across all pages"
```
