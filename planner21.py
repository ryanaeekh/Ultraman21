import os
from datetime import date, timedelta

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Mission 21", page_icon="\U0001f3af", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header, metric_card, status_badge, progress_bar, ACCENT, POS, NEG

inject_theme()
nav_menu("Mission 21")

# =========================================================
# FILE PATHS
# =========================================================
DATA_FOLDER = "data"
PLANNER_FILE = os.path.join(DATA_FOLDER, "planner.csv")
SETTINGS_FILE = os.path.join(DATA_FOLDER, "settings.csv")

os.makedirs(DATA_FOLDER, exist_ok=True)

BACKUP_FOLDER = os.path.join(DATA_FOLDER, "backups")
os.makedirs(BACKUP_FOLDER, exist_ok=True)

def backup_csv(filepath):
    """Create a timestamped backup before writing."""
    if os.path.exists(filepath):
        from datetime import datetime as dt_cls
        import shutil, glob
        basename = os.path.basename(filepath).replace(".csv", "")
        stamp = dt_cls.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(filepath, os.path.join(BACKUP_FOLDER, f"{basename}_{stamp}.csv"))
        for old in sorted(glob.glob(os.path.join(BACKUP_FOLDER, f"{basename}_*.csv")))[:-20]:
            os.remove(old)

# =========================================================
# REQUIRED COLUMNS
# =========================================================
PLANNER_COLS = [
    "date", "priority_1", "priority_2", "priority_3",
    "focus_done", "run_done", "income_done", "reflection", "score",
]
SETTINGS_COLS = ["long_term_goals", "daily_income_target", "hourly_rate_target", "daily_budget", "monthly_budget", "checklist_items", "expense_categories"]

# =========================================================
# FILE SETUP
# =========================================================
if not os.path.exists(PLANNER_FILE):
    pd.DataFrame(columns=PLANNER_COLS).to_csv(PLANNER_FILE, index=False)

if not os.path.exists(SETTINGS_FILE):
    pd.DataFrame([{"long_term_goals": "", "daily_income_target": 250, "hourly_rate_target": 30, "daily_budget": 50, "monthly_budget": 1500, "checklist_items": "Wake on time,Read 10 pages,Meditate", "expense_categories": "Food,Transport,Bills,Shopping,Health,Family,Other"}]).to_csv(SETTINGS_FILE, index=False)

EXERCISE_FILE = os.path.join(DATA_FOLDER, "exercise.csv")
EXERCISE_COLS = ["date", "status", "type", "duration", "km", "pace", "notes"]
if not os.path.exists(EXERCISE_FILE):
    pd.DataFrame(columns=EXERCISE_COLS).to_csv(EXERCISE_FILE, index=False)

JOURNAL_FILE = os.path.join(DATA_FOLDER, "journal.csv")
JOURNAL_COLS = ["date", "entry"]
if not os.path.exists(JOURNAL_FILE):
    pd.DataFrame(columns=JOURNAL_COLS).to_csv(JOURNAL_FILE, index=False)


def _ensure_columns(path, required_cols, default_row=None):
    df = pd.read_csv(path)
    if list(df.columns) != required_cols:
        df = pd.DataFrame([default_row] if default_row else [], columns=required_cols)
        df.to_csv(path, index=False)
    return df


_ensure_columns(PLANNER_FILE, PLANNER_COLS)
_ensure_columns(SETTINGS_FILE, SETTINGS_COLS, {"long_term_goals": "", "daily_income_target": 250, "hourly_rate_target": 30, "daily_budget": 50, "monthly_budget": 1500, "checklist_items": "Wake on time,Read 10 pages,Meditate", "expense_categories": "Food,Transport,Bills,Shopping,Health,Family,Other"})

today = str(date.today())

# =========================================================
# DATA HELPERS  (cached -- invalidated after writes)
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
    backup_csv(PLANNER_FILE)
    df.to_csv(PLANNER_FILE, index=False)
    invalidate_cache()


def save_settings(df: pd.DataFrame):
    backup_csv(SETTINGS_FILE)
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
        return "\U0001f7e2 Fully Completed"
    elif score >= 70:
        return "\U0001f7e1 Strong Progress"
    elif score >= 40:
        return "\U0001f7e0 In Progress"
    else:
        return "\U0001f534 Not Started"


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


def compute_habit_streak(df, habit_col):
    """Return current consecutive-day streak where habit_col is True."""
    if df.empty or habit_col not in df.columns:
        return 0
    completed = set(df[df[habit_col] == True]["date"].astype(str).tolist())
    streak, check = 0, date.today()
    while str(check) in completed:
        streak += 1
        check -= timedelta(days=1)
    return streak


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
# PAGE: TODAY
# =========================================================
st.markdown(page_header("Today", f"{today} \u2014 build the day deliberately"), unsafe_allow_html=True)

# --- Score ring ---
st.markdown(f'''<div style="text-align:center;margin:20px 0;">
    <div class="score-ring" style="--pct:{today_score};">
        <span class="score-ring-value">{today_score}</span>
    </div>
    <div class="metric-sub">{get_execution_label(today_score)}</div>
</div>''', unsafe_allow_html=True)

# --- Execution pills ---
row = get_row(planner_df, today)
focus = row.get("focus_done", False) if row is not None else False
run = row.get("run_done", False) if row is not None else False
income = row.get("income_done", False) if row is not None else False

