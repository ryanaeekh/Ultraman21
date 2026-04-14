import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import os
from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Mission 21", page_icon="\U0001f3af", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header, metric_card, status_badge, progress_bar, ACCENT, POS, NEG
from utils import (
    load_planner, load_settings, save_planner_df, save_settings_df,
    PLANNER_COLUMNS, SETTINGS_COLUMNS, clean_text,
)

inject_theme()
nav_menu("Mission 21")

today = str(date.today())

# =========================================================
# DATA HELPERS  (cached -- invalidated after writes)
# =========================================================
@st.cache_data(ttl=15)
def _load_planner():
    df = load_planner()
    if "date" in df.columns:
        df["date"] = df["date"].astype(str)
    return df


@st.cache_data(ttl=15)
def _load_settings():
    return load_settings()


def invalidate_cache():
    _load_planner.clear()
    _load_settings.clear()


def save_planner(df: pd.DataFrame):
    save_planner_df(df)
    invalidate_cache()


def save_settings(df: pd.DataFrame):
    save_settings_df(df)
    invalidate_cache()


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
planner_df = _load_planner()
settings_df = _load_settings()
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
st.markdown(page_header("Ryan", f"{today} \u2014 build the day deliberately"), unsafe_allow_html=True)

# --- Focus heading ---
st.markdown('<h1 style="text-align:center;margin:20px 0;letter-spacing:0.15em;">FOCUS</h1>', unsafe_allow_html=True)

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
