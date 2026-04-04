"""Insights / Analytics page — performance trends and habit tracking."""

import os
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from theme import inject_theme, nav_menu, page_header, metric_card, progress_bar, ACCENT, POS

# ── Constants ────────────────────────────────────────────────────────
DATA_FOLDER = "data"
PLANNER_FILE = os.path.join(DATA_FOLDER, "planner.csv")
PLANNER_COLS = [
    "date", "priority_1", "priority_2", "priority_3",
    "focus_done", "run_done", "income_done", "reflection", "score",
]

# ── Helpers ──────────────────────────────────────────────────────────

def _ensure_columns(path, required_cols):
    if not os.path.exists(path):
        pd.DataFrame(columns=required_cols).to_csv(path, index=False)
        return pd.DataFrame(columns=required_cols)
    df = pd.read_csv(path)
    if list(df.columns) != required_cols:
        df = pd.DataFrame(columns=required_cols)
        df.to_csv(path, index=False)
    return df


@st.cache_data
def load_planner():
    _ensure_columns(PLANNER_FILE, PLANNER_COLS)
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


def compute_streak(df):
    """Current consecutive-day streak where score > 0."""
    if df.empty:
        return 0
    completed = set(df[df["score"] > 0]["date"].astype(str).tolist())
    streak = 0
    check = date.today()
    while str(check) in completed:
        streak += 1
        check -= timedelta(days=1)
    return streak


def compute_habit_streak(df, habit_col):
    """Current consecutive-day streak where *habit_col* is True."""
    if df.empty or habit_col not in df.columns:
        return 0
    completed = set(df[df[habit_col] == True]["date"].astype(str).tolist())
    streak, check = 0, date.today()
    while str(check) in completed:
        streak += 1
        check -= timedelta(days=1)
    return streak


def get_execution_label(score):
    if score == 100:
        return "Fully Completed"
    elif score >= 70:
        return "Strong Progress"
    elif score >= 40:
        return "In Progress"
    else:
        return "Not Started"


# ── Page ─────────────────────────────────────────────────────────────

inject_theme()
nav_menu("Insights")

st.markdown(page_header("Insights", "Performance analytics"), unsafe_allow_html=True)

planner_df = load_planner()

if len(planner_df) < 2:
    st.info("Log at least 2 days to see insights.")
else:
    total_days   = len(planner_df)
    perfect_days = len(planner_df[planner_df["score"] == 100])
    all_time_avg = round(planner_df["score"].mean())
    streak       = compute_streak(planner_df)

    focus_rate  = round(planner_df["focus_done"].sum() / total_days * 100)
    run_rate    = round(planner_df["run_done"].sum()   / total_days * 100)
    income_rate = round(planner_df["income_done"].sum()/ total_days * 100)

    focus_streak  = compute_habit_streak(planner_df, "focus_done")
    run_streak    = compute_habit_streak(planner_df, "run_done")
    income_streak = compute_habit_streak(planner_df, "income_done")

    # ── Stat cards ───────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card("Days Logged", str(total_days)), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Perfect Days", str(perfect_days)), unsafe_allow_html=True)
    with c3:
        st.markdown(
            metric_card("All-Time Avg", f'{all_time_avg}<span style="font-size:1rem;opacity:.45">/100</span>'),
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            metric_card("Current Streak", str(streak), sub="consecutive days"),
            unsafe_allow_html=True,
        )

    # ── Score trend ──────────────────────────────────────────────────
    st.markdown('<div class="section-label">Score over time</div>', unsafe_allow_html=True)
    chart_df = planner_df.sort_values("date")[["date", "score"]].set_index("date")
    st.area_chart(chart_df, height=220)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Habit completion rates ───────────────────────────────────────
    st.markdown('<div class="section-label">Habit completion rates</div>', unsafe_allow_html=True)
    hc1, hc2, hc3 = st.columns(3, gap="medium")
    for col, name, pct in [
        (hc1, "All Priorities", focus_rate),
        (hc2, "Run",            run_rate),
        (hc3, "Income Target",  income_rate),
    ]:
        with col:
            st.markdown(
                f'<div class="card">'
                f'<div class="metric-label">{name}</div>'
                f'<div class="metric-value" style="color:{POS}">{pct}%</div>'
                f'{progress_bar(pct, POS)}'
                f'<div style="font-size:12px;opacity:.5;margin-top:7px">{pct}% of days</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Habit streaks ────────────────────────────────────────────────
    st.markdown('<div class="section-label">Current habit streaks</div>', unsafe_allow_html=True)
    hs1, hs2, hs3 = st.columns(3, gap="medium")
    for col, name, streak_val in [
        (hs1, "Priorities", focus_streak),
        (hs2, "Run",        run_streak),
        (hs3, "Income",     income_streak),
    ]:
        with col:
            st.markdown(
                metric_card(f"{name} Streak", str(streak_val), sub="consecutive days"),
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Last 7 days table ────────────────────────────────────────────
    st.markdown('<div class="section-label">Last 7 days</div>', unsafe_allow_html=True)
    week_ago = str(date.today() - timedelta(days=6))
    week_df  = planner_df[planner_df["date"] >= week_ago].sort_values("date")

    if week_df.empty:
        st.info("No entries in the last 7 days.")
    else:
        rows_html = ""
        for _, row in week_df.iterrows():
            score = int(row["score"])
            label = get_execution_label(score)
            score_color = POS if score >= 70 else (ACCENT if score >= 40 else "var(--text2)")
            rows_html += (
                f'<tr>'
                f'<td>{row["date"]}</td>'
                f'<td><div class="progress-track" style="width:100%">'
                f'<div class="progress-fill" style="width:{score}%;background:{score_color}"></div>'
                f'</div></td>'
                f'<td style="font-weight:600">{score}/100</td>'
                f'<td>{label}</td>'
                f'</tr>'
            )

        st.markdown(
            f'<table class="day-table">'
            f'<thead><tr><th>Date</th><th>Progress</th><th>Score</th><th>Status</th></tr></thead>'
            f'<tbody>{rows_html}</tbody>'
            f'</table>',
            unsafe_allow_html=True,
        )
