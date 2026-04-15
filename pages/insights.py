import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Insights", page_icon="\U0001f4c8", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header, metric_card
from utils import load_planner

inject_theme()
nav_menu("Insights")

st.markdown(page_header("Insights", "Patterns, not pressure"), unsafe_allow_html=True)

planner_df = load_planner()

if planner_df.empty:
    st.markdown('<div class="card" style="text-align:center;opacity:0.7;">No planner data yet.</div>', unsafe_allow_html=True)
    st.stop()

planner_df = planner_df.copy()
planner_df["date_parsed"] = pd.to_datetime(planner_df["date"], errors="coerce")
planner_df = planner_df.dropna(subset=["date_parsed"]).sort_values("date_parsed")

# ── Metrics ───────────────────────────────────────────────
days_logged = int(planner_df["score"].gt(0).sum())
perfect_days = int(planner_df["score"].eq(100).sum())

completed = set(planner_df[planner_df["score"] > 0]["date"].astype(str).tolist())
streak, check = 0, date.today()
while str(check) in completed:
    streak += 1
    check -= timedelta(days=1)

cols = st.columns(3)
with cols[0]:
    st.markdown(metric_card("Days Logged", f"{days_logged}", color="var(--accent-2)"), unsafe_allow_html=True)
with cols[1]:
    st.markdown(metric_card("Perfect Days", f"{perfect_days}", sub="100 / 100", color="var(--accent-2)"), unsafe_allow_html=True)
with cols[2]:
    st.markdown(metric_card("Current Streak", f"\U0001f525 {streak}", sub="consecutive days", color="var(--accent-2)"), unsafe_allow_html=True)

# ── Score Trend ───────────────────────────────────────────
st.markdown('<div class="section-title">\U0001f4c9 Score Trend</div>', unsafe_allow_html=True)
recent = planner_df.tail(30).copy()
chart_df = recent[["date_parsed", "score"]].rename(columns={"date_parsed": "Date", "score": "Score"}).set_index("Date")

import altair as alt
chart_data = chart_df.reset_index()
area = alt.Chart(chart_data).mark_area(
    line={"color": "#7fbcc4", "strokeWidth": 2},
    color=alt.Gradient(
        gradient="linear",
        stops=[
            alt.GradientStop(color="rgba(79,124,130,0.45)", offset=0),
            alt.GradientStop(color="rgba(79,124,130,0.02)", offset=1),
        ],
        x1=1, x2=1, y1=1, y2=0,
    ),
).encode(
    x=alt.X("Date:T", axis=alt.Axis(labelColor="#7fbcc4", tickColor="#4F7C82", grid=False)),
    y=alt.Y("Score:Q", scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(labelColor="#7fbcc4", tickColor="#4F7C82", gridColor="rgba(79,124,130,0.15)")),
).properties(height=260)
points = alt.Chart(chart_data).mark_point(filled=True, size=70, color="#B8E3E9", stroke="#7fbcc4").encode(
    x="Date:T", y="Score:Q"
)
st.altair_chart(area + points, use_container_width=True)

# ── Habit Completion Rates ────────────────────────────────
st.markdown('<div class="section-title">\U0001f3af Habit Completion</div>', unsafe_allow_html=True)
total = len(planner_df)
priorities_pct = round(100 * planner_df["focus_done"].sum() / total) if total else 0
attention_pct = round(100 * planner_df["run_done"].sum() / total) if total else 0
system_pct = round(100 * planner_df["income_done"].sum() / total) if total else 0

def habit_row(label, pct):
    return (
        f'<div class="card" style="padding:20px 22px;margin-bottom:12px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">'
        f'<span style="font-family:var(--font-display);font-size:13px;letter-spacing:0.12em;text-transform:uppercase;color:var(--text2);">{label}</span>'
        f'<span class="glow-badge" style="padding:4px 12px;font-size:12px;">{pct}%</span>'
        f'</div>'
        f'<div style="height:8px;border-radius:4px;background:rgba(184,227,233,0.08);overflow:hidden;">'
        f'<div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#4F7C82,#B8E3E9);box-shadow:0 0 12px rgba(79,124,130,0.45);"></div>'
        f'</div></div>'
    )

st.markdown(habit_row("Priorities", priorities_pct), unsafe_allow_html=True)
st.markdown(habit_row("Attention", attention_pct), unsafe_allow_html=True)
st.markdown(habit_row("System", system_pct), unsafe_allow_html=True)
