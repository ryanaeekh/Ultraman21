import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Settings", page_icon="\u2699\ufe0f", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header
from utils import load_settings, save_settings_df, SETTINGS_COLUMNS, clean_text

inject_theme()
nav_menu("Settings")

st.markdown(page_header("Settings", "Tune your system"), unsafe_allow_html=True)

settings_df = load_settings()
if settings_df.empty:
    settings_df = pd.DataFrame([{c: "" for c in SETTINGS_COLUMNS}])

def s_get(key, default=""):
    if key in settings_df.columns and not settings_df.empty:
        return clean_text(settings_df.loc[0, key]) or default
    return default

def s_float(key, default=0.0):
    raw = s_get(key, "")
    try:
        return float(raw) if raw != "" else default
    except Exception:
        return default

def s_set(key, value):
    global settings_df
    if key not in settings_df.columns:
        settings_df[key] = ""
    settings_df.loc[0, key] = value

# ── Goals ─────────────────────────────────────────────────
st.markdown('<div class="section-title">\u2728 Long Term Goals</div>', unsafe_allow_html=True)
goals_val = st.text_area("Goals", value=s_get("long_term_goals"), height=180, key="ss_goals",
                         placeholder="Write the goals that guide everything else.")
if st.button("Save Goals", use_container_width=True, key="save_goals"):
    s_set("long_term_goals", goals_val.strip())
    save_settings_df(settings_df)
    st.success("Goals saved.")
    st.rerun()

st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

# ── Targets ───────────────────────────────────────────────
st.markdown('<div class="section-title">\U0001f3af Daily & Monthly Targets</div>', unsafe_allow_html=True)
t_cols = st.columns(3)
with t_cols[0]:
    income_target = st.number_input("Daily Income Target (\u00a3)", min_value=0.0, step=10.0, format="%.2f",
                                     value=s_float("daily_income_target"), key="ss_income_target")
with t_cols[1]:
    daily_budget = st.number_input("Daily Budget (\u00a3)", min_value=0.0, step=5.0, format="%.2f",
                                    value=s_float("daily_budget"), key="ss_daily_budget")
with t_cols[2]:
    monthly_budget = st.number_input("Monthly Budget (\u00a3)", min_value=0.0, step=50.0, format="%.2f",
                                      value=s_float("monthly_budget"), key="ss_monthly_budget")
if st.button("Save Targets", use_container_width=True, key="save_targets"):
    s_set("daily_income_target", str(income_target))
    s_set("daily_budget", str(daily_budget))
    s_set("monthly_budget", str(monthly_budget))
    save_settings_df(settings_df)
    st.success("Targets saved.")
    st.rerun()

st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

# ── Expense Categories ────────────────────────────────────
st.markdown('<div class="section-title">\U0001f3f7\ufe0f Expense Categories</div>', unsafe_allow_html=True)
cats_raw = s_get("expense_categories", "Food, Transport, Shopping, Bills, Health, Entertainment, Other")
cats = [c.strip() for c in cats_raw.split(",") if c.strip()]

if cats:
    tag_html = '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;">'
    for c in cats:
        tag_html += (
            f'<span style="padding:6px 14px;border-radius:999px;background:var(--accent-soft);'
            f'border:1px solid var(--border);color:var(--text);font-size:13px;">{c}</span>'
        )
    tag_html += '</div>'
    st.markdown(tag_html, unsafe_allow_html=True)

new_cats = st.text_input("Categories (comma-separated)", value=cats_raw, key="ss_cats")
if st.button("Save Categories", use_container_width=True, key="save_cats"):
    s_set("expense_categories", new_cats.strip())
    save_settings_df(settings_df)
    st.success("Categories saved.")
    st.rerun()

st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

# ── Checklist Items ───────────────────────────────────────
st.markdown('<div class="section-title">\u2611\ufe0f Morning Checklist</div>', unsafe_allow_html=True)
chk_raw = s_get("checklist_items")
new_chk = st.text_area("Items (one per line)", value="\n".join([i.strip() for i in chk_raw.split(",") if i.strip()]),
                       height=140, key="ss_chk")
if st.button("Save Checklist", use_container_width=True, key="save_chk"):
    items = [i.strip() for i in new_chk.split("\n") if i.strip()]
    s_set("checklist_items", ",".join(items))
    save_settings_df(settings_df)
    st.success("Checklist saved.")
    st.rerun()
