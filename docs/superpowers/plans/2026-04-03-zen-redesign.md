# Zen Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply Japanese-minimalism styling to all 5 Planner21 pages — warm parchment tones, Georgia serif, generous spacing, quiet UI chrome — without touching any functionality.

**Architecture:** Create `.streamlit/config.toml` to set the native Streamlit theme for light mode (beige background, stone accent). Update each page's inline `<style>` block to use new design tokens, Georgia font, softened font weights, and thinner progress bars. Add a `@media (prefers-color-scheme: dark)` block to each page for walnut dark-mode tones.

**Tech Stack:** Streamlit, CSS custom properties, Georgia (system serif — no external font loading)

---

## File Map

| Action | File | What changes |
|---|---|---|
| Create | `.streamlit/config.toml` | New Streamlit theme — light mode base |
| Modify | `planner21.py` lines 148–421 | Full `<style>` block replacement |
| Modify | `pages/dashboard.py` lines 419–457 | Full `<style>` block replacement |
| Modify | `pages/finance.py` lines 257–393 | Full `<style>` block replacement |
| Modify | `pages/driving.py` lines 8–39 | Full `<style>` block replacement |
| Modify | `pages/excercise.py` lines 130–277 | Full `<style>` block replacement |

---

## Task 1: Create `.streamlit/config.toml`

**Files:**
- Create: `.streamlit/config.toml`

- [ ] **Step 1: Create the directory and file**

```bash
mkdir -p .streamlit
```

Then create `.streamlit/config.toml` with this content:

```toml
[theme]
primaryColor            = "#8a7055"
backgroundColor         = "#f5f0e8"
secondaryBackgroundColor = "#ede8de"
textColor               = "#3a3028"
font                    = "serif"
```

- [ ] **Step 2: Verify the app loads with the new theme**

Run from the `Ultraman21` directory:
```bash
python -m streamlit run planner21.py
```

Expected: page background is warm parchment (`#f5f0e8`), sidebar background is slightly darker beige (`#ede8de`), accent (links, focus) is stone brown. Text is dark warm brown.

- [ ] **Step 3: Commit**

```bash
git add .streamlit/config.toml
git commit -m "style: add streamlit zen theme config"
```

---

## Task 2: Update `planner21.py` style block

**Files:**
- Modify: `planner21.py` lines 148–421

- [ ] **Step 1: Replace the entire `<style>` block**

Find the block that starts at line 147:
```python
st.markdown("""
<style>
/* ── TOKENS ── */
:root {
    --r-lg: 20px; ...
```
...and ends at line 422:
```python
""", unsafe_allow_html=True)
```

Replace it entirely with:

