# Planner21 Feature Overhaul — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Planner21 genuinely useful for daily life by fixing critical gaps (missing entry form, dead nav), adding configurable targets, a weekly review page, per-habit streaks, budget alerts, morning checklist, data backup, custom expense categories, and a journal page.

**Architecture:** Each feature is a self-contained task modifying 1-3 files. No refactoring of the existing page structure — each page stays as its own file with inline helpers. Settings are stored in `data/settings.csv` (expanding the existing schema). New pages go into `pages/`.

**Tech Stack:** Python, Streamlit, Pandas, CSV persistence

---

## File Map

| File | Changes |
|------|---------|
| `planner21.py` | Task 1 (daily entry form), Task 2 (restore nav), Task 5 (per-habit streaks on Insights), Task 7 (morning checklist) |
| `pages/driving.py` | Task 3 (configurable targets) |
| `pages/finance.py` | Task 6 (budget alerts), Task 9 (custom categories) |
| `pages/weekly_review.py` | Task 4 (new page) |
| `pages/journal.py` | Task 10 (new page) |
| `data/settings.csv` | Task 3 (new columns), Task 6 (budget columns), Task 7 (checklist columns), Task 9 (custom categories column) |

---

### Task 1: Daily Entry Form on Today Page

The Today page (planner21.py:493-535) is read-only. Users cannot log priorities, mark completions, or write reflections. This is the most critical missing feature.

**Files:**
- Modify: `planner21.py:493-535` (Today page section)

- [ ] **Step 1: Add the daily entry form after the focus quote card**

