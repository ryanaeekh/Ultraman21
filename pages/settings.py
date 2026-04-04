"""Settings page -- goals, targets, budgets, checklist, export."""

import pandas as pd
import streamlit as st

from theme import inject_theme, nav_menu, page_header, ACCENT
from utils import (
    load_settings, load_planner, save_settings_df, save_planner_df,
    PLANNER_COLUMNS, SETTINGS_COLUMNS, clean_text,
)

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide", initial_sidebar_state="collapsed")

DEFAULT_SETTINGS = {
    "long_term_goals": "",
    "daily_income_target": 250,
    "hourly_rate_target": 30,
    "daily_budget": 50,
    "monthly_budget": 1500,
    "checklist_items": "Wake on time,Read 10 pages,Meditate",
    "expense_categories": "Food,Transport,Bills,Shopping,Health,Family,Other",
}


@st.cache_data(ttl=15)
def _load_settings():
    df = load_settings()
    if df.empty:
        df = pd.DataFrame([DEFAULT_SETTINGS])
    return df


@st.cache_data(ttl=15)
def _load_planner():
    return load_planner()


def _invalidate():
    _load_settings.clear()
    _load_planner.clear()


def save_settings(df: pd.DataFrame):
    save_settings_df(df)
    _invalidate()


def _safe_float(df, col, default):
    if col in df.columns and not df.empty:
        try:
            return float(df.loc[0, col])
        except (ValueError, TypeError):
            pass
    return default


inject_theme()
nav_menu("Settings")

st.markdown(page_header("Settings", "Goals, targets, data export, and reset"), unsafe_allow_html=True)

settings_df = _load_settings()
saved_goals = clean_text(settings_df.loc[0, "long_term_goals"]) if not settings_df.empty else ""

s_left, s_right = st.columns([1.1, 0.9], gap="large")

with s_left:
    st.markdown('<div class="section-label">Long-term Goals</div>', unsafe_allow_html=True)
    with st.form("settings_goals_form"):
        long_term_goals = st.text_area(
            "Your goals", value=saved_goals, height=280,
            placeholder="Write the future you are building toward...",
            label_visibility="collapsed",
        )
        if st.form_submit_button("Save Goals", use_container_width=True):
            settings_df.loc[0, "long_term_goals"] = long_term_goals
            save_settings(settings_df)
            st.success("Goals saved.")
            st.rerun()

with s_right:
    # -- Export --
    st.markdown('<div class="section-label">Data Export</div>', unsafe_allow_html=True)
    planner_df = _load_planner()
    csv = planner_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Export planner data as CSV",
        data=csv, file_name="planner21_export.csv",
        mime="text/csv", use_container_width=True,
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # -- Danger Zone --
    st.markdown('<div class="section-label">Danger Zone</div>', unsafe_allow_html=True)
    confirm = st.text_input("Type DELETE to confirm reset", placeholder="DELETE")
    if st.button("Clear all planner data", use_container_width=True):
        if confirm == "DELETE":
            save_planner_df(pd.DataFrame(columns=PLANNER_COLUMNS))
            _invalidate()
            st.success("Planner data cleared.")
            st.rerun()
        else:
            st.error("Type DELETE to confirm.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # -- Targets --
    st.markdown('<div class="section-label">Targets</div>', unsafe_allow_html=True)
    with st.form("targets_form"):
        income_target = st.number_input("Daily Income Target ($)", min_value=0.0, value=_safe_float(settings_df, "daily_income_target", 250.0), step=10.0)
        rate_target = st.number_input("Hourly Rate Target ($/hr)", min_value=0.0, value=_safe_float(settings_df, "hourly_rate_target", 30.0), step=5.0)
        if st.form_submit_button("Save Targets", use_container_width=True):
            settings_df.loc[0, "daily_income_target"] = income_target
            settings_df.loc[0, "hourly_rate_target"] = rate_target
            save_settings(settings_df)
            st.success("Targets saved.")
            st.rerun()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # -- Budget Limits --
    st.markdown('<div class="section-label">Budget Limits</div>', unsafe_allow_html=True)
    with st.form("budget_form"):
        daily_budget = st.number_input("Daily Spending Limit ($)", min_value=0.0, value=_safe_float(settings_df, "daily_budget", 50.0), step=5.0)
        monthly_budget = st.number_input("Monthly Spending Limit ($)", min_value=0.0, value=_safe_float(settings_df, "monthly_budget", 1500.0), step=50.0)
        if st.form_submit_button("Save Budgets", use_container_width=True):
            settings_df.loc[0, "daily_budget"] = daily_budget
            settings_df.loc[0, "monthly_budget"] = monthly_budget
            save_settings(settings_df)
            st.success("Budgets saved.")
            st.rerun()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # -- Morning Checklist --
    st.markdown('<div class="section-label">Morning Checklist</div>', unsafe_allow_html=True)
    current_checklist = ""
    if "checklist_items" in settings_df.columns and not settings_df.empty:
        current_checklist = str(settings_df.loc[0, "checklist_items"]).strip()
        if current_checklist.lower() == "nan":
            current_checklist = "Wake on time,Read 10 pages,Meditate"
    with st.form("checklist_form"):
        checklist_input = st.text_area("Checklist items (comma-separated)", value=current_checklist, height=80)
        if st.form_submit_button("Save Checklist", use_container_width=True):
            settings_df.loc[0, "checklist_items"] = checklist_input.strip()
            save_settings(settings_df)
            st.success("Checklist saved.")
            st.rerun()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # -- Expense Categories --
    st.markdown('<div class="section-label">Expense Categories</div>', unsafe_allow_html=True)
    current_categories = ""
    if "expense_categories" in settings_df.columns and not settings_df.empty:
        current_categories = str(settings_df.loc[0, "expense_categories"]).strip()
        if current_categories.lower() == "nan":
            current_categories = "Food,Transport,Bills,Shopping,Health,Family,Other"
    with st.form("categories_form"):
        categories_input = st.text_input("Expense categories (comma-separated)", value=current_categories)
        if st.form_submit_button("Save Categories", use_container_width=True):
            settings_df.loc[0, "expense_categories"] = categories_input.strip()
            save_settings(settings_df)
            st.success("Categories saved.")
            st.rerun()