```python
st.markdown("""
<style>
/* ── TOKENS ── */
:root {
    --r-lg: 18px; --r-md: 12px; --r-sm: 8px;
    --border: 1px solid rgba(0,0,0,0.07);
    --shadow: 0 1px 3px rgba(0,0,0,0.04);
    --accent: #8a7055;
    --accent-soft: rgba(138,112,85,0.09);
    --pos: #5a9a6a; --neg: #b87070;
}
@media (prefers-color-scheme: dark) {
    :root {
        --accent: #b08a65;
        --accent-soft: rgba(176,138,101,0.12);
        --border: 1px solid rgba(255,255,255,0.07);
        --shadow: 0 1px 3px rgba(0,0,0,0.12);
        --pos: #7ab88a;
    }
}

/* ── TYPOGRAPHY ── */
html, body, [class*="css"] {
    font-family: Georgia, 'Times New Roman', serif !important;
}
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
    font-family: Georgia, 'Times New Roman', serif !important;
}

/* ── LAYOUT ── */
.block-container {
    max-width: 1100px;
    padding-top: 4rem !important;
    padding-bottom: 4rem !important;
}

/* ── FORM / INPUT RESETS ── */
div[data-testid="stForm"] {
    border: none !important; padding: 0 !important; background: transparent !important;
}
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
    border-radius: 12px !important;
    font-size: 14.5px !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
    transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
}
div[data-testid="stTextArea"] textarea:focus,
div[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(138,112,85,0.10) !important;
}

/* ── BUTTONS ── */
div.stButton > button {
    border-radius: 12px !important;
    border: 1px solid rgba(0,0,0,0.14) !important;
    padding: 0.45rem 1rem !important;
    font-weight: 400 !important;
    font-size: 13.5px !important;
    font-family: Georgia, serif !important;
    background: var(--secondary-background-color) !important;
    color: inherit !important;
    transition: border-color 0.15s ease !important;
}
div.stButton > button:hover {
    border-color: var(--accent) !important;
    box-shadow: 0 2px 8px rgba(138,112,85,0.12) !important;
}

/* ── PAGE HEADER ── */
.page-header { margin-bottom: 2rem; }
.page-title {
    font-size: 2.1rem; font-weight: 500;
    letter-spacing: -0.01em; line-height: 1.1;
    color: var(--accent); margin-bottom: 4px;
}
.page-sub { font-size: 0.93rem; opacity: 0.55; letter-spacing: 0.01em; }

/* ── SECTION LABEL ── */
.section-label {
    font-size: 10px; font-weight: 400; letter-spacing: 0.12em;
    text-transform: uppercase; opacity: 0.55; margin-bottom: 14px;
}

/* ── CARDS ── */
.section-card {
    border: var(--border); border-radius: var(--r-lg);
    padding: 28px 32px; background: var(--secondary-background-color);
    box-shadow: var(--shadow); margin-bottom: 20px;
}
.section-title {
    font-size: 0.95rem; font-weight: 500; letter-spacing: -0.01em;
    margin-bottom: 16px; opacity: 0.88;
}
.goals-display {
    white-space: pre-wrap; font-size: 15px;
    line-height: 1.85; opacity: 0.90;
}

/* ── SCORE CARD ── */
.score-card {
    border: var(--border); border-radius: var(--r-lg);
    padding: 28px 32px; background: var(--secondary-background-color);
    box-shadow: var(--shadow); margin-bottom: 20px;
}
.score-label {
    font-size: 10px; text-transform: uppercase; letter-spacing: 0.12em;
    font-weight: 400; opacity: 0.55; margin-bottom: 8px;
}
.score-value {
    font-size: 3.2rem; font-weight: 500; letter-spacing: -0.03em; line-height: 1;
    color: var(--accent); margin-bottom: 4px;
}
.score-denom { font-size: 1.3rem; opacity: 0.4; }
.score-status { font-size: 0.92rem; font-weight: 400; margin: 8px 0 16px; opacity: 0.70; }
.progress-shell {
    width: 100%; height: 3px; border-radius: 999px;
    overflow: hidden; background: rgba(0,0,0,0.07);
}
.progress-bar { height: 100%; border-radius: 999px; background: var(--accent); }

/* ── EXEC CHECKS ── */
.exec-checks { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }
.exec-check {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 7px 13px; border-radius: 999px; border: var(--border);
    font-size: 12px; font-weight: 400;
    background: var(--secondary-background-color); box-shadow: var(--shadow);
    letter-spacing: 0.01em;
}
.exec-check.done { border-color: rgba(90,154,106,0.40); background: rgba(90,154,106,0.08); color: var(--pos); }
.exec-check.miss { opacity: 0.35; }

/* ── TODAY'S PLAN ITEMS ── */
.plan-item {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 12px 0; border-bottom: 1px solid rgba(0,0,0,0.05);
}
.plan-item:last-of-type { border-bottom: none; }
.plan-icon { font-size: 1rem; margin-top: 1px; flex-shrink: 0; }
.plan-body { flex: 1; min-width: 0; }
.plan-title { font-size: 13.5px; font-weight: 500; }
.plan-sub { font-size: 12px; opacity: 0.55; margin-top: 2px; line-height: 1.6;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.plan-done .plan-title { color: var(--pos); }
.plan-miss { opacity: 0.45; }
.plan-footer { font-size: 12px; opacity: 0.55; margin-top: 4px; }

/* ── MARK COMPLETED HEADER ── */
.mark-header {
    font-size: 10px; font-weight: 400; letter-spacing: 0.12em;
    text-transform: uppercase; opacity: 0.50; margin-bottom: 12px;
}

/* ── INSIGHT METRIC CARDS ── */
.ins-grid { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }
.ins-card {
    flex: 1; min-width: 130px;
    border: var(--border); border-radius: var(--r-md);
    padding: 20px 24px; background: var(--secondary-background-color);
    box-shadow: var(--shadow);
}
.ins-card-label {
    font-size: 10px; text-transform: uppercase; letter-spacing: 0.12em;
    font-weight: 400; opacity: 0.50; margin-bottom: 10px;
}
.ins-card-value {
    font-size: 1.95rem; font-weight: 500; letter-spacing: -0.02em; line-height: 1;
}
.ins-card-sub { font-size: 12px; opacity: 0.55; margin-top: 6px; }

/* ── HABIT BARS ── */
.habit-card {
    border: var(--border); border-radius: var(--r-md);
    padding: 18px 22px; background: var(--secondary-background-color);
    box-shadow: var(--shadow); margin-bottom: 0;
}
.habit-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.habit-name { font-size: 14px; font-weight: 500; }
.habit-pct { font-size: 14px; font-weight: 500; color: var(--accent); }
.habit-bar-shell {
    width: 100%; height: 3px; border-radius: 999px;
    background: rgba(0,0,0,0.07); overflow: hidden;
}
.habit-bar-fill { height: 100%; border-radius: 999px; background: var(--accent); }

/* ── HISTORY CARDS ── */
.hist-card {
    border: var(--border); border-radius: var(--r-lg);
    padding: 18px 22px; background: var(--secondary-background-color);
    box-shadow: var(--shadow); margin-bottom: 14px;
    transition: border-color 0.15s ease;
}
.hist-card:hover { border-color: rgba(138,112,85,0.30); }
.hist-header { display: flex; align-items: center; gap: 14px; margin-bottom: 12px; }
.hist-date { font-size: 14px; font-weight: 500; min-width: 105px; }
.hist-bar-wrap { flex: 1; height: 3px; border-radius: 999px; background: rgba(0,0,0,0.07); overflow: hidden; }
.hist-bar-fill { height: 100%; border-radius: 999px; background: var(--accent); }
.hist-score { font-size: 13.5px; font-weight: 500; min-width: 50px; text-align: right; }
.hist-label { font-size: 12px; opacity: 0.60; min-width: 148px; text-align: right; }
.hist-body { display: flex; gap: 28px; flex-wrap: wrap; font-size: 13.5px; opacity: 0.82; }
.hist-col { flex: 1; min-width: 155px; }
.hist-col-title {
    font-size: 10px; text-transform: uppercase; letter-spacing: 0.12em;
    font-weight: 400; opacity: 0.50; margin-bottom: 8px;
}
.hist-item { margin-bottom: 5px; line-height: 1.6; }
.hist-reflection {
    margin-top: 14px; padding: 12px 16px; border-radius: var(--r-sm);
    background: var(--accent-soft); font-size: 13.5px;
    font-style: italic; line-height: 1.7; opacity: 0.82;
    border-left: 2px solid rgba(138,112,85,0.30);
}

/* ── 7-DAY ROWS ── */
.week-row {
    display: flex; align-items: center; gap: 14px;
    padding: 11px 16px; border-radius: var(--r-md);
    background: var(--secondary-background-color); border: var(--border);
    margin-bottom: 8px; font-size: 13.5px; box-shadow: var(--shadow);
}
.week-date { font-weight: 500; min-width: 100px; }
.week-bar-wrap { flex: 1; height: 3px; border-radius: 999px; background: rgba(0,0,0,0.07); overflow: hidden; }
.week-bar-fill { height: 100%; border-radius: 999px; background: var(--accent); }
.week-score { font-weight: 500; min-width: 50px; text-align: right; }
.week-label { opacity: 0.60; min-width: 140px; text-align: right; font-size: 12px; }

/* ── FOCUS QUOTE CARD ── */
.focus-quote-card {
    border: 1px solid rgba(138,112,85,0.30);
    border-radius: var(--r-lg);
    padding: 28px 32px 24px;
    background: var(--accent-soft);
    box-shadow: none;
    margin-bottom: 20px;
}
.focus-quote-label {
    font-size: 1.1rem; font-weight: 500; letter-spacing: 0.10em;
    text-transform: uppercase; color: var(--accent);
    margin-bottom: 14px; text-align: center;
}
.focus-quote-mark {
    font-size: 4.5rem; line-height: 0.6;
    color: var(--accent); opacity: 0.20;
    font-family: Georgia, serif;
    margin-bottom: 12px;
}
.focus-quote-text {
    font-size: 15px; line-height: 1.9;
    font-style: italic; opacity: 0.85;
    letter-spacing: 0.01em;
}
.focus-quote-attrib {
    margin-top: 18px;
    font-size: 13px; font-weight: 400;
    opacity: 0.45; letter-spacing: 0.04em;
}

/* ── SIDEBAR ── */
.mission-quote {
    font-size: 12.5px; line-height: 1.8; opacity: 0.65;
    font-style: italic; margin-bottom: 4px;
    padding: 12px 16px; border-radius: var(--r-md);
    background: var(--accent-soft);
    border-left: 2px solid rgba(138,112,85,0.30);
}
.mission-attrib { font-size: 11.5px; opacity: 0.40; margin-top: 8px; font-style: normal; }

section[data-testid="stSidebar"] { border-right: 1px solid rgba(0,0,0,0.07); }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span { font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)
```