Replace the Today page section (planner21.py lines 493-535) with a version that includes:
- 3 priority text inputs (pre-filled if today's row exists)
- 3 checkboxes: focus_done, run_done, income_done
- Reflection textarea
- Auto-calculated score display
- Save button

```python
if page == "Today":
    st.markdown(
        f'<div class="page-header">'
        f'<div class="page-title">⚡ Today</div>'
        f'<div class="page-sub">{today} — build the day deliberately</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Score card (top) ──
    st.markdown(
        f'<div class="score-card">'
        f'<div class="score-label">Today\'s Score</div>'
        f'<div class="score-value">{today_score}<span class="score-denom">/100</span></div>'
        f'<div class="score-status">{get_execution_label(today_score)}</div>'
        f'<div class="progress-shell"><div class="progress-bar" style="width:{today_score}%"></div></div>'
        f'<div class="exec-checks">'
        f'<span class="exec-check {"done" if today_row is not None and today_row["focus_done"] else "miss"}">{"✓" if today_row is not None and today_row["focus_done"] else "○"} Priorities</span>'
        f'<span class="exec-check {"done" if today_row is not None and today_row["run_done"] else "miss"}">{"✓" if today_row is not None and today_row["run_done"] else "○"} Run</span>'
        f'<span class="exec-check {"done" if today_row is not None and today_row["income_done"] else "miss"}">{"✓" if today_row is not None and today_row["income_done"] else "○"} Income</span>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    if saved_goals:
        st.markdown(
            f'<div class="section-card">'
            f'<div class="section-title">🎯 Long Term Goals</div>'
            f'<div class="goals-display">{saved_goals}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Daily entry form ──
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📝 Log Today</div>', unsafe_allow_html=True)

    with st.form("today_form"):
        p1 = st.text_input("Priority 1", value=clean_text(today_row["priority_1"]) if today_row is not None else "")
        p2 = st.text_input("Priority 2", value=clean_text(today_row["priority_2"]) if today_row is not None else "")
        p3 = st.text_input("Priority 3", value=clean_text(today_row["priority_3"]) if today_row is not None else "")

        st.markdown('<div class="mark-header">Mark completed</div>', unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            focus_done = st.checkbox("✅ All Priorities", value=bool(today_row["focus_done"]) if today_row is not None else False)
        with fc2:
            run_done = st.checkbox("🏃 Run", value=bool(today_row["run_done"]) if today_row is not None else False)
        with fc3:
            income_done = st.checkbox("💰 Income Target", value=bool(today_row["income_done"]) if today_row is not None else False)

        reflection = st.text_area(
            "Reflection",
            value=clean_text(today_row["reflection"]) if today_row is not None else "",
            placeholder="What happened today? What did you learn?",
            height=120,
        )

        score = calculate_score(focus_done, run_done, income_done)
        st.caption(f"Score: {score}/100 — {get_execution_label(score)}")

        if st.form_submit_button("💾 Save Today", use_container_width=True):
            new_data = {
                "date": today,
                "priority_1": p1.strip(),
                "priority_2": p2.strip(),
                "priority_3": p3.strip(),
                "focus_done": focus_done,
                "run_done": run_done,
                "income_done": income_done,
                "reflection": reflection.strip(),
                "score": score,
            }
            planner_df = load_planner()
            if today in planner_df["date"].values:
                for col, val in new_data.items():
                    planner_df.loc[planner_df["date"] == today, col] = val
            else:
                planner_df = pd.concat([planner_df, pd.DataFrame([new_data])], ignore_index=True)
            save_planner(planner_df)
            st.success("Today saved.")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Focus quote (moved below form) ──
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
```

- [ ] **Step 2: Verify the app runs**

Run: `python -m streamlit run planner21.py`
Expected: Today page shows score card + goals + daily entry form + focus quote. Form saves and reloads.

- [ ] **Step 3: Commit**

```bash
git add planner21.py
git commit -m "feat: add daily entry form to Today page"
```

---

### Task 2: Restore History & Insights Navigation

History (line 541) and Insights (line 616) pages exist but are unreachable because the sidebar radio only offers `["Today", "Settings"]`.

**Files:**
- Modify: `planner21.py:481-487` (sidebar radio)

- [ ] **Step 1: Update the sidebar radio to include all 4 pages**

Change planner21.py line 481-487:

```python
    page = st.radio(
        "Navigate",
        ["Today", "History", "Insights", "Settings"],
        index=["Today", "History", "Insights", "Settings"].index(st.session_state.page)
        if st.session_state.page in ["Today", "History", "Insights", "Settings"] else 0,
        label_visibility="collapsed",
    )
    st.session_state.page = page
```

- [ ] **Step 2: Verify all 4 pages are accessible**

Run: `python -m streamlit run planner21.py`
Expected: Sidebar shows Today, History, Insights, Settings. Each page loads without error.

- [ ] **Step 3: Commit**

```bash
git add planner21.py
git commit -m "feat: restore History and Insights pages to sidebar nav"
```

---

### Task 3: Configurable Income Targets

The $250 daily target and $30/hr rate are hardcoded in driving.py. Add settings fields so the user can configure them.

**Files:**
- Modify: `planner21.py` (Settings page, add target inputs)
- Modify: `pages/driving.py:215,264` (read targets from settings)
- Modify: `data/settings.csv` (add columns)

- [ ] **Step 1: Expand settings schema**

In planner21.py, update SETTINGS_COLS (line 25):

```python
SETTINGS_COLS = ["long_term_goals", "daily_income_target", "hourly_rate_target"]
```

Update the default row in file setup (line 34):

```python
if not os.path.exists(SETTINGS_FILE):
    pd.DataFrame([{"long_term_goals": "", "daily_income_target": 250, "hourly_rate_target": 30}]).to_csv(SETTINGS_FILE, index=False)
```

Update `_ensure_columns` call (line 46):

```python
_ensure_columns(SETTINGS_FILE, SETTINGS_COLS, {"long_term_goals": "", "daily_income_target": 250, "hourly_rate_target": 30})
```

- [ ] **Step 2: Add target inputs to the Settings page**

In the Settings page section (planner21.py, inside `s_right` column, after the Data section around line 744), add:

```python
        st.markdown('<div class="section-label">🎯 Targets</div>', unsafe_allow_html=True)
        with st.form("targets_form"):
            current_income_target = float(settings_df.loc[0, "daily_income_target"]) if "daily_income_target" in settings_df.columns and not pd.isna(settings_df.loc[0, "daily_income_target"]) else 250.0
            current_rate_target = float(settings_df.loc[0, "hourly_rate_target"]) if "hourly_rate_target" in settings_df.columns and not pd.isna(settings_df.loc[0, "hourly_rate_target"]) else 30.0

            income_target = st.number_input("Daily Income Target ($)", min_value=0.0, value=current_income_target, step=10.0)
            rate_target = st.number_input("Hourly Rate Target ($/hr)", min_value=0.0, value=current_rate_target, step=5.0)

            if st.form_submit_button("💾 Save Targets", use_container_width=True):
                settings_df.loc[0, "daily_income_target"] = income_target
                settings_df.loc[0, "hourly_rate_target"] = rate_target
                save_settings(settings_df)
                st.success("Targets saved.")
                st.rerun()
```

- [ ] **Step 3: Update driving.py to read targets from settings**

At the top of driving.py (after DATA_FOLDER setup, around line 80), add settings reading:

```python
SETTINGS_FILE = os.path.join(DATA_FOLDER, "settings.csv")
DAILY_TARGET = 250.0
HOURLY_TARGET = 30.0
if os.path.exists(SETTINGS_FILE):
    try:
        _settings = pd.read_csv(SETTINGS_FILE)
        if "daily_income_target" in _settings.columns and not _settings.empty:
            DAILY_TARGET = float(_settings.loc[0, "daily_income_target"])
        if "hourly_rate_target" in _settings.columns and not _settings.empty:
            HOURLY_TARGET = float(_settings.loc[0, "hourly_rate_target"])
    except Exception:
        pass
```

Replace hardcoded `250` on line 215:

```python
target_status = "Target Achieved" if float(earnings) >= DAILY_TARGET else "Below Target"
```

Replace hardcoded `250` on line 262:

```python
st.warning(f"⚠️ Below ${DAILY_TARGET:.0f} Target")
```

Replace hardcoded `30` on line 264:

```python
if float(row["hourly_rate"]) >= HOURLY_TARGET:
    st.success(f"💪 Good hourly rate (≥${HOURLY_TARGET:.0f}/hr)")
else:
    st.warning(f"📉 Hourly rate below ${HOURLY_TARGET:.0f}/hr")
```

- [ ] **Step 4: Verify**

Run app, go to Settings → save new targets → go to Driving → verify new thresholds apply.

- [ ] **Step 5: Commit**

```bash
git add planner21.py pages/driving.py
git commit -m "feat: configurable income and hourly rate targets in Settings"
```

---

### Task 4: Weekly Review Page

New page showing a 7-day summary: total income, expenses, net, avg score, exercise count, best/worst day.

**Files:**
- Create: `pages/weekly_review.py`

- [ ] **Step 1: Create the weekly review page**

```python
import os
import calendar
from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Weekly Review", page_icon="📅", layout="wide")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

PLANNER_FILE  = os.path.join(DATA_DIR, "planner.csv")
DRIVING_FILE  = os.path.join(DATA_DIR, "driving.csv")
FINANCE_FILE  = os.path.join(DATA_DIR, "finance.csv")
MONTHLY_FILE  = os.path.join(DATA_DIR, "monthly_expenses.csv")
EXERCISE_FILE = os.path.join(DATA_DIR, "exercise.csv")


def safe_read(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
        return df if not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def safe_float(v):
    try:
        return 0.0 if pd.isna(v) else float(v)
    except Exception:
        return 0.0


# ── Load data ──
today = date.today()
week_start = today - timedelta(days=6)
date_range = [str(week_start + timedelta(days=i)) for i in range(7)]

planner_df  = safe_read(PLANNER_FILE)
driving_df  = safe_read(DRIVING_FILE)
finance_df  = safe_read(FINANCE_FILE)
monthly_df  = safe_read(MONTHLY_FILE)
exercise_df = safe_read(EXERCISE_FILE)

# Filter to this week
def week_filter(df, col="date"):
    if df.empty or col not in df.columns:
        return pd.DataFrame()
    temp = df.copy()
    temp[col] = temp[col].astype(str)
    return temp[temp[col].isin(date_range)]

w_planner  = week_filter(planner_df)
w_driving  = week_filter(driving_df)
w_finance  = week_filter(finance_df)
w_exercise = week_filter(exercise_df)

# ── Calculations ──
week_income = round(w_driving["earnings"].apply(safe_float).sum(), 2) if not w_driving.empty and "earnings" in w_driving.columns else 0.0
week_variable_exp = round(w_finance["amount"].apply(safe_float).sum(), 2) if not w_finance.empty and "amount" in w_finance.columns else 0.0

days_in_month = calendar.monthrange(today.year, today.month)[1]
daily_fixed = round(monthly_df["amount"].apply(safe_float).sum() / days_in_month, 2) if not monthly_df.empty and "amount" in monthly_df.columns else 0.0
week_fixed = round(daily_fixed * 7, 2)
week_total_exp = round(week_variable_exp + week_fixed, 2)
week_net = round(week_income - week_total_exp, 2)

week_avg_score = 0
best_day = worst_day = None
if not w_planner.empty and "score" in w_planner.columns:
    w_planner["score"] = pd.to_numeric(w_planner["score"], errors="coerce").fillna(0).astype(int)
    week_avg_score = round(w_planner["score"].mean())
    best_idx = w_planner["score"].idxmax()
    worst_idx = w_planner["score"].idxmin()
    best_day = f'{w_planner.loc[best_idx, "date"]} ({w_planner.loc[best_idx, "score"]}/100)'
    worst_day = f'{w_planner.loc[worst_idx, "date"]} ({w_planner.loc[worst_idx, "score"]}/100)'

exercise_count = 0
if not w_exercise.empty and "status" in w_exercise.columns:
    exercise_count = len(w_exercise[w_exercise["status"].astype(str).str.lower().isin(["done", "completed", "yes"])])

days_logged = len(w_planner) if not w_planner.empty else 0

# ── Styling (same zen tokens) ──
st.markdown("""
<style>
:root {
    --accent: #8a7055; --pos: #5a9a6a; --neg: #b87070;
    --border: 1px solid rgba(0,0,0,0.07); --shadow: 0 1px 3px rgba(0,0,0,0.04);
}
@media (prefers-color-scheme: dark) {
    :root { --accent: #b08a65; --border: 1px solid rgba(255,255,255,0.07); --shadow: 0 1px 3px rgba(0,0,0,0.12); --pos: #7ab88a; }
}
[data-theme="dark"] { --accent: #b08a65; --border: 1px solid rgba(255,255,255,0.07); --shadow: 0 1px 3px rgba(0,0,0,0.12); --pos: #7ab88a; }
.stDecoration { display: none !important; }
html, body, [class*="css"] { font-family: Georgia, 'Times New Roman', serif !important; }
.block-container { max-width: 1200px; padding-top: 4rem !important; padding-bottom: 4rem !important; }
.wr-card { border: var(--border); border-radius: 18px; padding: 22px 28px; background: var(--secondary-background-color); box-shadow: var(--shadow); margin-bottom: 14px; }
.wr-label { font-size: 10px; opacity: 0.55; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 400; margin-bottom: 8px; }
.wr-value { font-size: 2rem; font-weight: 500; line-height: 1.1; letter-spacing: -0.02em; }
.wr-sub { font-size: 13px; opacity: 0.65; margin-top: 4px; }
.wr-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(0,0,0,0.05); font-size: 0.93rem; }
.wr-row:last-child { border-bottom: none; }
.wr-key { opacity: 0.65; } .wr-val { font-weight: 500; }
div.stButton > button { border-radius: 12px !important; border: 1px solid rgba(0,0,0,0.14) !important; font-weight: 400 !important; font-family: Georgia, serif !important; background: var(--secondary-background-color) !important; color: inherit !important; }
div.stButton > button:hover { border-color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
_dark = st.session_state["dark_mode"]
_bg = "#0e1117" if _dark else "#f5f0e8"
_sbg = "#161b22" if _dark else "#ede8de"
_color = "#fafafa" if _dark else "#3a3028"
st.markdown(f"""<style>
.stApp {{ background-color: {_bg} !important; color: {_color} !important; }}
section[data-testid="stSidebar"] > div:first-child {{ background-color: {_sbg} !important; }}
header[data-testid="stHeader"] {{ background-color: {_bg} !important; }}
</style>""", unsafe_allow_html=True)

# ── Render ──
st.title("📅 Weekly Review")
st.markdown(f'<div style="opacity:0.6;margin-bottom:1.4rem">{week_start.strftime("%b %d")} – {today.strftime("%b %d, %Y")}</div>', unsafe_allow_html=True)

# Top cards
c1, c2, c3, c4 = st.columns(4, gap="medium")
net_color = "var(--pos)" if week_net >= 0 else "var(--neg)"
with c1:
    st.markdown(f'<div class="wr-card"><div class="wr-label">Week Income</div><div class="wr-value">${week_income:.2f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="wr-card"><div class="wr-label">Week Expenses</div><div class="wr-value">${week_total_exp:.2f}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="wr-card"><div class="wr-label">Week Net</div><div class="wr-value" style="color:{net_color}">${week_net:.2f}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="wr-card"><div class="wr-label">Avg Score</div><div class="wr-value">{week_avg_score}/100</div></div>', unsafe_allow_html=True)

# Detail breakdown
left, right = st.columns([1, 1], gap="large")

with left:
    rows = (
        f'<div class="wr-row"><span class="wr-key">Driving Income</span><span class="wr-val">${week_income:.2f}</span></div>'
        f'<div class="wr-row"><span class="wr-key">Variable Expenses</span><span class="wr-val">${week_variable_exp:.2f}</span></div>'
        f'<div class="wr-row"><span class="wr-key">Fixed Share (7 days)</span><span class="wr-val">${week_fixed:.2f}</span></div>'
        f'<div class="wr-row"><span class="wr-key">Total Expenses</span><span class="wr-val">${week_total_exp:.2f}</span></div>'
        f'<div class="wr-row"><span class="wr-key">Week Net</span><span class="wr-val" style="color:{net_color}">${week_net:.2f}</span></div>'
    )
    st.markdown(f'<div class="wr-card"><div class="wr-label">Financial Breakdown</div>{rows}</div>', unsafe_allow_html=True)

with right:
    rows = (
        f'<div class="wr-row"><span class="wr-key">Days Logged</span><span class="wr-val">{days_logged}/7</span></div>'
        f'<div class="wr-row"><span class="wr-key">Avg Score</span><span class="wr-val">{week_avg_score}/100</span></div>'
        f'<div class="wr-row"><span class="wr-key">Exercise Sessions</span><span class="wr-val">{exercise_count}</span></div>'
        f'<div class="wr-row"><span class="wr-key">Best Day</span><span class="wr-val">{best_day or "—"}</span></div>'
        f'<div class="wr-row"><span class="wr-key">Worst Day</span><span class="wr-val">{worst_day or "—"}</span></div>'
    )
    st.markdown(f'<div class="wr-card"><div class="wr-label">Execution Summary</div>{rows}</div>', unsafe_allow_html=True)

# Daily breakdown table
if not w_planner.empty and "score" in w_planner.columns:
    st.markdown('<div class="wr-card"><div class="wr-label">Day by Day</div>', unsafe_allow_html=True)
    for _, row in w_planner.sort_values("date").iterrows():
        sc = int(row["score"])
        dt = row["date"]
        st.markdown(
            f'<div class="wr-row"><span class="wr-key">{dt}</span><span class="wr-val">{sc}/100</span></div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)
```

- [ ] **Step 2: Verify**

Run app, navigate to Weekly Review in sidebar.

- [ ] **Step 3: Commit**

```bash
git add pages/weekly_review.py
git commit -m "feat: add weekly review page with financial and execution summary"
```

---

### Task 5: Per-Habit Streaks on Insights Page

Currently only overall streak (score > 0) exists. Add individual streaks for focus, run, and income on the Insights page.

**Files:**
- Modify: `planner21.py:616-699` (Insights page)

- [ ] **Step 1: Add per-habit streak calculation**

Add this function after `compute_weekly_avg` (around line 143):

```python
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
```

- [ ] **Step 2: Add streak display to the Insights stat cards**

In the Insights page (around line 638), after computing `income_rate`, add:

```python
        focus_streak  = compute_habit_streak(planner_df, "focus_done")
        run_streak    = compute_habit_streak(planner_df, "run_done")
        income_streak = compute_habit_streak(planner_df, "income_done")
```

Then after the habit completion bars section (around line 680), add:

```python
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Current habit streaks</div>', unsafe_allow_html=True)
        hs1, hs2, hs3 = st.columns(3, gap="medium")
        for col, name, streak_val in [
            (hs1, "✅ Priorities", focus_streak),
            (hs2, "🏃 Run",       run_streak),
            (hs3, "💰 Income",    income_streak),
        ]:
            with col:
                st.markdown(
                    f'<div class="ins-card">'
                    f'<div class="ins-card-label">{name} Streak</div>'
                    f'<div class="ins-card-value">{streak_val}</div>'
                    f'<div class="ins-card-sub">🔥 consecutive days</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
```

- [ ] **Step 3: Verify and commit**

```bash
git add planner21.py
git commit -m "feat: add per-habit streaks to Insights page"
```

---

### Task 6: Expense Budget Alerts

Add daily/monthly spending limits in Settings. Show warnings on the finance page when approaching or over budget.

**Files:**
- Modify: `planner21.py` (Settings page — add budget inputs)
- Modify: `pages/finance.py` (show budget warnings)

- [ ] **Step 1: Expand settings schema for budgets**

In planner21.py, update SETTINGS_COLS:

```python
SETTINGS_COLS = ["long_term_goals", "daily_income_target", "hourly_rate_target", "daily_budget", "monthly_budget"]
```

Update default row:

```python
{"long_term_goals": "", "daily_income_target": 250, "hourly_rate_target": 30, "daily_budget": 50, "monthly_budget": 1500}
```

- [ ] **Step 2: Add budget inputs to Settings page**

Add below the targets form in the Settings page:

```python
        st.markdown('<div class="section-label">💸 Budget Limits</div>', unsafe_allow_html=True)
        with st.form("budget_form"):
            current_daily_budget = float(settings_df.loc[0, "daily_budget"]) if "daily_budget" in settings_df.columns and not pd.isna(settings_df.loc[0, "daily_budget"]) else 50.0
            current_monthly_budget = float(settings_df.loc[0, "monthly_budget"]) if "monthly_budget" in settings_df.columns and not pd.isna(settings_df.loc[0, "monthly_budget"]) else 1500.0

            daily_budget = st.number_input("Daily Spending Limit ($)", min_value=0.0, value=current_daily_budget, step=5.0)
            monthly_budget = st.number_input("Monthly Spending Limit ($)", min_value=0.0, value=current_monthly_budget, step=50.0)

            if st.form_submit_button("💾 Save Budgets", use_container_width=True):
                settings_df.loc[0, "daily_budget"] = daily_budget
                settings_df.loc[0, "monthly_budget"] = monthly_budget
                save_settings(settings_df)
                st.success("Budgets saved.")
                st.rerun()
```

- [ ] **Step 3: Read budgets in finance.py and display alerts**

At the top of finance.py (after DATA_DIR setup), read settings:

```python
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.csv")
DAILY_BUDGET = 50.0
MONTHLY_BUDGET = 1500.0
if os.path.exists(SETTINGS_FILE):
    try:
        _settings = pd.read_csv(SETTINGS_FILE)
        if "daily_budget" in _settings.columns and not _settings.empty:
            DAILY_BUDGET = float(_settings.loc[0, "daily_budget"])
        if "monthly_budget" in _settings.columns and not _settings.empty:
            MONTHLY_BUDGET = float(_settings.loc[0, "monthly_budget"])
    except Exception:
        pass
```

After the top summary cards section (around line 496), add budget alerts:

```python
# Budget alerts
daily_spent = summary["variable_expenses"]
monthly_var_spent = 0.0
if not finance_df.empty:
    temp = finance_df.copy()
    temp["date"] = pd.to_datetime(temp["date"], errors="coerce")
    temp = temp.dropna(subset=["date"])
    dt = pd.to_datetime(selected_date_str)
    mask = (temp["date"].dt.year == dt.year) & (temp["date"].dt.month == dt.month)
    monthly_var_spent = round(temp.loc[mask, "amount"].apply(safe_float).sum(), 2)

if daily_spent > DAILY_BUDGET:
    st.error(f"⚠️ Over daily budget! Spent ${daily_spent:.2f} / ${DAILY_BUDGET:.2f} limit")
elif daily_spent >= DAILY_BUDGET * 0.8:
    st.warning(f"⚡ Approaching daily budget: ${daily_spent:.2f} / ${DAILY_BUDGET:.2f}")

if monthly_var_spent > MONTHLY_BUDGET:
    st.error(f"⚠️ Over monthly budget! Spent ${monthly_var_spent:.2f} / ${MONTHLY_BUDGET:.2f} limit")
elif monthly_var_spent >= MONTHLY_BUDGET * 0.8:
    st.warning(f"⚡ Approaching monthly budget: ${monthly_var_spent:.2f} / ${MONTHLY_BUDGET:.2f}")
```

- [ ] **Step 4: Verify and commit**

```bash
git add planner21.py pages/finance.py
git commit -m "feat: add budget alerts with configurable daily/monthly limits"
```

---

### Task 7: Morning Routine Checklist

Add a configurable daily checklist (e.g., wake on time, read, meditate) that contributes bonus points visible on the Today page.

**Files:**
- Modify: `planner21.py` (Settings: checklist config; Today: checklist display)
- Modify: `data/settings.csv` (new column)

- [ ] **Step 1: Add checklist_items to settings schema**

Update SETTINGS_COLS:

```python
SETTINGS_COLS = ["long_term_goals", "daily_income_target", "hourly_rate_target", "daily_budget", "monthly_budget", "checklist_items"]
```

Default: `"checklist_items": "Wake on time,Read 10 pages,Meditate"`

- [ ] **Step 2: Add checklist editor to Settings page**

```python
        st.markdown('<div class="section-label">☑️ Morning Checklist</div>', unsafe_allow_html=True)
        current_checklist = clean_text(settings_df.loc[0, "checklist_items"]) if "checklist_items" in settings_df.columns else "Wake on time,Read 10 pages,Meditate"
        with st.form("checklist_form"):
            checklist_input = st.text_area(
                "Checklist items (comma-separated)",
                value=current_checklist,
                placeholder="Wake on time, Read 10 pages, Meditate",
                height=80,
            )
            if st.form_submit_button("💾 Save Checklist", use_container_width=True):
                settings_df.loc[0, "checklist_items"] = checklist_input.strip()
                save_settings(settings_df)
                st.success("Checklist saved.")
                st.rerun()
```

- [ ] **Step 3: Display interactive checklist on Today page**

On the Today page, before the daily entry form, add:

```python
    # ── Morning checklist ──
    checklist_raw = ""
    if not settings_df.empty and "checklist_items" in settings_df.columns:
        checklist_raw = clean_text(settings_df.loc[0, "checklist_items"])
    if checklist_raw:
        items = [i.strip() for i in checklist_raw.split(",") if i.strip()]
        if items:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">☑️ Morning Checklist</div>', unsafe_allow_html=True)
            done_count = 0
            for item in items:
                key = f"checklist_{item}"
                if key not in st.session_state:
                    st.session_state[key] = False
                checked = st.checkbox(item, value=st.session_state[key], key=key)
                if checked:
                    done_count += 1
            st.caption(f"{done_count}/{len(items)} completed")
            st.markdown('</div>', unsafe_allow_html=True)
```

Note: Checklist state resets per session (not persisted to CSV). This is intentional — it's a daily reset.

- [ ] **Step 4: Verify and commit**

```bash
git add planner21.py
git commit -m "feat: add configurable morning checklist to Today page"
```

---

### Task 8: Data Backup on Save

Auto-backup CSVs before writing. Each save creates a timestamped copy in `data/backups/`.

**Files:**
- Modify: `planner21.py` (add backup function, call before saves)
- Modify: `pages/finance.py` (call backup before saves)
- Modify: `pages/driving.py` (call backup before saves)
- Modify: `pages/excercise.py` (call backup before saves)

- [ ] **Step 1: Add backup utility to planner21.py**

After DATA_FOLDER setup (line 16), add:

```python
BACKUP_FOLDER = os.path.join(DATA_FOLDER, "backups")
os.makedirs(BACKUP_FOLDER, exist_ok=True)

def backup_csv(filepath):
    """Create a timestamped backup before writing."""
    if os.path.exists(filepath):
        from datetime import datetime as dt_cls
        basename = os.path.basename(filepath).replace(".csv", "")
        stamp = dt_cls.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_FOLDER, f"{basename}_{stamp}.csv")
        import shutil
        shutil.copy2(filepath, backup_path)
        # Keep only last 20 backups per file
        import glob
        pattern = os.path.join(BACKUP_FOLDER, f"{basename}_*.csv")
        backups = sorted(glob.glob(pattern))
        for old in backups[:-20]:
            os.remove(old)
```

Update `save_planner` and `save_settings`:

```python
def save_planner(df: pd.DataFrame):
    backup_csv(PLANNER_FILE)
    df.to_csv(PLANNER_FILE, index=False)
    invalidate_cache()

def save_settings(df: pd.DataFrame):
    backup_csv(SETTINGS_FILE)
    df.to_csv(SETTINGS_FILE, index=False)
    invalidate_cache()
```

- [ ] **Step 2: Add backup to finance.py save functions**

At top of finance.py (after DATA_DIR), add:

```python
BACKUP_FOLDER = os.path.join(DATA_DIR, "backups")
os.makedirs(BACKUP_FOLDER, exist_ok=True)

def backup_csv(filepath):
    if os.path.exists(filepath):
        from datetime import datetime as dt_cls
        import shutil, glob
        basename = os.path.basename(filepath).replace(".csv", "")
        stamp = dt_cls.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(filepath, os.path.join(BACKUP_FOLDER, f"{basename}_{stamp}.csv"))
        for old in sorted(glob.glob(os.path.join(BACKUP_FOLDER, f"{basename}_*.csv")))[:-20]:
            os.remove(old)
```

Update `save_finance` and `save_monthly`:

```python
def save_finance(df):
    backup_csv(FINANCE_FILE)
    df.to_csv(FINANCE_FILE, index=False)

def save_monthly(df):
    backup_csv(MONTHLY_FILE)
    df.to_csv(MONTHLY_FILE, index=False)
```

- [ ] **Step 3: Add backup to driving.py**

Add the same backup_csv function after DATA_FOLDER setup. Then wrap every `driving_df.to_csv(DRIVING_FILE, ...)` call with `backup_csv(DRIVING_FILE)` before it. There are 2 places: line 195 (off day) and line 231 (driving day).

- [ ] **Step 4: Add backup to excercise.py**

Add the same backup_csv function after DATA_DIR setup. Update `save_exercise_df`:

```python
def save_exercise_df(df):
    backup_csv(EXERCISE_FILE)
    df = ensure_columns(df, EXERCISE_COLUMNS)
    df.to_csv(EXERCISE_FILE, index=False)
```

- [ ] **Step 5: Add import button to Settings page**

In planner21.py Settings page, add a restore section:

```python
        st.markdown('<div class="section-label">🔄 Restore from Backup</div>', unsafe_allow_html=True)
        backup_dir = os.path.join(DATA_FOLDER, "backups")
        if os.path.exists(backup_dir):
            backups = sorted([f for f in os.listdir(backup_dir) if f.endswith(".csv")], reverse=True)
            if backups:
                selected_backup = st.selectbox("Select backup", backups[:20])
                if st.button("Restore selected backup"):
                    import shutil
                    # Determine which file this backup belongs to
                    for prefix in ["planner", "settings", "driving", "finance", "monthly_expenses", "exercise"]:
                        if selected_backup.startswith(prefix):
                            target = os.path.join(DATA_FOLDER, f"{prefix}.csv")
                            shutil.copy2(os.path.join(backup_dir, selected_backup), target)
                            invalidate_cache()
                            st.success(f"Restored {prefix}.csv from {selected_backup}")
                            st.rerun()
                            break
            else:
                st.info("No backups found yet.")
        else:
            st.info("Backup directory not created yet.")
```

- [ ] **Step 6: Verify and commit**

```bash
git add planner21.py pages/finance.py pages/driving.py pages/excercise.py
git commit -m "feat: auto-backup CSVs before saves with restore in Settings"
```

---

### Task 9: Custom Expense Categories

Let users add custom categories from the finance page. Store in settings.csv.

**Files:**
- Modify: `planner21.py` (expand settings schema)
- Modify: `pages/finance.py` (read custom categories, add management UI)

- [ ] **Step 1: Add custom_categories to settings schema**

Update SETTINGS_COLS in planner21.py:

```python
SETTINGS_COLS = ["long_term_goals", "daily_income_target", "hourly_rate_target", "daily_budget", "monthly_budget", "checklist_items", "expense_categories"]
```

Default: `"expense_categories": "Food,Transport,Bills,Shopping,Health,Family,Other"`

- [ ] **Step 2: Update finance.py to use dynamic categories**

At the top of finance.py (after settings read), add:

```python
DEFAULT_CATEGORIES = ["Food", "Transport", "Bills", "Shopping", "Health", "Family", "Other"]
EXPENSE_CATEGORIES = DEFAULT_CATEGORIES
if os.path.exists(SETTINGS_FILE):
    try:
        _settings = pd.read_csv(SETTINGS_FILE)
        if "expense_categories" in _settings.columns and not _settings.empty:
            raw = str(_settings.loc[0, "expense_categories"]).strip()
            if raw and raw.lower() != "nan":
                EXPENSE_CATEGORIES = [c.strip() for c in raw.split(",") if c.strip()]
    except Exception:
        pass
```

Replace all hardcoded `["Food", "Transport", "Bills", "Shopping", "Health", "Family", "Other"]` with `EXPENSE_CATEGORIES`. There are 2 locations: line 530 (new expense form) and line 599 (edit form).

- [ ] **Step 3: Add category management at bottom of finance page**

After the right column section, add:

```python
st.markdown("---")
st.subheader("⚙️ Manage Expense Categories")
st.caption("Add or remove categories. Changes apply to the dropdown above after page reload.")

new_cat = st.text_input("Add new category")
if st.button("Add Category") and new_cat.strip():
    if new_cat.strip() not in EXPENSE_CATEGORIES:
        EXPENSE_CATEGORIES.append(new_cat.strip())
        # Save back to settings
        if os.path.exists(SETTINGS_FILE):
            _settings = pd.read_csv(SETTINGS_FILE)
            _settings.loc[0, "expense_categories"] = ",".join(EXPENSE_CATEGORIES)
            _settings.to_csv(SETTINGS_FILE, index=False)
            st.success(f"Added '{new_cat.strip()}'")
            st.rerun()

st.write("Current categories: " + ", ".join(EXPENSE_CATEGORIES))
```

- [ ] **Step 4: Verify and commit**

```bash
git add planner21.py pages/finance.py
git commit -m "feat: custom expense categories stored in settings"
```

---

### Task 10: Journal / Notes Page

A simple freeform daily notes page separate from the planner reflection.

**Files:**
- Create: `pages/journal.py`
- CSV: `data/journal.csv` (date, entry)

- [ ] **Step 1: Create the journal page**

```python
import os
from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Journal", page_icon="📓", layout="wide")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
JOURNAL_FILE = os.path.join(DATA_DIR, "journal.csv")
BACKUP_FOLDER = os.path.join(DATA_DIR, "backups")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

JOURNAL_COLS = ["date", "entry"]

if not os.path.exists(JOURNAL_FILE):
    pd.DataFrame(columns=JOURNAL_COLS).to_csv(JOURNAL_FILE, index=False)


def backup_csv(filepath):
    if os.path.exists(filepath):
        from datetime import datetime as dt_cls
        import shutil, glob
        basename = os.path.basename(filepath).replace(".csv", "")
        stamp = dt_cls.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(filepath, os.path.join(BACKUP_FOLDER, f"{basename}_{stamp}.csv"))
        for old in sorted(glob.glob(os.path.join(BACKUP_FOLDER, f"{basename}_*.csv")))[:-20]:
            os.remove(old)


def load_journal():
    try:
        df = pd.read_csv(JOURNAL_FILE)
        if df.empty:
            return pd.DataFrame(columns=JOURNAL_COLS)
        df["date"] = df["date"].astype(str)
        return df
    except Exception:
        return pd.DataFrame(columns=JOURNAL_COLS)


def save_journal(df):
    backup_csv(JOURNAL_FILE)
    df.to_csv(JOURNAL_FILE, index=False)


# ── Styling ──
st.markdown("""
<style>
:root {
    --accent: #8a7055; --pos: #5a9a6a; --neg: #b87070;
    --border: 1px solid rgba(0,0,0,0.07); --shadow: 0 1px 3px rgba(0,0,0,0.04);
}
@media (prefers-color-scheme: dark) {
    :root { --accent: #b08a65; --border: 1px solid rgba(255,255,255,0.07); --shadow: 0 1px 3px rgba(0,0,0,0.12); --pos: #7ab88a; }
}
[data-theme="dark"] { --accent: #b08a65; --border: 1px solid rgba(255,255,255,0.07); --shadow: 0 1px 3px rgba(0,0,0,0.12); --pos: #7ab88a; }
.stDecoration { display: none !important; }
html, body, [class*="css"] { font-family: Georgia, 'Times New Roman', serif !important; }
.block-container { max-width: 900px; padding-top: 4rem !important; padding-bottom: 4rem !important; }
.j-card { border: var(--border); border-radius: 18px; padding: 24px 28px; background: var(--secondary-background-color); box-shadow: var(--shadow); margin-bottom: 14px; }
.j-date { font-size: 10px; opacity: 0.55; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 400; margin-bottom: 8px; }
.j-text { font-size: 15px; line-height: 1.85; white-space: pre-wrap; }
div[data-testid="stForm"] { border: none !important; padding: 0 !important; background: transparent !important; }
div[data-testid="stTextArea"] textarea { border-radius: 12px !important; font-family: Georgia, serif !important; font-size: 14.5px !important; }
div.stButton > button { border-radius: 12px !important; border: 1px solid rgba(0,0,0,0.14) !important; font-weight: 400 !important; font-family: Georgia, serif !important; background: var(--secondary-background-color) !important; color: inherit !important; }
div.stButton > button:hover { border-color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
_dark = st.session_state["dark_mode"]
_bg = "#0e1117" if _dark else "#f5f0e8"
_sbg = "#161b22" if _dark else "#ede8de"
_color = "#fafafa" if _dark else "#3a3028"
st.markdown(f"""<style>
.stApp {{ background-color: {_bg} !important; color: {_color} !important; }}
section[data-testid="stSidebar"] > div:first-child {{ background-color: {_sbg} !important; }}
header[data-testid="stHeader"] {{ background-color: {_bg} !important; }}
</style>""", unsafe_allow_html=True)

# ── Page ──
st.title("📓 Journal")
st.markdown('<div style="opacity:0.6;margin-bottom:1.4rem">Thoughts, ideas, and anything that doesn\'t fit elsewhere.</div>', unsafe_allow_html=True)

today_str = str(date.today())
journal_df = load_journal()

# Get today's entry if it exists
existing = journal_df[journal_df["date"] == today_str]
current_entry = existing.iloc[0]["entry"] if not existing.empty else ""

with st.form("journal_form"):
    entry = st.text_area(
        f"Journal — {today_str}",
        value=current_entry if pd.notna(current_entry) else "",
        height=300,
        placeholder="Write freely. This is your space.",
        label_visibility="collapsed",
    )
    if st.form_submit_button("💾 Save Entry", use_container_width=True):
        if today_str in journal_df["date"].values:
            journal_df.loc[journal_df["date"] == today_str, "entry"] = entry.strip()
        else:
            journal_df = pd.concat([journal_df, pd.DataFrame([{"date": today_str, "entry": entry.strip()}])], ignore_index=True)
        save_journal(journal_df)
        st.success("Journal saved.")
        st.rerun()

# ── Past entries ──
if len(journal_df) > 0:
    st.markdown("---")
    st.markdown('<div style="font-size:10px;opacity:0.55;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:14px">Past Entries</div>', unsafe_allow_html=True)

    past = journal_df[journal_df["date"] != today_str].sort_values("date", ascending=False)
    for _, row in past.iterrows():
        entry_text = str(row["entry"]) if pd.notna(row["entry"]) else ""
        if entry_text:
            st.markdown(
                f'<div class="j-card"><div class="j-date">{row["date"]}</div><div class="j-text">{entry_text}</div></div>',
                unsafe_allow_html=True,
            )
```

- [ ] **Step 2: Verify**

Run app, navigate to Journal, write and save an entry.

- [ ] **Step 3: Commit**

```bash
git add pages/journal.py
git commit -m "feat: add journal page for freeform daily notes"
```

---

## Self-Review Checklist

1. **Spec coverage:** All 10 features mapped to tasks. Task 1 = daily entry form, Task 2 = restore nav, Task 3 = configurable targets, Task 4 = weekly review, Task 5 = per-habit streaks, Task 6 = budget alerts, Task 7 = morning checklist, Task 8 = data backup, Task 9 = custom categories, Task 10 = journal page. No gaps.

2. **Placeholder scan:** All code blocks are complete. No TODOs, TBDs, or "fill in later" statements.

3. **Type consistency:** `SETTINGS_COLS` is built up incrementally across tasks (3→6→7→9). Final value: `["long_term_goals", "daily_income_target", "hourly_rate_target", "daily_budget", "monthly_budget", "checklist_items", "expense_categories"]`. All task code references these column names consistently.
