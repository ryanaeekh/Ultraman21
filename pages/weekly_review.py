import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Weekly Review", page_icon="\U0001f4c6", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header, metric_card
from utils import load_finance, load_exercise, load_planner

inject_theme()
nav_menu("Weekly Review")

today = date.today()
week_start = today - timedelta(days=6)

st.markdown(page_header("Weekly Review", f"{week_start.strftime('%d %b')} \u2014 {today.strftime('%d %b %Y')}"), unsafe_allow_html=True)

finance_df = load_finance()
exercise_df = load_exercise()
planner_df = load_planner()

def _in_week(df, col="date"):
    if df.empty:
        return df
    temp = df.copy()
    temp[col] = pd.to_datetime(temp[col], errors="coerce")
    mask = (temp[col].dt.date >= week_start) & (temp[col].dt.date <= today)
    return temp[mask]

fin_week = _in_week(finance_df)
week_income = float(fin_week[fin_week["category"] == "Income"]["amount"].sum()) if not fin_week.empty else 0.0
week_exp = float(fin_week[fin_week["category"] != "Income"]["amount"].sum()) if not fin_week.empty else 0.0
week_net = week_income - week_exp

ex_week = _in_week(exercise_df)
ex_count = int(len(ex_week[ex_week["status"].astype(str).str.lower() == "done"])) if not ex_week.empty else 0

# ── Top metrics ───────────────────────────────────────────
g1 = st.columns(2)
with g1[0]:
    st.markdown(metric_card("Week Income", f"${week_income:,.2f}", color="var(--accent-2)"), unsafe_allow_html=True)
with g1[1]:
    st.markdown(metric_card("Week Expenses", f"${week_exp:,.2f}", color="var(--neg)"), unsafe_allow_html=True)

g2 = st.columns(2)
with g2[0]:
    net_color = "var(--accent-2)" if week_net >= 0 else "var(--neg)"
    st.markdown(metric_card("Net", f"${week_net:,.2f}", color=net_color), unsafe_allow_html=True)
with g2[1]:
    st.markdown(metric_card("Exercise", f"{ex_count}", sub="sessions done", color="var(--accent-2)"), unsafe_allow_html=True)

# ── Day-by-day ────────────────────────────────────────────
st.markdown('<div class="section-title">\U0001f5d3\ufe0f Day by Day</div>', unsafe_allow_html=True)

planner_week = _in_week(planner_df)
day_scores = {}
if not planner_week.empty:
    for _, r in planner_week.iterrows():
        d = r["date"].date() if hasattr(r["date"], "date") else pd.to_datetime(r["date"]).date()
        day_scores[d] = int(r["score"])

def score_ring_inline(score):
    return (
        f'<div style="width:52px;height:52px;border-radius:50%;'
        f'background:conic-gradient(#B8E3E9 0deg,#4F7C82 {score*3.6}deg,rgba(184,227,233,0.08) 0deg);'
        f'display:flex;align-items:center;justify-content:center;position:relative;">'
        f'<div style="position:absolute;inset:5px;border-radius:50%;background:#0e3a40;'
        f'display:flex;align-items:center;justify-content:center;">'
        f'<span style="font-family:var(--font-display);font-size:15px;font-weight:700;color:var(--text);">{score}</span>'
        f'</div></div>'
    )

rows_html = ""
for i in range(7):
    d = week_start + timedelta(days=i)
    score = day_scores.get(d, 0)
    rows_html += (
        f'<div class="list-row" style="padding:12px 18px;">'
        f'<div><div style="font-family:var(--font-display);font-size:13px;letter-spacing:0.1em;text-transform:uppercase;color:var(--text2);">{d.strftime("%a")}</div>'
        f'<div style="font-size:14px;color:var(--text);margin-top:4px;">{d.strftime("%d %b")}</div></div>'
        f'{score_ring_inline(score)}</div>'
    )
st.markdown(rows_html, unsafe_allow_html=True)

# ── Average score ─────────────────────────────────────────
avg_score = round(float(planner_week["score"].mean()) if not planner_week.empty else 0.0)
st.markdown(
    f'<div class="card" style="margin-top:22px;text-align:center;">'
    f'<div class="section-title" style="margin-bottom:10px;">\U0001f31f Average Score</div>'
    f'<div class="metric-value" style="font-size:64px;color:var(--text);">{avg_score}</div>'
    f'<div class="metric-sub">over the last 7 days</div>'
    f'</div>',
    unsafe_allow_html=True,
)
