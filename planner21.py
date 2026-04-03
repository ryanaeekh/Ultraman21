import os
from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Planner21", page_icon="⚡", layout="wide")

# =========================================================
# FILE PATHS
# =========================================================
DATA_FOLDER = "data"
PLANNER_FILE = os.path.join(DATA_FOLDER, "planner.csv")
SETTINGS_FILE = os.path.join(DATA_FOLDER, "settings.csv")

os.makedirs(DATA_FOLDER, exist_ok=True)

# =========================================================
# REQUIRED COLUMNS
# =========================================================
PLANNER_COLS = [
    "date", "priority_1", "priority_2", "priority_3",
    "focus_done", "run_done", "income_done", "reflection", "score",
]
SETTINGS_COLS = ["long_term_goals", "daily_income_target", "hourly_rate_target"]

# =========================================================
# FILE SETUP
# =========================================================
if not os.path.exists(PLANNER_FILE):
    pd.DataFrame(columns=PLANNER_COLS).to_csv(PLANNER_FILE, index=False)

if not os.path.exists(SETTINGS_FILE):
    pd.DataFrame([{"long_term_goals": "", "daily_income_target": 250, "hourly_rate_target": 30}]).to_csv(SETTINGS_FILE, index=False)


def _ensure_columns(path, required_cols, default_row=None):
    df = pd.read_csv(path)
    if list(df.columns) != required_cols:
        df = pd.DataFrame([default_row] if default_row else [], columns=required_cols)
        df.to_csv(path, index=False)
    return df


_ensure_columns(PLANNER_FILE, PLANNER_COLS)
_ensure_columns(SETTINGS_FILE, SETTINGS_COLS, {"long_term_goals": "", "daily_income_target": 250, "hourly_rate_target": 30})

today = str(date.today())

