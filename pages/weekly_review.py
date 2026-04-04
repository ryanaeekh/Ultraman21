import calendar
from datetime import date, timedelta

import pandas as pd
import streamlit as st
from theme import inject_theme, nav_menu, page_header, metric_card, detail_row, section_card, ACCENT, POS, NEG
from utils import safe_float, safe_bool, load_planner, load_driving, load_finance, load_monthly_expenses, load_exercise

st.set_page_config(page_title="Weekly Review", page_icon="📅", layout="wide", initial_sidebar_state="collapsed")


def get_days_in_month(date_obj):
    return calendar.monthrange(date_obj.year, date_obj.month)[1]


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
    return load_monthly_expenses()


@st.cache_data(ttl=15)
def _load_exercise():
    df = load_exercise()
    if not df.empty and "date" in df.columns:
        df["date"] = df["date"].astype(str)
    return df


# =========================================================
# WEEKLY CALCULATIONS
# =========================================================
today_obj = date.today()
week_start = today_obj - timedelta(days=6)
week_dates = [str(week_start + timedelta(days=i)) for i in range(7)]

planner_df  = _load_planner()
driving_df  = _load_driving()
finance_df  = _load_finance()
monthly_df  = _load_monthly()
exercise_df = _load_exercise()

week_income = 0.0
if not driving_df.empty and "date" in driving_df.columns and "earnings" in driving_df.columns:
    mask = driving_df["date"].isin(week_dates)
    week_income = round(driving_df.loc[mask, "earnings"].sum(), 2)

week_variable_exp = 0.0
if not finance_df.empty and "date" in finance_df.columns and "amount" in finance_df.columns:
    mask = finance_df["date"].isin(week_dates)
    week_variable_exp = round(finance_df.loc[mask, "amount"].sum(), 2)

daily_fixed_share = 0.0
if not monthly_df.empty and "amount" in monthly_df.columns:
    total_fixed = monthly_df["amount"].apply(safe_float).sum()
    days_in_month = get_days_in_month(today_obj)
    daily_fixed_share = round(total_fixed / days_in_month, 2) if days_in_month > 0 else 0.0
week_fixed = round(daily_fixed_share * 7, 2)
week_total_exp = round(week_variable_exp + week_fixed, 2)
week_net = round(week_income - week_total_exp, 2)

week_avg_score = 0.0
if not planner_df.empty and "score" in planner_df.columns and "date" in planner_df.columns:
    mask = planner_df["date"].isin(week_dates)
    week_scores = planner_df.loc[mask]
    if not week_scores.empty:
        week_avg_score = round(week_scores["score"].mean(), 1)

exercise_count = 0
if not exercise_df.empty and "date" in exercise_df.columns and "status" in exercise_df.columns:
    mask = exercise_df["date"].isin(week_dates)
    week_ex = exercise_df.loc[mask]
    exercise_count = int(week_ex["status"].apply(lambda v: str(v).strip().lower() in ("done", "completed", "yes")).sum())

best_day = "N/A"
worst_day = "N/A"
if not planner_df.empty and "score" in planner_df.columns and "date" in planner_df.columns:
    mask = planner_df["date"].isin(week_dates)
    week_plan = planner_df.loc[mask].copy()
    if not week_plan.empty:
        best_day = week_plan.loc[week_plan["score"].idxmax(), "date"]
        worst_day = week_plan.loc[week_plan["score"].idxmin(), "date"]

day_rows = []
for d in week_dates:
    score = 0
    if not planner_df.empty and "date" in planner_df.columns and "score" in planner_df.columns:
        rows = planner_df[planner_df["date"] == d]
        if not rows.empty:
            score = int(rows.iloc[0]["score"])
    income = 0.0
    if not driving_df.empty and "date" in driving_df.columns and "earnings" in driving_df.columns:
        rows = driving_df[driving_df["date"] == d]
        if not rows.empty:
            income = round(rows["earnings"].sum(), 2)
    expense = 0.0
    if not finance_df.empty and "date" in finance_df.columns and "amount" in finance_df.columns:
        rows = finance_df[finance_df["date"] == d]
        if not rows.empty:
            expense = round(rows["amount"].sum(), 2)
    day_net = round(income - expense - daily_fixed_share, 2)
    day_rows.append({"Date": d, "Score": score, "Income": income, "Expense": expense, "Net": day_net})

