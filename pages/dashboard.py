import calendar
from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header, metric_card, detail_row as theme_detail_row, section_card as theme_section_card, status_badge, progress_bar, ACCENT, POS, NEG, TEXT2
from utils import safe_float, safe_bool, clean_text, load_planner, load_driving, load_finance, load_monthly_expenses, load_exercise


def get_days_in_month(date_obj):
    return calendar.monthrange(date_obj.year, date_obj.month)[1]


def detail_row(key, val, cls=""):
    return theme_detail_row(key, val, cls)


def section_card(title, inner_html, extra_style=""):
    return theme_section_card(title, inner_html)


# =========================================================
# CACHED DATA LOADERS
# =========================================================
@st.cache_data(ttl=15)
def _load_planner():
    df = load_planner()
    if not df.empty and "date" in df.columns:
        df["date"] = df["date"].astype(str)
    return df


@st.cache_data(ttl=15)
def _load_driving():
    df = load_driving()
    if not df.empty and "date" in df.columns:
        df["date"] = df["date"].astype(str)
    return df


@st.cache_data(ttl=15)
def _load_finance():
    df = load_finance()
    if not df.empty and "date" in df.columns:
        df["date"] = df["date"].astype(str)
    return df


@st.cache_data(ttl=15)
def _load_monthly():
    df = load_monthly_expenses()
    if not df.empty and "amount" in df.columns:
        df["amount"] = df["amount"].apply(safe_float)
    return df


@st.cache_data(ttl=15)
def _load_exercise():
    df = load_exercise()
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


def get_exercise_status(exercise_df, today_str):
    if exercise_df.empty or "date" not in exercise_df.columns:
        return "No Data Yet", "🏃", 0, "Create exercise.csv to start tracking"
    rows = exercise_df[exercise_df["date"] == today_str]
    if rows.empty:
        return "Not Logged", "🏃", 0, "No entry for today yet"
    row = rows.iloc[0]
    status = str(row.get("status", "")).strip().lower()
    km = safe_float(row.get("km", 0))
    duration = safe_float(row.get("duration", 0))
    ex_type = str(row.get("type", "")).strip() or "Exercise"
    if status in ["done", "completed", "yes"]:
        detail = f"{ex_type} · {km:.1f} km · {duration:.0f} min" if km > 0 else f"{ex_type} · {duration:.0f} min"
        return "Completed", "✅", 100, detail
    elif status in ["rest", "off"]:
        return "Rest Day", "🛌", 50, "Scheduled rest"
    elif status in ["planned"]:
        return "Planned", "📌", 20, f"{ex_type} planned"
    return "Logged", "📋", 30, f"{ex_type} logged"


def get_monthly_income(driving_df, date_obj):
    if driving_df.empty or "date" not in driving_df.columns or "earnings" not in driving_df.columns:
        return 0.0
    temp = driving_df.copy()
    temp["date"] = pd.to_datetime(temp["date"], errors="coerce")
    temp = temp.dropna(subset=["date"])
    mask = (temp["date"].dt.year == date_obj.year) & (temp["date"].dt.month == date_obj.month)
    return round(temp.loc[mask, "earnings"].apply(safe_float).sum(), 2)


def get_monthly_variable_expense(finance_df, date_obj):
    if finance_df.empty or "date" not in finance_df.columns or "amount" not in finance_df.columns:
        return 0.0
    temp = finance_df.copy()
    temp["date"] = pd.to_datetime(temp["date"], errors="coerce")
    temp = temp.dropna(subset=["date"])
    mask = (temp["date"].dt.year == date_obj.year) & (temp["date"].dt.month == date_obj.month)
    return round(temp.loc[mask, "amount"].apply(safe_float).sum(), 2)


def get_monthly_fixed_expense(monthly_df):
    if monthly_df.empty or "amount" not in monthly_df.columns:
        return 0.0
    return round(monthly_df["amount"].apply(safe_float).sum(), 2)


def get_monthly_avg_score(planner_df, date_obj):
    if planner_df.empty or "date" not in planner_df.columns or "score" not in planner_df.columns:
        return 0
    temp = planner_df.copy()
    temp["date"] = pd.to_datetime(temp["date"], errors="coerce")
    temp = temp.dropna(subset=["date"])
    mask = (temp["date"].dt.year == date_obj.year) & (temp["date"].dt.month == date_obj.month)
    month_df = temp.loc[mask]
    return round(month_df["score"].mean()) if not month_df.empty else 0


def compute_streak(planner_df):
    if planner_df.empty:
        return 0
    completed = set(planner_df[planner_df["score"] > 0]["date"].astype(str).tolist())
    streak = 0
    check = date.today()
    while str(check) in completed:
        streak += 1
        check -= timedelta(days=1)
    return streak


def compute_weekly_avg(planner_df):
    if planner_df.empty:
        return 0
    week_ago = str(date.today() - timedelta(days=6))
    week_df = planner_df[planner_df["date"] >= week_ago]
    return round(week_df["score"].mean()) if not week_df.empty else 0