- [ ] **Step 2: Visual verification**

With the app running (`python -m streamlit run planner21.py`), open the Planner page and check:
- Background is parchment beige, sidebar is slightly darker beige
- Page title uses Georgia serif at medium weight (not heavy/bold)
- Section labels are small, light, uppercase — not bold
- Score card has no accent bar along the top
- Progress bar is thin (3px)
- Buttons have no upward-bounce on hover

- [ ] **Step 3: Commit**

```bash
git add planner21.py
git commit -m "style: zen redesign for planner page"
```

---

## Task 3: Update `pages/dashboard.py` style block

**Files:**
- Modify: `pages/dashboard.py` lines 419–457

- [ ] **Step 1: Replace the `<style>` block**

Find the block starting at line 419:
```python
st.markdown("""
<style>
.block-container { max-width:1280px; padding-top:1.6rem !important; ...
```
...ending at the `""")` that closes it (around line 458).

Replace it entirely with:

```python
st.markdown("""
<style>
/* ── TOKENS ── */
:root {
    --border: 1px solid rgba(0,0,0,0.07);
    --shadow: 0 1px 3px rgba(0,0,0,0.04);
    --radius-lg: 18px; --radius-md: 12px;
    --accent: #8a7055;
    --pos: #5a9a6a; --neg: #b87070;
}
@media (prefers-color-scheme: dark) {
    :root {
        --accent: #b08a65;
        --border: 1px solid rgba(255,255,255,0.07);
        --shadow: 0 1px 3px rgba(0,0,0,0.12);
        --pos: #7ab88a;
    }
}
html, body, [class*="css"] { font-family: Georgia, 'Times New Roman', serif !important; }

.block-container { max-width:1200px; padding-top:4rem !important; padding-bottom:4rem !important; }
.rule-banner { border:var(--border); border-radius:var(--radius-lg); padding:24px 28px; background:var(--secondary-background-color); box-shadow:var(--shadow); margin-bottom:20px; }
.rule-label { font-size:10px; opacity:0.55; letter-spacing:0.12em; text-transform:uppercase; font-weight:400; margin-bottom:7px; }
.rule-value { font-size:1.35rem; font-weight:400; line-height:1.6; }
.metric-card { border:var(--border); border-radius:var(--radius-lg); padding:22px 22px 18px; background:var(--secondary-background-color); box-shadow:var(--shadow); min-height:158px; height:100%; }
.metric-head { display:flex; justify-content:space-between; align-items:flex-start; gap:10px; }
.metric-label { font-size:10px; opacity:0.55; margin-bottom:7px; text-transform:uppercase; letter-spacing:0.12em; font-weight:400; }
.metric-value { font-size:2rem; font-weight:500; line-height:1.1; margin-bottom:5px; letter-spacing:-0.02em; }
.metric-sub { font-size:13px; opacity:0.68; line-height:1.6; }
.metric-icon { font-size:1.45rem; opacity:0.75; }
.progress-shell { width:100%; height:3px; border-radius:999px; overflow:hidden; background:rgba(0,0,0,0.07); margin-top:14px; }
.progress-bar { height:100%; border-radius:999px; background:var(--accent); }
.section-card { border:var(--border); border-radius:var(--radius-lg); padding:24px 28px; background:var(--secondary-background-color); box-shadow:var(--shadow); height:100%; }
.section-title { font-size:1rem; font-weight:500; margin-bottom:1rem; letter-spacing:-0.01em; }
.status-chip { display:inline-block; padding:7px 14px; border-radius:999px; font-size:0.88rem; font-weight:400; margin-bottom:10px; border:var(--border); background:var(--secondary-background-color); }
.status-chip.good { color:var(--pos); } .status-chip.mid { color:#c8a850; } .status-chip.warn { color:#c88050; } .status-chip.bad { color:var(--neg); }
.detail-list { display:grid; gap:0; }
.detail-row { display:flex; justify-content:space-between; align-items:center; gap:16px; padding:11px 0; border-bottom:1px solid rgba(0,0,0,0.05); font-size:0.93rem; }
.detail-row:last-child { border-bottom:none; }
.detail-key { opacity:0.65; } .detail-value { font-weight:500; text-align:right; }
.insight-box { border:var(--border); border-radius:var(--radius-md); padding:14px 18px; background:var(--secondary-background-color); margin-bottom:10px; line-height:1.7; font-size:0.92rem; }
.focus-box { border:var(--border); border-radius:var(--radius-md); padding:14px 18px; background:var(--secondary-background-color); margin-bottom:10px; line-height:1.7; }
.focus-label { font-size:10px; text-transform:uppercase; letter-spacing:0.12em; opacity:0.55; font-weight:400; margin-bottom:5px; }
.focus-value { font-size:0.95rem; font-weight:400; line-height:1.65; }
.trend-row { display:flex; align-items:center; gap:8px; margin-bottom:6px; font-size:13px; }
.trend-date { opacity:0.55; min-width:80px; }
.trend-bar-wrap { flex:1; height:3px; border-radius:999px; background:rgba(0,0,0,0.07); overflow:hidden; }
.trend-bar-fill { height:100%; border-radius:999px; background:var(--accent); }
.trend-score { min-width:40px; text-align:right; font-weight:500; opacity:0.80; }
.streak-pill { display:inline-flex; align-items:center; gap:6px; padding:5px 13px; border-radius:999px; border:var(--border); font-size:13px; font-weight:400; background:var(--secondary-background-color); margin-right:8px; margin-bottom:4px; }
div[data-testid="stForm"] { border:none !important; padding:0 !important; background:transparent !important; }
div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input {
    border-radius:12px !important; font-family:Georgia,serif !important;
}
div.stButton > button {
    border-radius:12px !important; border:1px solid rgba(0,0,0,0.14) !important;
    padding:0.45rem 0.95rem !important; font-weight:400 !important;
    font-family:Georgia,serif !important;
    background:var(--secondary-background-color) !important; color:inherit !important;
}
div.stButton > button:hover { border-color:var(--accent) !important; }
div[data-testid="stSelectbox"] { margin-top:-6px; }
</style>
""", unsafe_allow_html=True)
```