pills_html = '<div class="exec-pills">'
for label, done in [("Priorities", focus), ("Run", run), ("Income", income)]:
    cls = "done" if done else "pending"
    pills_html += f'<span class="exec-pill {cls}">{label}</span>'
pills_html += '</div>'
st.markdown(pills_html, unsafe_allow_html=True)

# --- Long-term goals ---
if saved_goals:
    st.markdown(f'''<div class="card accent-left-card" style="margin-top:20px;">
    <div class="section-title">\U0001f3af Long Term Goals</div>
    <div style="white-space:pre-wrap;font-size:15px;line-height:1.85;color:var(--text);opacity:0.90;">{saved_goals}</div>
</div>''', unsafe_allow_html=True)
else:
    st.markdown('''<div class="card" style="margin-top:20px;">
    <div class="section-title">\U0001f3af Long Term Goals</div>
    <div style="opacity:0.5;font-size:14px;line-height:1.6;color:var(--text2);">No goals set yet \u2014 go to Settings to add them.</div>
</div>''', unsafe_allow_html=True)

# --- Morning checklist ---
checklist_raw = ""
if not settings_df.empty and "checklist_items" in settings_df.columns:
    checklist_raw = str(settings_df.loc[0, "checklist_items"]).strip()
    if checklist_raw.lower() == "nan":
        checklist_raw = ""
if checklist_raw:
    items = [i.strip() for i in checklist_raw.split(",") if i.strip()]
    if items:
        st.markdown('<div class="section-title">\u2611\ufe0f Morning Checklist</div>', unsafe_allow_html=True)
        done_count = 0
        for item in items:
            key = f"checklist_{item}"
            if key not in st.session_state:
                st.session_state[key] = False
            checked = st.checkbox(item, value=st.session_state[key], key=key)
            if checked:
                done_count += 1
        st.caption(f"{done_count}/{len(items)} completed")

# --- Daily entry form ---
_p1 = clean_text(today_row["priority_1"]) if today_row is not None else ""
_p2 = clean_text(today_row["priority_2"]) if today_row is not None else ""
_p3 = clean_text(today_row["priority_3"]) if today_row is not None else ""
_refl = clean_text(today_row["reflection"]) if today_row is not None else ""
_focus = bool(today_row["focus_done"]) if today_row is not None else False
_run = bool(today_row["run_done"]) if today_row is not None else False
_income = bool(today_row["income_done"]) if today_row is not None else False

st.markdown('<div class="section-title">\U0001f4dd Daily Entry</div>', unsafe_allow_html=True)


def _auto_save():
    """Save the daily entry from session state."""
    p1 = st.session_state.get("entry_p1", "")
    p2 = st.session_state.get("entry_p2", "")
    p3 = st.session_state.get("entry_p3", "")
    chk_focus = st.session_state.get("entry_focus", False)
    chk_run = st.session_state.get("entry_run", False)
    chk_income = st.session_state.get("entry_income", False)
    refl = st.session_state.get("entry_refl", "")
    new_row = {
        "date": today,
        "priority_1": p1,
        "priority_2": p2,
        "priority_3": p3,
        "focus_done": chk_focus,
        "run_done": chk_run,
        "income_done": chk_income,
        "reflection": refl,
        "score": calculate_score(chk_focus, chk_run, chk_income),
    }
    df = load_planner()
    existing = df[df["date"] == today]
    if not existing.empty:
        idx = existing.index[0]
        for k, v in new_row.items():
            df.at[idx, k] = v
    else:
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_planner(df)


p1 = st.text_input("Priority 1", value=_p1, key="entry_p1", on_change=_auto_save)
p2 = st.text_input("Priority 2", value=_p2, key="entry_p2", on_change=_auto_save)
p3 = st.text_input("Priority 3", value=_p3, key="entry_p3", on_change=_auto_save)

col1, col2, col3 = st.columns(3)
with col1:
    chk_focus = st.checkbox("\u2705 All Priorities", value=_focus, key="entry_focus", on_change=_auto_save)
with col2:
    chk_run = st.checkbox("\U0001f3c3 Run", value=_run, key="entry_run", on_change=_auto_save)
with col3:
    chk_income = st.checkbox("\U0001f4b0 Income Target", value=_income, key="entry_income", on_change=_auto_save)

reflection = st.text_area("Reflection", value=_refl, height=120, key="entry_refl", on_change=_auto_save)

_preview = calculate_score(chk_focus, chk_run, chk_income)
st.caption(f"Auto-calculated score: **{_preview}**/100")

# --- Focus quote ---
quote_text = (
    'Because you might as well be dead.<br>'
    'Seriously, if you always put limits on everything you do, physical or anything else,<br>'
    'it\'ll spread over into the rest of your life.<br>'
    'It\'ll spread into your work, into your morality, into your entire being.<br><br>'
    'There are no limits.<br>'
    'There are only plateaus, and you must not stay there, you must go beyond them.<br>'
    'If it kills you, it kills you. A man must constantly exceed his level."'
    '<div style="margin-top:18px;font-size:13px;opacity:0.45;font-style:normal;letter-spacing:0.04em;">\u2014 Bruce Lee</div>'
)
st.markdown(f'''<div class="card accent-left-card" style="text-align:center;padding:20px 28px;">
    <div style="font-family:var(--font-display);font-style:italic;font-size:16px;color:var(--text2);line-height:1.7;">
        {quote_text}
    </div>
</div>''', unsafe_allow_html=True)