# =========================================================
# THEME + HEADER
# =========================================================
inject_theme()
nav_menu("Weekly Review")

start_str = week_start.strftime("%b %d")
end_str = today_obj.strftime("%b %d, %Y")
st.markdown(page_header("Weekly Review", f"{start_str} — {end_str}"), unsafe_allow_html=True)

net_color = POS if week_net > 0 else (NEG if week_net < 0 else "")
net_sign = "+" if week_net > 0 else ""
score_color = POS if week_avg_score >= 70 else (NEG if week_avg_score < 50 else ACCENT)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(metric_card("Week Income", f"${week_income:,.2f}", "Driving earnings"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("Week Expenses", f"${week_total_exp:,.2f}", f"Variable ${week_variable_exp:,.2f} + Fixed ${week_fixed:,.2f}"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("Week Net", f"{net_sign}${week_net:,.2f}", "Income minus total expenses", color=net_color), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("Avg Score", f'{week_avg_score}<span style="font-size:0.5em;opacity:0.5"> /100</span>', "7-day execution average", color=score_color), unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

col_fin, col_exec = st.columns(2)

with col_fin:
    rows_html = ""
    for key, val, cls in [
        ("Driving Income", f"${week_income:,.2f}", "positive" if week_income > 0 else ""),
        ("Variable Expenses", f"${week_variable_exp:,.2f}", "negative" if week_variable_exp > 0 else ""),
        ("Fixed Expenses (7d share)", f"${week_fixed:,.2f}", "negative" if week_fixed > 0 else ""),
        ("Total Expenses", f"${week_total_exp:,.2f}", "negative" if week_total_exp > 0 else ""),
        ("Net Result", (net_sign + "$" + f"{week_net:,.2f}"), "positive" if week_net > 0 else ("negative" if week_net < 0 else "")),
    ]:
        rows_html += detail_row(key, val, cls)
    st.markdown(section_card("Financial Breakdown", rows_html), unsafe_allow_html=True)

with col_exec:
    score_cls = "positive" if week_avg_score >= 70 else ("negative" if week_avg_score < 50 else "")
    exec_rows_html = ""
    for key, val, cls in [
        ("Avg Score", str(week_avg_score) + " / 100", score_cls),
        ("Exercise Days", str(exercise_count) + " / 7", "positive" if exercise_count >= 5 else ("negative" if exercise_count < 3 else "")),
        ("Best Day", best_day, ""),
        ("Worst Day", worst_day, ""),
        ("Days Logged", str(len(planner_df[planner_df["date"].isin(week_dates)])) + " / 7" if not planner_df.empty and "date" in planner_df.columns else "0 / 7", ""),
    ]:
        exec_rows_html += detail_row(key, val, cls)
    st.markdown(section_card("Execution Summary", exec_rows_html), unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

table_rows = ""
for row in day_rows:
    net_val = row["Net"]
    net_td_cls = "c-pos" if net_val > 0 else ("c-neg" if net_val < 0 else "")
    net_prefix = "+" if net_val > 0 else ""
    score_td_cls = "c-pos" if row["Score"] >= 70 else ("c-neg" if row["Score"] < 50 and row["Score"] > 0 else "")
    table_rows += (
        '<tr>'
        '<td>' + row["Date"] + '</td>'
        '<td class="' + score_td_cls + '">' + str(row["Score"]) + '</td>'
        '<td>$' + f'{row["Income"]:,.2f}' + '</td>'
        '<td>$' + f'{row["Expense"]:,.2f}' + '</td>'
        '<td class="' + net_td_cls + '">' + net_prefix + '$' + f'{net_val:,.2f}' + '</td>'
        '</tr>'
    )
day_table_html = (
    '<table class="day-table">'
    '<thead><tr><th>Date</th><th>Score</th><th>Income</th><th>Expense</th><th>Net</th></tr></thead>'
    '<tbody>' + table_rows + '</tbody>'
    '</table>'
)
st.markdown(section_card("Day-by-Day Breakdown", day_table_html), unsafe_allow_html=True)