- [ ] **Step 2: Visual verification**

Open the Dashboard page and check:
- Cards use the parchment background set by config.toml, cards slightly darker beige
- Rule banner text is lighter weight (not bold)
- Metric values use font-weight 500 (not 800)
- Trend bars are thin (3px)
- Section titles are medium weight (not heavy)

- [ ] **Step 3: Commit**

```bash
git add pages/dashboard.py
git commit -m "style: zen redesign for dashboard page"
```

---

## Task 4: Update `pages/finance.py` style block

**Files:**
- Modify: `pages/finance.py` lines 256–393

- [ ] **Step 1: Replace the `<style>` block**

Find the block starting at line 256:
```python
st.markdown(
    """
    <style>
    :root {
        --um-radius-lg: 18px;
```
...ending at the closing `""",` (around line 393).

Replace it entirely with:

```python
st.markdown(
    """
    <style>
    :root {
        --um-radius-lg: 18px;
        --um-radius-md: 12px;
        --border: 1px solid rgba(0,0,0,0.07);
        --shadow: 0 1px 3px rgba(0,0,0,0.04);
        --accent: #8a7055;
        --pos: #5a9a6a; --neg: #b87070;
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --accent: #b08a65;
            --border: 1px solid rgba(255,255,255,0.07);
            --shadow: 0 1px 3px rgba(0,0,0,0.12);
            --pos: #7ab88a;
        }
    }
    html, body, [class*="css"] { font-family: Georgia, 'Times New Roman', serif !important; }

    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 4rem !important;
    }

    h1, h2, h3 {
        margin-bottom: 0.35rem !important;
        font-weight: 500 !important;
    }

    .page-subtitle {
        font-size: 16px;
        line-height: 1.7;
        opacity: 0.65;
        margin-bottom: 0.6rem;
    }

    .summary-row {
        display: flex;
        gap: 14px;
        flex-wrap: wrap;
        margin: 0.6rem 0 1.4rem 0;
    }

    .summary-card {
        flex: 1 1 210px;
        min-width: 210px;
        border: var(--border);
        border-radius: 18px;
        padding: 18px 22px;
        background: var(--secondary-background-color);
        box-shadow: var(--shadow);
    }

    .summary-label {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 400;
        opacity: 0.55;
        margin-bottom: 8px;
    }

    .summary-value {
        font-size: 24px;
        font-weight: 500;
        line-height: 1.2;
    }

    .section-card {
        border: var(--border);
        border-radius: 18px;
        padding: 24px 28px;
        background: var(--secondary-background-color);
        box-shadow: var(--shadow);
        margin-bottom: 18px;
    }

    .tight-top { margin-top: -6px; }

    .small-note {
        font-size: 13px;
        opacity: 0.65;
        margin-top: -2px;
        margin-bottom: 12px;
    }

    .record-card {
        border: var(--border);
        border-radius: 12px;
        padding: 14px 18px;
        background: var(--secondary-background-color);
        margin-bottom: 10px;
    }

    .record-title {
        font-size: 15px;
        font-weight: 500;
        margin-bottom: 4px;
    }

    .record-sub {
        font-size: 13px;
        opacity: 0.65;
    }

    .pill {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: var(--secondary-background-color);
        border: var(--border);
        font-size: 13px;
        margin-right: 8px;
        margin-bottom: 8px;
    }

    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }

    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextInput"] input {
        border-radius: 12px !important;
        font-family: Georgia, serif !important;
    }

    div.stButton > button {
        border-radius: 12px !important;
        border: 1px solid rgba(0,0,0,0.14) !important;
        padding: 0.45rem 0.95rem !important;
        font-weight: 400 !important;
        font-family: Georgia, serif !important;
        background: var(--secondary-background-color) !important;
        color: inherit !important;
    }

    div.stButton > button:hover {
        border-color: var(--accent) !important;
    }

    div[data-testid="stSelectbox"] { margin-top: -6px; }
    </style>
    """,
    unsafe_allow_html=True,
)
```