# =========================================================
# SESSION STATE
# =========================================================
for key, default in [
    ("page", "Today"),
    ("dark_mode", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# =========================================================
# DATA HELPERS  (cached — invalidated after writes)
# =========================================================
@st.cache_data
def load_planner():
    df = pd.read_csv(PLANNER_FILE)
    if "date" in df.columns:
        df["date"] = df["date"].astype(str)
    for col in ["focus_done", "run_done", "income_done"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda v: str(v).strip().lower() == "true")
    for col in ["score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    return df


@st.cache_data
def load_settings():
    return pd.read_csv(SETTINGS_FILE)


def invalidate_cache():
    load_planner.clear()
    load_settings.clear()


def save_planner(df: pd.DataFrame):
    df.to_csv(PLANNER_FILE, index=False)
    invalidate_cache()


def save_settings(df: pd.DataFrame):
    df.to_csv(SETTINGS_FILE, index=False)
    invalidate_cache()


def clean_text(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def get_row(df, date_str):
    rows = df[df["date"] == date_str]
    return rows.iloc[0] if not rows.empty else None


def calculate_score(focus_done, run_done, income_done):
    return (40 if focus_done else 0) + (20 if run_done else 0) + (40 if income_done else 0)


def get_execution_label(score):
    if score == 100:
        return "🟢 Fully Completed"
    elif score >= 70:
        return "🟡 Strong Progress"
    elif score >= 40:
        return "🟠 In Progress"
    else:
        return "🔴 Not Started"


def compute_streak(df):
    """Return current consecutive-day streak where score > 0."""
    if df.empty:
        return 0
    completed = set(df[df["score"] > 0]["date"].astype(str).tolist())
    streak = 0
    check = date.today()
    while str(check) in completed:
        streak += 1
        check -= timedelta(days=1)
    return streak


def compute_weekly_avg(df):
    if df.empty:
        return 0
    week_ago = str(date.today() - timedelta(days=6))
    week_df = df[df["date"] >= week_ago]
    return round(week_df["score"].mean()) if not week_df.empty else 0


# =========================================================
# STYLING
# =========================================================
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
[data-theme="dark"] {
    --accent: #b08a65;
    --accent-soft: rgba(176,138,101,0.12);
    --border: 1px solid rgba(255,255,255,0.07);
    --shadow: 0 1px 3px rgba(0,0,0,0.12);
    --pos: #7ab88a;
}

.stDecoration { display: none !important; }

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

_dark = st.session_state.get("dark_mode", False)
_bg    = "#0e1117" if _dark else "#f5f0e8"
_sbg   = "#161b22" if _dark else "#ede8de"
_color = "#fafafa" if _dark else "#3a3028"
st.markdown(f"""<style>
.stApp {{ background-color: {_bg} !important; color: {_color} !important; }}
section[data-testid="stSidebar"] > div:first-child {{ background-color: {_sbg} !important; }}
header[data-testid="stHeader"] {{ background-color: {_bg} !important; }}
</style>""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================
planner_df = load_planner()
settings_df = load_settings()
today_row = get_row(planner_df, today)

saved_goals = ""
if not settings_df.empty and "long_term_goals" in settings_df.columns:
    saved_goals = clean_text(settings_df.loc[0, "long_term_goals"])

streak = compute_streak(planner_df)
weekly_avg = compute_weekly_avg(planner_df)
today_score = int(today_row["score"]) if today_row is not None else 0

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown(
        '<div style="font-size:1.35rem;font-weight:500;letter-spacing:-0.02em;'
        'color:#8a7055;margin-bottom:14px">⚡ Mission21</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="mission-quote">'
        '"Let\'s make sure that the man you become 3 years from now looks back and thanks you—<br>'
        'for the sacrifices you made,<br>'
        'the discipline you held,<br>'
        'and the hard decisions you chose today.<br>'
        'He\'s proud of you. Don\'t let him down."'
        '<div class="mission-attrib">— Ryan Aee 01.01.2026</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.toggle("🌙 Dark mode", key="dark_mode")

    page = st.radio(
        "Navigate",
        ["Today", "History", "Insights", "Settings"],
        index=["Today", "History", "Insights", "Settings"].index(st.session_state.page) if st.session_state.page in ["Today", "History", "Insights", "Settings"] else 0,
        label_visibility="collapsed",
    )
    st.session_state.page = page


# =========================================================
# PAGE: TODAY
# =========================================================
if page == "Today":
    st.markdown(
        f'<div class="page-header">'
        f'<div class="page-title">⚡ Today</div>'
        f'<div class="page-sub">{today} — build the day deliberately</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # --- Score card ---
    _focus = bool(today_row["focus_done"]) if today_row is not None else False
    _run = bool(today_row["run_done"]) if today_row is not None else False
    _income = bool(today_row["income_done"]) if today_row is not None else False
    _pct = min(today_score, 100)

    st.markdown(
        f'<div class="score-card">'
        f'<div class="score-label">Today\'s Score</div>'
        f'<div><span class="score-value">{today_score}</span>'
        f'<span class="score-denom">/100</span></div>'
        f'<div class="score-status">{get_execution_label(today_score)}</div>'
        f'<div class="progress-shell"><div class="progress-bar" style="width:{_pct}%"></div></div>'
        f'<div class="exec-checks">'
        f'<span class="exec-check {"done" if _focus else "miss"}">Priorities</span>'
        f'<span class="exec-check {"done" if _run else "miss"}">Run</span>'
        f'<span class="exec-check {"done" if _income else "miss"}">Income</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # --- Long-term goals ---
    if saved_goals:
        st.markdown(
            f'<div class="section-card">'
            f'<div class="section-title">🎯 Long Term Goals</div>'
            f'<div class="goals-display">{saved_goals}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="section-card">'
            '<div class="section-title">🎯 Long Term Goals</div>'
            '<div style="opacity:0.5;font-size:14px;line-height:1.6">'
            'No goals set yet — go to Settings to add them.</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # --- Daily entry form ---
    _p1 = clean_text(today_row["priority_1"]) if today_row is not None else ""
    _p2 = clean_text(today_row["priority_2"]) if today_row is not None else ""
    _p3 = clean_text(today_row["priority_3"]) if today_row is not None else ""
    _refl = clean_text(today_row["reflection"]) if today_row is not None else ""

    st.markdown(
        '<div class="section-card"><div class="section-title">📝 Daily Entry</div></div>',
        unsafe_allow_html=True,
    )

    with st.form("today_form", clear_on_submit=False):
        p1 = st.text_input("Priority 1", value=_p1)
        p2 = st.text_input("Priority 2", value=_p2)
        p3 = st.text_input("Priority 3", value=_p3)

        col1, col2, col3 = st.columns(3)
        with col1:
            chk_focus = st.checkbox("✅ All Priorities", value=_focus)
        with col2:
            chk_run = st.checkbox("🏃 Run", value=_run)
        with col3:
            chk_income = st.checkbox("💰 Income Target", value=_income)

        reflection = st.text_area("Reflection", value=_refl, height=120)

        _preview = calculate_score(chk_focus, chk_run, chk_income)
        st.caption(f"Auto-calculated score: **{_preview}**/100")

        submitted = st.form_submit_button("💾 Save Today")

    if submitted:
        new_row = {
            "date": today,
            "priority_1": p1,
            "priority_2": p2,
            "priority_3": p3,
            "focus_done": chk_focus,
            "run_done": chk_run,
            "income_done": chk_income,
            "reflection": reflection,
            "score": calculate_score(chk_focus, chk_run, chk_income),
        }
        if today_row is not None:
            idx = planner_df[planner_df["date"] == today].index[0]
            for k, v in new_row.items():
                planner_df.at[idx, k] = v
        else:
            planner_df = pd.concat([planner_df, pd.DataFrame([new_row])], ignore_index=True)
        save_planner(planner_df)
        st.rerun()

    # --- Focus quote ---
    st.markdown(
        '<div class="focus-quote-card">'
        '<div class="focus-quote-label">Focus</div>'
        '<div class="focus-quote-text">'
        'Because you might as well be dead.<br>'
        'Seriously, if you always put limits on everything you do, physical or anything else,<br>'
        'it\'ll spread over into the rest of your life.<br>'
        'It\'ll spread into your work, into your morality, into your entire being.<br><br>'
        'There are no limits.<br>'
        'There are only plateaus, and you must not stay there, you must go beyond them.<br>'
        'If it kills you, it kills you. A man must constantly exceed his level."'
        '</div>'
        '<div class="focus-quote-attrib">— Bruce Lee</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# PAGE: HISTORY
# =========================================================
elif page == "History":
    st.markdown(
        '<div class="page-header">'
        '<div class="page-title">📚 History</div>'
        '<div class="page-sub">Every day you logged — reviewed in full</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    planner_df = load_planner()

    if planner_df.empty:
        st.info("No history yet. Start logging your days.")
    else:
        hist = planner_df.sort_values("date", ascending=False).reset_index(drop=True)

        show_only_completed = st.toggle("Show only days with score > 0", value=False)
        if show_only_completed:
            hist = hist[hist["score"] > 0]

        if hist.empty:
            st.info("No matching records.")
        else:
            for _, row in hist.iterrows():
                score = int(row["score"])
                label = get_execution_label(score)
                reflection = clean_text(row["reflection"])
                p1 = clean_text(row["priority_1"])
                p2 = clean_text(row["priority_2"])
                p3 = clean_text(row["priority_3"])

                f_icon = "✅" if row["focus_done"] else "❌"
                r_icon = "✅" if row["run_done"] else "❌"
                i_icon = "✅" if row["income_done"] else "❌"

                reflection_html = (
                    f'<div class="hist-reflection">💬 {reflection}</div>'
                    if reflection else ""
                )

                st.markdown(
                    f'<div class="hist-card">'
                    f'  <div class="hist-header">'
                    f'    <div class="hist-date">{row["date"]}</div>'
                    f'    <div class="hist-bar-wrap"><div class="hist-bar-fill" style="width:{score}%"></div></div>'
                    f'    <div class="hist-score">{score}/100</div>'
                    f'    <div class="hist-label">{label}</div>'
                    f'  </div>'
                    f'  <div class="hist-body">'
                    f'    <div class="hist-col">'
                    f'      <div class="hist-col-title">Priorities</div>'
                    f'      <div class="hist-item">1 · {p1 or "—"}</div>'
                    f'      <div class="hist-item">2 · {p2 or "—"}</div>'
                    f'      <div class="hist-item">3 · {p3 or "—"}</div>'
                    f'    </div>'
                    f'    <div class="hist-col">'
                    f'      <div class="hist-col-title">Execution</div>'
                    f'      <div class="hist-item">{f_icon} All Priorities</div>'
                    f'      <div class="hist-item">{r_icon} Run</div>'
                    f'      <div class="hist-item">{i_icon} Income Target</div>'
                    f'    </div>'
                    f'  </div>'
                    f'  {reflection_html}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                if st.button("🗑️ Delete", key=f"del_{row['date']}"):
                    updated = planner_df[planner_df["date"] != row["date"]]
                    save_planner(updated.reset_index(drop=True))
                    st.rerun()

# =========================================================
# PAGE: INSIGHTS
# =========================================================
elif page == "Insights":
    st.markdown(
        '<div class="page-header">'
        '<div class="page-title">📈 Insights</div>'
        '<div class="page-sub">Patterns, trends, and what the data says about your execution</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    planner_df = load_planner()

    if len(planner_df) < 2:
        st.info("Log at least 2 days to see insights.")
    else:
        total_days   = len(planner_df)
        perfect_days = len(planner_df[planner_df["score"] == 100])
        active_days  = len(planner_df[planner_df["score"] > 0])
        all_time_avg = round(planner_df["score"].mean())
        focus_rate   = round(planner_df["focus_done"].sum() / total_days * 100)
        run_rate     = round(planner_df["run_done"].sum()   / total_days * 100)
        income_rate  = round(planner_df["income_done"].sum()/ total_days * 100)

        # ── Stat cards ──
        st.markdown(
            f'<div class="ins-grid">'
            f'<div class="ins-card"><div class="ins-card-label">Days Logged</div>'
            f'<div class="ins-card-value">{total_days}</div></div>'
            f'<div class="ins-card"><div class="ins-card-label">Perfect Days</div>'
            f'<div class="ins-card-value">{perfect_days}</div></div>'
            f'<div class="ins-card"><div class="ins-card-label">All-Time Avg</div>'
            f'<div class="ins-card-value">{all_time_avg}<span style="font-size:1rem;opacity:.45">/100</span></div></div>'
            f'<div class="ins-card"><div class="ins-card-label">Current Streak</div>'
            f'<div class="ins-card-value">{streak}</div>'
            f'<div class="ins-card-sub">🔥 consecutive days</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Score trend ──
        st.markdown('<div class="section-label">Score over time</div>', unsafe_allow_html=True)
        chart_df = planner_df.sort_values("date")[["date", "score"]].set_index("date")
        st.line_chart(chart_df, height=200)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Habit completion ──
        st.markdown('<div class="section-label">Habit completion rates</div>', unsafe_allow_html=True)
        hc1, hc2, hc3 = st.columns(3, gap="medium")
        for col, name, pct in [
            (hc1, "✅ All Priorities", focus_rate),
            (hc2, "🏃 Run",           run_rate),
            (hc3, "💰 Income Target", income_rate),
        ]:
            with col:
                st.markdown(
                    f'<div class="habit-card">'
                    f'<div class="habit-top"><span class="habit-name">{name}</span>'
                    f'<span class="habit-pct">{pct}%</span></div>'
                    f'<div class="habit-bar-shell">'
                    f'<div class="habit-bar-fill" style="width:{pct}%"></div></div>'
                    f'<div style="font-size:12px;opacity:.5;margin-top:7px">{pct}% of days</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Last 7 days ──
        st.markdown('<div class="section-label">Last 7 days</div>', unsafe_allow_html=True)
        week_ago = str(date.today() - timedelta(days=6))
        week_df  = planner_df[planner_df["date"] >= week_ago].sort_values("date")

        for _, row in week_df.iterrows():
            score = int(row["score"])
            st.markdown(
                f'<div class="week-row">'
                f'<span class="week-date">{row["date"]}</span>'
                f'<div class="week-bar-wrap"><div class="week-bar-fill" style="width:{score}%"></div></div>'
                f'<span class="week-score">{score}/100</span>'
                f'<span class="week-label">{get_execution_label(score)}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

# =========================================================
# PAGE: SETTINGS
# =========================================================
elif page == "Settings":
    st.markdown(
        '<div class="page-header">'
        '<div class="page-title">⚙️ Settings</div>'
        '<div class="page-sub">Goals, data export, and reset</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    settings_df = load_settings()
    saved_goals = clean_text(settings_df.loc[0, "long_term_goals"]) if not settings_df.empty else ""

    s_left, s_right = st.columns([1.1, 0.9], gap="large")

    with s_left:
        st.markdown('<div class="section-label">🎯 Long Term Goals</div>', unsafe_allow_html=True)
        with st.form("settings_goals_form"):
            long_term_goals = st.text_area(
                "Your goals",
                value=saved_goals,
                height=280,
                placeholder="Write the future you are building toward...",
                label_visibility="collapsed",
            )
            if st.form_submit_button("💾 Save Goals", use_container_width=True):
                settings_df.loc[0, "long_term_goals"] = long_term_goals
                save_settings(settings_df)
                st.success("Goals saved.")
                st.rerun()

    with s_right:
        st.markdown('<div class="section-label">📦 Data</div>', unsafe_allow_html=True)
        planner_df = load_planner()
        csv = planner_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Export planner data as CSV",
            data=csv,
            file_name="planner21_export.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">⚠️ Danger Zone</div>', unsafe_allow_html=True)
        confirm = st.text_input("Type DELETE to confirm reset", placeholder="DELETE")
        if st.button("🗑️ Clear all planner data", use_container_width=True):
            if confirm == "DELETE":
                pd.DataFrame(columns=PLANNER_COLS).to_csv(PLANNER_FILE, index=False)
                invalidate_cache()
                st.success("Planner data cleared.")
                st.rerun()
            else:
                st.error("Type DELETE to confirm.")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">🎯 Targets</div>', unsafe_allow_html=True)
        with st.form("targets_form"):
            current_income_target = 250.0
            current_rate_target = 30.0
            if "daily_income_target" in settings_df.columns and not settings_df.empty:
                try: current_income_target = float(settings_df.loc[0, "daily_income_target"])
                except: pass
            if "hourly_rate_target" in settings_df.columns and not settings_df.empty:
                try: current_rate_target = float(settings_df.loc[0, "hourly_rate_target"])
                except: pass
            income_target = st.number_input("Daily Income Target ($)", min_value=0.0, value=current_income_target, step=10.0)
            rate_target = st.number_input("Hourly Rate Target ($/hr)", min_value=0.0, value=current_rate_target, step=5.0)
            if st.form_submit_button("💾 Save Targets", use_container_width=True):
                settings_df.loc[0, "daily_income_target"] = income_target
                settings_df.loc[0, "hourly_rate_target"] = rate_target
                save_settings(settings_df)
                st.success("Targets saved.")
                st.rerun()