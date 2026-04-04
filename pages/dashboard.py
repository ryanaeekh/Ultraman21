import os
import calendar
from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header, metric_card, detail_row as theme_detail_row, section_card as theme_section_card, status_badge, progress_bar, ACCENT, POS, NEG, TEXT2
from utils import safe_float, safe_bool, clean_text

# =========================================================
# PATHS
# =========================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

PLANNER_FILE  = os.path.join(DATA_DIR, "planner.csv")
DRIVING_FILE  = os.path.join(DATA_DIR, "driving.csv")
FINANCE_FILE  = os.path.join(DATA_DIR, "finance.csv")
MONTHLY_FILE  = os.path.join(DATA_DIR, "monthly_expenses.csv")
EXERCISE_FILE = os.path.join(DATA_DIR, "exercise.csv")


# =========================================================
# SAFE HELPERS
# =========================================================
def safe_read_csv(path, columns=None):
    if not os.path.exists(path):
        return pd.DataFrame(columns=columns or [])
    try:
        df = pd.read_csv(path)
        return pd.DataFrame(columns=columns or list(df.columns)) if df.empty else df
    except Exception:
        return pd.DataFrame(columns=columns or [])


def parse_date_column(df, col="date"):
    if df.empty or col not in df.columns:
        return df
    temp = df.copy()
    temp[col] = pd.to_datetime(temp[col], errors="coerce")
    return temp


def get_days_in_month(date_obj):
    return calendar.monthrange(date_obj.year, date_obj.month)[1]


def detail_row(key, val, cls=""):
    """Build one detail-row using theme classes."""
    return theme_detail_row(key, val, cls)


def section_card(title, inner_html, extra_style=""):
    """Build a section card using theme classes."""
    return theme_section_card(title, inner_html)


# =========================================================
# CACHED DATA LOADERS
# =========================================================
@st.cache_data(ttl=15)
def load_planner():
    """
    Reads ultraman21.py schema:
    date, priority_1, priority_2, priority_3,
    focus_done, run_done, income_done, reflection, score
    """
    df = safe_read_csv(PLANNER_FILE)
    if df.empty:
        return df
    if "date" in df.columns:
        df["date"] = df["date"].astype(str)
    for col in ["focus_done", "run_done", "income_done"]:
        if col in df.columns:
            df[col] = df[col].apply(safe_bool)
    if "score" in df.columns:
        df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0).astype(int)
    return df


@st.cache_data(ttl=15)
def load_driving():
    df = safe_read_csv(DRIVING_FILE)
    if not df.empty:
        if "date" in df.columns:
            df["date"] = df["date"].astype(str)
        if "earnings" in df.columns:
            df["earnings"] = df["earnings"].apply(safe_float)
    return df


@st.cache_data(ttl=15)
def load_finance():
    df = safe_read_csv(FINANCE_FILE)
    if not df.empty:
        if "date" in df.columns:
            df["date"] = df["date"].astype(str)
        if "amount" in df.columns:
            df["amount"] = df["amount"].apply(safe_float)
    return df


@st.cache_data(ttl=15)
def load_monthly():
    df = safe_read_csv(MONTHLY_FILE)
    if not df.empty and "amount" in df.columns:
        df["amount"] = df["amount"].apply(safe_float)
    return df


@st.cache_data(ttl=15)
def load_exercise():
    df = safe_read_csv(EXERCISE_FILE)
    if not df.empty and "date" in df.columns:
        df["date"] = df["date"].astype(str)
    return df


# =========================================================
# TODAY HELPERS
# =========================================================
def get_today_planner_row(planner_df, today_str):
    if planner_df.empty or "date" not in planner_df.columns:
        return None
    rows = planner_df[planner_df["date"] == today_str]
    return rows.iloc[0] if not rows.empty else None


def get_today_income(driving_df, today_str):
    if driving_df.empty or "date" not in driving_df.columns or "earnings" not in driving_df.columns:
        return 0.0
    rows = driving_df[driving_df["date"] == today_str]
    return round(rows["earnings"].sum(), 2) if not rows.empty else 0.0


def get_today_variable_expense(finance_df, today_str):
    if finance_df.empty or "date" not in finance_df.columns or "amount" not in finance_df.columns:
        return 0.0
    rows = finance_df[finance_df["date"] == today_str]
    return round(rows["amount"].sum(), 2) if not rows.empty else 0.0


def get_daily_fixed_share(monthly_df, date_obj):
    if monthly_df.empty or "amount" not in monthly_df.columns:
        return 0.0
    total = monthly_df["amount"].apply(safe_float).sum()
    days = get_days_in_month(date_obj)
    return round(total / days, 2) if days > 0 else 0.0


def get_today_score(planner_df, today_str):
    row = get_today_planner_row(planner_df, today_str)
    if row is None or "score" not in row.index:
        return 0
    try:
        return int(float(row["score"]))
    except Exception:
        return 0