def get_score_trend(planner_df, days=7):
    if planner_df.empty:
        return 0
    week_ago = str(date.today() - timedelta(days=days))
    prev_week = str(date.today() - timedelta(days=days * 2))
    current = planner_df[planner_df["date"] >= week_ago]["score"].mean() if not planner_df[planner_df["date"] >= week_ago].empty else 0
    previous = planner_df[(planner_df["date"] >= prev_week) & (planner_df["date"] < week_ago)]["score"].mean() if not planner_df[(planner_df["date"] >= prev_week) & (planner_df["date"] < week_ago)].empty else 0
    return round(current - previous, 1)


def get_income_pace(monthly_income, date_obj):
    day = date_obj.day
    if day == 0:
        return None, None
    daily_rate = round(monthly_income / day, 2)
    days_in_month = get_days_in_month(date_obj)
    projected = round(daily_rate * days_in_month, 2)
    return daily_rate, projected


def build_insights(today_net, today_score, monthly_net):
    i1 = ("Execution is strong today." if today_score >= 70
          else "Execution is below standard. Push harder before the day closes." if today_score < 50
          else "Execution is partial. Finish the remaining priorities.")
    i2 = ("Positive cash flow today. Protect the margin." if today_net > 0
          else "Negative cash flow today. Find the leak and fix it." if today_net < 0
          else "Break even today. Push income or cut spending.")
    i3 = ("Month is above water. Keep structure tight." if monthly_net > 0
          else "Month is under pressure. Watch spending and push output." if monthly_net < 0
          else "Month is neutral. Small improvements matter most.")
    return i1, i2, i3


def get_strongest_lever(today_net, today_score, exercise_label):
    if today_score >= 85:             return "Execution is your strongest lever today — protect momentum."
    if today_net > 0:                 return "Money discipline is working — avoid giving it back."
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

planner_df  = _load_planner()
driving_df  = _load_driving()
finance_df  = _load_finance()
monthly_df  = _load_monthly()
exercise_df = _load_exercise()

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

st.markdown(page_header("System Dashboard", "Daily overview"), unsafe_allow_html=True)

st.markdown(
    '<div class="card accent-left-card">'
    '<div class="metric-label">Today\'s Rule</div>'
    '<div style="font-size:1.1rem;line-height:1.6;margin-top:6px">🧠 ' + today_rule + '</div>'
    '</div>',
    unsafe_allow_html=True,
)

top1, top2, top3 = st.columns(3, gap="large")
net_color = POS if today_net > 0 else NEG if today_net < 0 else ""
with top1:
    st.markdown(metric_card("Today Net", "$" + f"{today_net:.2f}", "Income $" + f"{today_income:.2f}" + " · Spent $" + f"{today_total_expense:.2f}", color=net_color), unsafe_allow_html=True)
with top2:
    st.markdown(metric_card("Exercise", exercise_label, exercise_detail, color=ACCENT) + progress_bar(exercise_progress, ACCENT), unsafe_allow_html=True)
with top3:
    st.markdown(metric_card("Daily Score", str(today_score) + "/100", execution_status, color=ACCENT) + progress_bar(score_progress, ACCENT), unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

status_color = POS if status_class == "good" else NEG if status_class == "bad" else ACCENT
exec_rows = (
    detail_row("Date", today) +
    detail_row("Exercise", exercise_label) +
    detail_row("Today Net", "$" + f"{today_net:.2f}", get_net_class(today_net)) +
    detail_row("7-Day Avg Score", str(weekly_avg) + "/100") +
    detail_row("Current Streak", "🔥 " + str(streak) + " days")
)
st.markdown('<div class="card"><div class="section-title">⚡ Execution Status</div>' + status_badge(execution_status, status_color) + progress_bar(score_progress, status_color) + exec_rows + '</div>', unsafe_allow_html=True)

left_col, right_col = st.columns([1.2, 1], gap="large")

with left_col:
    fin_rows = (
        detail_row("Driving Income",   "$" + f"{today_income:.2f}") +
        detail_row("Variable Expense", "$" + f"{today_variable_expense:.2f}") +
        detail_row("Fixed Expense Share", "$" + f"{today_fixed_share:.2f}") +
        detail_row("Total Expense",    "$" + f"{today_total_expense:.2f}") +
        detail_row("Today Net",        "$" + f"{today_net:.2f}", get_net_class(today_net))
    )
    st.markdown(section_card("💵 Today Financial Breakdown", fin_rows), unsafe_allow_html=True)

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
    st.markdown(section_card("📈 Monthly Overview · " + month_name, mon_rows), unsafe_allow_html=True)

with right_col:
    insights_html = '<div class="insight-box">' + insight_1 + '</div><div class="insight-box">' + insight_2 + '</div><div class="insight-box">' + insight_3 + '</div>'
    st.markdown(section_card("🧠 System Insights", insights_html), unsafe_allow_html=True)

    focus_html = (
        '<div class="focus-box"><div class="metric-label">Today\'s Rule</div><div style="margin-top:6px">' + today_rule + '</div></div>'
        '<div class="focus-box"><div class="metric-label">Strongest Lever</div><div style="margin-top:6px">' + strongest_lever + '</div></div>'
        '<div class="focus-box"><div class="metric-label">Recovery Action</div><div style="margin-top:6px">' + recovery_action + '</div></div>'
    )
    st.markdown(section_card("🎯 Mission21 Focus Panel", focus_html), unsafe_allow_html=True)
