"""Settings page -- goals, targets, budgets, checklist, export, and backup restore."""

import os
import shutil

import pandas as pd
import streamlit as st

from theme import inject_theme, nav_menu, page_header, ACCENT
from utils import backup_csv, clean_text

# ─── Constants ───────────────────────────────────────────────────────
DATA_FOLDER = "data"
PLANNER_FILE = os.path.join(DATA_FOLDER, "planner.csv")
SETTINGS_FILE = os.path.join(DATA_FOLDER, "settings.csv")
BACKUP_FOLDER = os.path.join(DATA_FOLDER, "backups")

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

PLANNER_COLS = [
    "date", "priority_1", "priority_2", "priority_3",
    "focus_done", "run_done", "income_done", "reflection", "score",
]
SETTINGS_COLS = [
    "long_term_goals", "daily_income_target", "hourly_rate_target",
    "daily_budget", "monthly_budget", "checklist_items", "expense_categories",
]

DEFAULT_SETTINGS = {
    "long_term_goals": "",
    "daily_income_target": 250,
    "hourly_rate_target": 30,
    "daily_budget": 50,
    "monthly_budget": 1500,
    "checklist_items": "Wake on time,Read 10 pages,Meditate",
    "expense_categories": "Food,Transport,Bills,Shopping,Health,Family,Other",
}

# ─── File bootstrap ─────────────────────────────────────────────────
if not os.path.exists(PLANNER_FILE):
    pd.DataFrame(columns=PLANNER_COLS).to_csv(PLANNER_FILE, index=False)

if not os.path.exists(SETTINGS_FILE):
    pd.DataFrame([DEFAULT_SETTINGS]).to_csv(SETTINGS_FILE, index=False)


# ─── Helpers ─────────────────────────────────────────────────────────
@st.cache_data
def load_settings():
    return pd.read_csv(SETTINGS_FILE)


@st.cache_data
def load_planner():
    return pd.read_csv(PLANNER_FILE)


def invalidate_cache():
    load_settings.clear()
    load_planner.clear()


def save_settings(df: pd.DataFrame):
    backup_csv(SETTINGS_FILE)
    df.to_csv(SETTINGS_FILE, index=False)
    invalidate_cache()


def _safe_float(df, col, default):
    """Safely read a float value from the first row of a settings DataFrame."""
    if col in df.columns and not df.empty:
        try:
            return float(df.loc[0, col])
        except (ValueError, TypeError):
            pass
    return default


# ─── Page ────────────────────────────────────────────────────────────
inject_theme()
nav_menu("Settings")

st.markdown(page_header("Settings", "Goals, targets, data export, and reset"), unsafe_allow_html=True)

settings_df = load_settings()
saved_goals = clean_text(settings_df.loc[0, "long_term_goals"]) if not settings_df.empty else ""

s_left, s_right = st.columns([1.1, 0.9], gap="large")

# ── Left column: Goals ───────────────────────────────────────────────
with s_left:
    st.markdown('<div class="section-label">Long-term Goals</div>', unsafe_allow_html=True)
    with st.form("settings_goals_form"):
        long_term_goals = st.text_area(
            "Your goals",
            value=saved_goals,
            height=280,
            placeholder="Write the future you are building toward...",
            label_visibility="collapsed",
        )
        if st.form_submit_button("Save Goals", use_container_width=True):
            settings_df.loc[0, "long_term_goals"] = long_term_goals
            save_settings(settings_df)
            st.success("Goals saved.")
            st.rerun()

# ── Right column: everything else ────────────────────────────────────
with s_right:
    # -- Export --
    st.markdown('<div class="section-label">Data Export</div>', unsafe_allow_html=True)
    planner_df = load_planner()
    csv = planner_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Export planner data as CSV",
        data=csv,
        file_name="planner21_export.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # -- Danger Zone --
    st.markdown('<div class="section-label">Danger Zone</div>', unsafe_allow_html=True)
    confirm = st.text_input("Type DELETE to confirm reset", placeholder="DELETE")
    if st.button("Clear all planner data", use_container_width=True):
        if confirm == "DELETE":
            pd.DataFrame(columns=PLANNER_COLS).to_csv(PLANNER_FILE, index=False)
            invalidate_cache()
            st.success("Planner data cleared.")
            st.rerun()
        else:
            st.error("Type DELETE to confirm.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # -- Targets --
    st.markdown('<div class="section-label">Targets</div>', unsafe_allow_html=True)
    with st.form("targets_form"):
        current_income_target = _safe_float(settings_df, "daily_income_target", 250.0)
        current_rate_target = _safe_float(settings_df, "hourly_rate_target", 30.0)
        income_target = st.number_input(
            "Daily Income Target ($)", min_value=0.0, value=current_income_target, step=10.0,
        )
        rate_target = st.number_input(
            "Hourly Rate Target ($/hr)", min_value=0.0, value=current_rate_target, step=5.0,
        )
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
        current_daily_budget = _safe_float(settings_df, "daily_budget", 50.0)
        current_monthly_budget = _safe_float(settings_df, "monthly_budget", 1500.0)
        daily_budget = st.number_input(
            "Daily Spending Limit ($)", min_value=0.0, value=current_daily_budget, step=5.0,
        )
        monthly_budget = st.number_input(
            "Monthly Spending Limit ($)", min_value=0.0, value=current_monthly_budget, step=50.0,
        )
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
        checklist_input = st.text_area(
            "Checklist items (comma-separated)",
            value=current_checklist,
            placeholder="Wake on time, Read 10 pages, Meditate",
            height=80,
        )
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
        categories_input = st.text_input(
            "Expense categories (comma-separated)",
            value=current_categories,
            placeholder="Food, Transport, Bills, Shopping, Health, Family, Other",
        )
        if st.form_submit_button("Save Categories", use_container_width=True):
            settings_df.loc[0, "expense_categories"] = categories_input.strip()
            save_settings(settings_df)
            st.success("Categories saved.")
            st.rerun()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # -- Restore from Backup --
    st.markdown('<div class="section-label">Restore from Backup</div>', unsafe_allow_html=True)
    if os.path.exists(BACKUP_FOLDER):
        backups = sorted(
            [f for f in os.listdir(BACKUP_FOLDER) if f.endswith(".csv")],
            reverse=True,
        )
        if backups:
            selected_backup = st.selectbox("Select backup", backups[:20])
            if st.button("Restore selected backup"):
                for prefix in [
                    "planner", "settings", "driving", "finance",
                    "monthly_expenses", "exercise", "journal",
                ]:
                    if selected_backup.startswith(prefix):
                        target = os.path.join(DATA_FOLDER, f"{prefix}.csv")
                        shutil.copy2(
                            os.path.join(BACKUP_FOLDER, selected_backup), target,
                        )
                        invalidate_cache()
                        st.success(f"Restored {prefix}.csv from {selected_backup}")
                        st.rerun()
                        break
        else:
            st.info("No backups found yet.")
    else:
        st.info("Backup directory not created yet.")