# =========================================================
# STATUS HELPERS
# =========================================================
def get_execution_status(score):
    if score >= 85:   return "🟢 Locked In"
    elif score >= 70: return "🟡 On Track"
    elif score >= 50: return "🟠 Unstable"
    return "🔴 Off System"


def get_status_class(score):
    if score >= 85:   return "good"
    elif score >= 70: return "mid"
    elif score >= 50: return "warn"
    return "bad"


def get_net_class(value):
    if value > 0:   return "positive"
    elif value < 0: return "negative"
    return ""


def get_today_rule(planner_row, income, expense):
    if planner_row is not None:
        for field in ["today_rule", "reflection"]:
            if field in planner_row.index:
                val = clean_text(planner_row.get(field, ""))
                if val:
                    return val
    if income == 0 and expense == 0:
        return "No data yet — log the day properly."
    if income <= 0 and expense > 0:
        return "Expense without income — protect cash today."
    if income > expense:
        return "You stayed above water today — maintain control."
    if income == expense:
        return "Break-even day — tighten decisions."
    return "Expense is beating income — cut leakage immediately."


# =========================================================
# EXERCISE
# =========================================================
def get_exercise_status(exercise_df, today_str):
    if exercise_df.empty or "date" not in exercise_df.columns:
        return "No Data Yet", "🏃", 0, "Create exercise.csv to start tracking"
    rows = exercise_df[exercise_df["date"] == today_str]
    if rows.empty:
        return "Not Logged", "🏃", 0, "No exercise entry today"

    row    = rows.iloc[0]
    status = clean_text(row.get("status", "")).lower()
    etype  = clean_text(row.get("type", ""))
    dur    = clean_text(row.get("duration", ""))
    km     = clean_text(row.get("km", ""))
    notes  = clean_text(row.get("notes", ""))

    label, percent = "Logged", 25
    if status in ("done", "completed", "yes"):  label, percent = "Completed", 100
    elif status in ("rest", "off"):             label, percent = "Rest Day", 60
    elif status in ("planned", "scheduled"):    label, percent = "Planned", 35

    parts  = [p for p in [etype, (km + " km") if km else "", (dur + " min") if dur else ""] if p]
    detail = " · ".join(parts) if parts else (notes or "Exercise logged")
    return label, "🏋️", percent, detail


# =========================================================
# STREAK & TREND
# =========================================================
def compute_streak(planner_df):
    if planner_df.empty or "score" not in planner_df.columns:
        return 0
    completed = set(planner_df[planner_df["score"] > 0]["date"].astype(str).tolist())
    streak, check = 0, date.today()
    while str(check) in completed:
        streak += 1
        check -= timedelta(days=1)
    return streak


def compute_weekly_avg(planner_df):
    if planner_df.empty or "score" not in planner_df.columns:
        return 0
    week_ago = str(date.today() - timedelta(days=6))
    week_df  = planner_df[planner_df["date"] >= week_ago]
    return round(week_df["score"].mean()) if not week_df.empty else 0


def get_score_trend(planner_df, days=7):
    if planner_df.empty or "score" not in planner_df.columns:
        return []
    cutoff = str(date.today() - timedelta(days=days - 1))
    recent = planner_df[planner_df["date"] >= cutoff].sort_values("date")
    return list(zip(recent["date"].astype(str), recent["score"].astype(int)))


# =========================================================
# MONTHLY HELPERS
# =========================================================
def get_monthly_income(driving_df, today_obj):
    if driving_df.empty or "date" not in driving_df.columns or "earnings" not in driving_df.columns:
        return 0.0
    temp = parse_date_column(driving_df.copy(), "date")
    temp["earnings"] = temp["earnings"].apply(safe_float)
    temp = temp.dropna(subset=["date"])
    rows = temp[(temp["date"].dt.year == today_obj.year) & (temp["date"].dt.month == today_obj.month)]
    return round(rows["earnings"].sum(), 2)


def get_monthly_variable_expense(finance_df, today_obj):
    if finance_df.empty or "date" not in finance_df.columns or "amount" not in finance_df.columns:
        return 0.0
    temp = parse_date_column(finance_df.copy(), "date")
    temp["amount"] = temp["amount"].apply(safe_float)
    temp = temp.dropna(subset=["date"])
    rows = temp[(temp["date"].dt.year == today_obj.year) & (temp["date"].dt.month == today_obj.month)]
    return round(rows["amount"].sum(), 2)


def get_monthly_fixed_expense(monthly_df):
    if monthly_df.empty or "amount" not in monthly_df.columns:
        return 0.0
    return round(monthly_df["amount"].apply(safe_float).sum(), 2)


