import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Mission 21", page_icon="\U0001f3af", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header
from utils import load_planner, load_settings, clean_text

inject_theme()
nav_menu("Mission 21")

today = date.today()
today_str = str(today)

planner_df = load_planner()
settings_df = load_settings()

row = planner_df[planner_df["date"] == today_str]
today_row = row.iloc[0] if not row.empty else None

today_score = int(today_row["score"]) if today_row is not None else 0
focus_done = bool(today_row["focus_done"]) if today_row is not None else False
run_done = bool(today_row["run_done"]) if today_row is not None else False
income_done = bool(today_row["income_done"]) if today_row is not None else False

saved_goals = ""
if not settings_df.empty and "long_term_goals" in settings_df.columns:
    saved_goals = clean_text(settings_df.loc[0, "long_term_goals"])

# ── Hero ──────────────────────────────────────────────────
st.markdown(page_header("Ryan", "Your daily operating system"), unsafe_allow_html=True)

pretty_date = today.strftime("%-d %B %Y \u2022 %A") if os.name != "nt" else today.strftime("%#d %B %Y \u2022 %A")
st.markdown(f'<div style="margin:-4px 0 28px;"><span class="date-pill">{pretty_date}</span></div>', unsafe_allow_html=True)

# ── Focus heading ─────────────────────────────────────────
st.markdown('''
<div style="text-align:center;margin:32px auto 28px;max-width:720px;padding:0 16px;">
  <h1 style="color:#000000 !important;font-family:var(--font-display);
             font-size:34px;font-weight:700;letter-spacing:-0.01em;
             margin:0;line-height:1.25;">\u201cThe only limits in life are the one you make\u201d</h1>
</div>
''', unsafe_allow_html=True)

# ── Execution Pills ───────────────────────────────────────
pills = [("Priorities", focus_done), ("Attention", run_done), ("System", income_done)]
seg_html = '<div class="seg-row" style="margin-top:24px;">'
for label, done in pills:
    cls = "seg-pill active" if done else "seg-pill"
    seg_html += f'<div class="{cls}">{label}</div>'
seg_html += '</div>'
st.markdown(seg_html, unsafe_allow_html=True)

# ── Long Term Goals ───────────────────────────────────────
if saved_goals:
    goals_body = saved_goals.replace("\n", "<br>")
    st.markdown(f'''
    <div class="card accent-left-card" style="margin-top:22px;text-align:center;">
      <div class="section-title" style="justify-content:center;">\u2728 Long Term Goals</div>
      <div style="font-size:15px;line-height:1.9;color:var(--text);opacity:0.92;">{goals_body}</div>
    </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown('''
    <div class="card" style="margin-top:22px;text-align:center;">
      <div class="section-title">\u2728 Long Term Goals</div>
      <div style="font-size:14px;color:var(--text2);opacity:0.75;">
        No goals set yet \u2014 visit Settings to add them.
      </div>
    </div>
    ''', unsafe_allow_html=True)

# ── Bruce Lee Quote ───────────────────────────────────────
quote_text = (
    "Because you might as well be dead. Seriously, if you always put limits on everything you do, "
    "physical or anything else, it'll spread over into the rest of your life. It'll spread into your work, "
    "into your morality, into your entire being. "
    "There are no limits. There are only plateaus, and you must not stay there, you must go beyond them. "
    "If it kills you, it kills you. A man must constantly exceed his level."
)
st.markdown(f'''
<div class="card" style="margin-top:22px;">
  <div class="quote-block">
    {quote_text}
    <span class="quote-author">Bruce Lee</span>
  </div>
</div>
''', unsafe_allow_html=True)