- [ ] **Step 2: Visual verification**

Open the Finance page and check:
- Headings (`h1`, `h2`, `h3`) use medium weight — not heavy
- Summary cards have parchment background, good breathing room
- Section labels are small, light, uppercase

- [ ] **Step 3: Commit**

```bash
git add pages/finance.py
git commit -m "style: zen redesign for finance page"
```

---

## Task 5: Update `pages/driving.py` style block

**Files:**
- Modify: `pages/driving.py` lines 8–39

- [ ] **Step 1: Replace the `<style>` block**

Find the block starting at line 8:
```python
st.markdown("""
<style>
:root {
    --accent: #a08060;
```
...ending at line 40 (`""", unsafe_allow_html=True)`).

Replace it entirely with:

```python
st.markdown("""
<style>
:root {
    --accent: #8a7055;
    --pos: #5a9a6a; --neg: #b87070;
    --border: 1px solid rgba(0,0,0,0.07);
    --shadow: 0 1px 3px rgba(0,0,0,0.04);
    --radius: 18px;
}
@media (prefers-color-scheme: dark) {
    :root {
        --accent: #b08a65;
        --border: 1px solid rgba(255,255,255,0.07);
        --shadow: 0 1px 3px rgba(0,0,0,0.12);
        --pos: #7ab88a;
    }
}
html, body, [class*="css"] { font-family: Georgia, 'Times New Roman', serif !important; }
.block-container {
    max-width: 1200px;
    padding-top: 4rem !important;
    padding-bottom: 4rem !important;
}
div[data-testid="stForm"] {
    border: none !important; padding: 0 !important; background: transparent !important;
}
div[data-testid="stTextInput"] input {
    border-radius: 12px !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
    font-family: Georgia, serif !important;
}
div.stButton > button {
    border-radius: 12px !important;
    border: 1px solid rgba(0,0,0,0.14) !important;
    font-weight: 400 !important;
    font-family: Georgia, serif !important;
    background: var(--secondary-background-color) !important;
    color: inherit !important;
}
div.stButton > button:hover {
    border-color: var(--accent) !important;
}
</style>
""", unsafe_allow_html=True)
```