def get_monthly_avg_score(planner_df, today_obj):
    if planner_df.empty or "score" not in planner_df.columns:
        return 0.0
    temp = parse_date_column(planner_df.copy(), "date")
    temp["score"] = pd.to_numeric(temp["score"], errors="coerce").fillna(0)
    temp = temp.dropna(subset=["date"])
    rows = temp[(temp["date"].dt.year == today_obj.year) & (temp["date"].dt.month == today_obj.month)]
    return round(rows["score"].mean(), 1) if not rows.empty else 0.0


def get_income_pace(monthly_income, today_obj):
    elapsed = today_obj.day
    if elapsed == 0:
        return None, None
    daily_rate = monthly_income / elapsed
    projected  = daily_rate * get_days_in_month(today_obj)
    return round(daily_rate, 2), round(projected, 2)


# =========================================================
# INSIGHTS
# =========================================================
def build_insights(today_net, today_score, monthly_net):
    i1 = ("You are positive for the day. Protect the gain — avoid careless spending tonight." if today_net > 0
          else "You are negative for the day. Reduce leakage and close with discipline." if today_net < 0
          else "Break-even so far. One strong decision can still swing the day.")
    i2 = ("Execution is strong. Keep momentum and avoid unnecessary distractions." if today_score >= 85
          else "Still recoverable. Finish one meaningful action before shutdown." if today_score >= 60
          else "System not fully online. Focus on one reset action instead of chasing perfection.")
    i3 = ("Month is above water. Keep structure tight and stack consistent days." if monthly_net > 0
          else "Month is under pressure. Watch spending and push productive output." if monthly_net < 0
          else "Month is neutral. Small improvements matter most right now.")
    return i1, i2, i3


def get_strongest_lever(today_net, today_score, exercise_label):
    if today_score >= 85:         return "Execution is your strongest lever today — protect momentum."
    if today_net > 0:             return "Money discipline is working — avoid giving it back."
    if exercise_label == "Completed": return "Training is done — use that win to carry the rest of the day."
    return "Simplicity is your strongest lever — finish one meaningful action."


def get_recovery_action(today_score, today_net, exercise_label):
    if today_score < 50:  return "Complete one focused task before the day ends."
    if today_net < 0:     return "Stop extra spending and close the day clean."
    if exercise_label in ("Not Logged", "No Data Yet", "Logged", "Planned"):
        return "Get some movement in — even a short session counts."
    return "Maintain control and do not drift tonight."


# =========================================================
# LOAD ALL DATA
# =========================================================
today_obj = date.today()
today     = str(today_obj)

planner_df  = load_planner()
driving_df  = load_driving()
finance_df  = load_finance()
monthly_df  = load_monthly()
exercise_df = load_exercise()

planner_row = get_today_planner_row(planner_df, today)

today_income           = get_today_income(driving_df, today)
today_variable_expense = get_today_variable_expense(finance_df, today)
today_fixed_share      = get_daily_fixed_share(monthly_df, today_obj)
today_total_expense    = round(today_variable_expense + today_fixed_share, 2)
today_net              = round(today_income - today_total_expense, 2)

today_score      = get_today_score(planner_df, today)
execution_status = get_execution_status(today_score)
status_class     = get_status_class(today_score)
today_rule       = get_today_rule(planner_row, today_income, today_total_expense)

exercise_label, exercise_icon, exercise_percent, exercise_detail = get_exercise_status(exercise_df, today)

monthly_income           = get_monthly_income(driving_df, today_obj)
monthly_variable_expense = get_monthly_variable_expense(finance_df, today_obj)
monthly_fixed_expense    = get_monthly_fixed_expense(monthly_df)
monthly_total_expense    = round(monthly_variable_expense + monthly_fixed_expense, 2)
monthly_net              = round(monthly_income - monthly_total_expense, 2)
monthly_avg_score        = get_monthly_avg_score(planner_df, today_obj)

streak      = compute_streak(planner_df)
weekly_avg  = compute_weekly_avg(planner_df)
score_trend = get_score_trend(planner_df, days=7)

daily_rate, projected_income = get_income_pace(monthly_income, today_obj)

score_progress    = max(0, min(today_score, 100))
exercise_progress = max(0, min(exercise_percent, 100))

insight_1, insight_2, insight_3 = build_insights(today_net, today_score, monthly_net)
strongest_lever = get_strongest_lever(today_net, today_score, exercise_label)
recovery_action = get_recovery_action(today_score, today_net, exercise_label)

month_name = today_obj.strftime("%B %Y")


# =========================================================
# INJECT THEME
# =========================================================
inject_theme()
nav_menu("Dashboard")

# =========================================================
# HEADER
# =========================================================
st.markdown(page_header("System Dashboard", "Daily overview"), unsafe_allow_html=True)

# =========================================================
# RULE BANNER
# =========================================================
st.markdown(
    '<div class="card accent-left-card">'
    '<div class="metric-label">Today\'s Rule</div>'
    '<div style="font-size:1.1rem;line-height:1.6;margin-top:6px">🧠 ' + today_rule + '</div>'
    '</div>',
    unsafe_allow_html=True,
)

# =========================================================
# TOP 3 METRIC CARDS
# =========================================================
top1, top2, top3 = st.columns(3, gap="large")

net_color = POS if today_net > 0 else NEG if today_net < 0 else ""
with top1:
    st.markdown(
        metric_card(
            "Today Net",
            "$" + f"{today_net:.2f}",
            "Income $" + f"{today_income:.2f}" + " · Spent $" + f"{today_total_expense:.2f}",
            color=net_color,
        ),
        unsafe_allow_html=True,
    )

with top2:
    st.markdown(
        metric_card("Exercise", exercise_label, exercise_detail, color=ACCENT)
        + progress_bar(exercise_progress, ACCENT),
        unsafe_allow_html=True,
    )

with top3:
    st.markdown(
        metric_card("Daily Score", str(today_score) + "/100", execution_status, color=ACCENT)
        + progress_bar(score_progress, ACCENT),
        unsafe_allow_html=True,
    )

# =========================================================
# EXECUTION STATUS CARD
# =========================================================
st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

status_color = POS if status_class == "good" else NEG if status_class == "bad" else ACCENT
exec_rows = (
    detail_row("Date", today) +
    detail_row("Exercise", exercise_label) +
    detail_row("Today Net", "$" + f"{today_net:.2f}", get_net_class(today_net)) +
    detail_row("7-Day Avg Score", str(weekly_avg) + "/100") +
    detail_row("Current Streak", "🔥 " + str(streak) + " days")
)
st.markdown(
    '<div class="card">'
    '<div class="section-title">⚡ Execution Status</div>'
    + status_badge(execution_status, status_color)
    + progress_bar(score_progress, status_color)
    + exec_rows +
    '</div>',
    unsafe_allow_html=True,
)

# =========================================================
# MAIN 2-COLUMN LAYOUT
# =========================================================
left_col, right_col = st.columns([1.2, 1], gap="large")

with left_col:
    # Today Financial Breakdown
    fin_rows = (
        detail_row("Driving Income",   "$" + f"{today_income:.2f}") +
        detail_row("Variable Expense", "$" + f"{today_variable_expense:.2f}") +
        detail_row("Fixed Expense Share", "$" + f"{today_fixed_share:.2f}") +
        detail_row("Total Expense",    "$" + f"{today_total_expense:.2f}") +
        detail_row("Today Net",        "$" + f"{today_net:.2f}", get_net_class(today_net))
    )
    st.markdown(
        section_card("💵 Today Financial Breakdown", fin_rows),
        unsafe_allow_html=True,
    )

    # Monthly Overview
    mon_rows = (
        detail_row("Month Income",      "$" + f"{monthly_income:.2f}") +
        detail_row("Variable Expense",  "$" + f"{monthly_variable_expense:.2f}") +
        detail_row("Fixed Expense",     "$" + f"{monthly_fixed_expense:.2f}") +
        detail_row("Total Expense",     "$" + f"{monthly_total_expense:.2f}") +
        detail_row("Month Net",         "$" + f"{monthly_net:.2f}", get_net_class(monthly_net))
    )
    if daily_rate is not None:
        mon_rows += (
            detail_row("Daily Run Rate",         "$" + f"{daily_rate:.2f}" + "/day") +
            detail_row("Projected Month Income", "$" + f"{projected_income:.2f}")
        )
    mon_rows += detail_row("Avg Score This Month", f"{monthly_avg_score}/100")

    st.markdown(
        section_card("📈 Monthly Overview · " + month_name, mon_rows),
        unsafe_allow_html=True,
    )

with right_col:
    # System Insights
    insights_html = (
        '<div class="insight-box">' + insight_1 + '</div>'
        '<div class="insight-box">' + insight_2 + '</div>'
        '<div class="insight-box">' + insight_3 + '</div>'
    )
    st.markdown(
        section_card("🧠 System Insights", insights_html),
        unsafe_allow_html=True,
    )

    # Mission21 Focus Panel
    focus_html = (
        '<div class="focus-box"><div class="metric-label">Today\'s Rule</div>'
        '<div style="margin-top:6px">' + today_rule + '</div></div>'
        '<div class="focus-box"><div class="metric-label">Strongest Lever</div>'
        '<div style="margin-top:6px">' + strongest_lever + '</div></div>'
        '<div class="focus-box"><div class="metric-label">Recovery Action</div>'
        '<div style="margin-top:6px">' + recovery_action + '</div></div>'
    )
    st.markdown(
        section_card("🎯 Mission21 Focus Panel", focus_html),
        unsafe_allow_html=True,
    )