- [ ] **Step 2: Visual verification**

Open the Driving page and check:
- Page uses Georgia font
- Background is parchment (set by config.toml)
- Buttons are light weight, no bounce on hover

- [ ] **Step 3: Commit**

```bash
git add pages/driving.py
git commit -m "style: zen redesign for driving page"
```

---

## Task 6: Update `pages/excercise.py` style block

**Files:**
- Modify: `pages/excercise.py` lines 130–277

- [ ] **Step 1: Replace the `<style>` block**

Find the block starting at line 130:
```python
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1250px;
```
...ending at the closing `""",` (around line 277).

Replace it entirely with:

```python
st.markdown(
    """
    <style>
    :root {
        --accent: #8a7055;
        --pos: #5a9a6a; --neg: #b87070;
        --border: 1px solid rgba(0,0,0,0.07);
        --shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --accent: #b08a65;
            --border: 1px solid rgba(255,255,255,0.07);
            --shadow: 0 1px 3px rgba(0,0,0,0.12);
            --pos: #7ab88a;
        }
    }
    html, body, [class*="css"] { font-family: Georgia, 'Times New Roman', serif !important; }

    .block-container {
        max-width: 1200px;
        padding-top: 4rem !important;
        padding-bottom: 4rem !important;
    }

    .page-subtitle {
        font-size: 1rem;
        opacity: 0.60;
        margin-top: -4px;
        margin-bottom: 1.4rem;
    }

    .hero-banner {
        border: var(--border);
        border-radius: 18px;
        padding: 22px 28px;
        background: var(--secondary-background-color);
        box-shadow: var(--shadow);
        margin-bottom: 18px;
    }

    .hero-label {
        font-size: 10px;
        opacity: 0.55;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-weight: 400;
        margin-bottom: 8px;
    }

    .hero-value {
        font-size: 1.3rem;
        font-weight: 500;
        line-height: 1.5;
    }

    .metric-card {
        border: var(--border);
        border-radius: 18px;
        padding: 22px;
        background: var(--secondary-background-color);
        box-shadow: var(--shadow);
        min-height: 150px;
    }

    .metric-head {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
    }

    .metric-label {
        font-size: 10px;
        opacity: 0.55;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 400;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 500;
        line-height: 1.1;
        margin-bottom: 6px;
        letter-spacing: -0.02em;
        color: var(--accent);
    }

    .metric-sub {
        font-size: 13px;
        opacity: 0.65;
        line-height: 1.6;
    }

    .metric-icon {
        font-size: 1.45rem;
        opacity: 0.70;
    }

    .section-card {
        border: var(--border);
        border-radius: 18px;
        padding: 24px 28px;
        background: var(--secondary-background-color);
        box-shadow: var(--shadow);
        height: 100%;
    }

    .section-title {
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 1rem;
        letter-spacing: -0.01em;
    }

    .small-note {
        font-size: 0.90rem;
        opacity: 0.65;
        line-height: 1.6;
    }

    .success-box {
        padding: 12px 16px;
        border-radius: 12px;
        background: rgba(90,154,106,0.08);
        border: 1px solid rgba(90,154,106,0.20);
        margin-top: 10px;
        margin-bottom: 8px;
        font-weight: 400;
    }

    .warning-box {
        padding: 12px 16px;
        border-radius: 12px;
        background: rgba(200,160,80,0.08);
        border: 1px solid rgba(200,160,80,0.18);
        margin-top: 10px;
        margin-bottom: 8px;
        font-weight: 400;
    }

    div.stButton > button {
        border-radius: 12px !important;
        border: 1px solid rgba(0,0,0,0.14) !important;
        font-weight: 400 !important;
        font-family: Georgia, serif !important;
        background: var(--secondary-background-color) !important;
        color: inherit !important;
    }
    div.stButton > button:hover {
        border-color: var(--accent) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
```

- [ ] **Step 2: Visual verification**

Open the Exercise page and check:
- Metric values use medium weight (not heavy)
- Metric labels are small, light, uppercase
- Cards have comfortable padding
- Section titles are medium weight

- [ ] **Step 3: Commit**

```bash
git add pages/excercise.py
git commit -m "style: zen redesign for exercise page"
```

---

## Task 7: Final cross-page check

- [ ] **Step 1: Smoke test all pages**

Run the app and open each of the 5 pages in order. For each, verify:
1. Background is warm parchment (not grey/white)
2. Font is Georgia serif (clearly visible in headings and body text)
3. No heavy-weight (900) fonts — everything looks calm, not bold
4. Progress bars are thin (3px hairlines)
5. Buttons don't animate upward on hover
6. No accent-colored bar running across the top of the score card

- [ ] **Step 2: Toggle dark mode**

In Streamlit settings (hamburger menu → Settings → Theme → Dark), switch to dark. Verify:
- Background becomes dark walnut (not Streamlit default blue-grey) — **note:** if OS dark mode is off, `prefers-color-scheme: dark` won't fire; use the OS toggle or browser devtools to simulate.
- Accent lightens to `#b08a65`
- Text remains readable

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "style: complete zen redesign across all pages"
```
