import os
from datetime import date
import calendar

import pandas as pd
import streamlit as st
from theme import inject_theme, nav_menu, page_header, detail_row, section_card, status_badge, ACCENT, POS, NEG
from utils import clean_text, safe_float, backup_csv

st.set_page_config(page_title="Finance", page_icon="💰", layout="wide", initial_sidebar_state="collapsed")

# =========================================================
# PATHS
# =========================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

SETTINGS_FILE = os.path.join(DATA_DIR, "settings.csv")
FINANCE_FILE = os.path.join(DATA_DIR, "finance.csv")
DRIVING_FILE = os.path.join(DATA_DIR, "driving.csv")
MONTHLY_FILE = os.path.join(DATA_DIR, "monthly_expenses.csv")

os.makedirs(DATA_DIR, exist_ok=True)

BACKUP_FOLDER = os.path.join(DATA_DIR, "backups")
os.makedirs(BACKUP_FOLDER, exist_ok=True)

DAILY_BUDGET = 50.0
MONTHLY_BUDGET = 1500.0
if os.path.exists(SETTINGS_FILE):
    try:
        _settings = pd.read_csv(SETTINGS_FILE)
        if "daily_budget" in _settings.columns and not _settings.empty:
            DAILY_BUDGET = float(_settings.loc[0, "daily_budget"])
        if "monthly_budget" in _settings.columns and not _settings.empty:
            MONTHLY_BUDGET = float(_settings.loc[0, "monthly_budget"])
    except Exception:
        pass

DEFAULT_CATEGORIES = ["Food", "Transport", "Bills", "Shopping", "Health", "Family", "Other"]
EXPENSE_CATEGORIES = DEFAULT_CATEGORIES[:]
if os.path.exists(SETTINGS_FILE):
    try:
        _settings = pd.read_csv(SETTINGS_FILE)
        if "expense_categories" in _settings.columns and not _settings.empty:
            raw = str(_settings.loc[0, "expense_categories"]).strip()
            if raw and raw.lower() != "nan":
                EXPENSE_CATEGORIES = [c.strip() for c in raw.split(",") if c.strip()]
    except Exception:
        pass

# =========================================================
# REQUIRED COLUMNS
# =========================================================
finance_required_columns = [
    "date",
    "category",
    "amount",
]

monthly_required_columns = [
    "name",
    "amount",
]

# =========================================================
# FILE SETUP
# =========================================================
if not os.path.exists(FINANCE_FILE):
    pd.DataFrame(columns=finance_required_columns).to_csv(FINANCE_FILE, index=False)

if not os.path.exists(MONTHLY_FILE):
    pd.DataFrame(columns=monthly_required_columns).to_csv(MONTHLY_FILE, index=False)

# IMPORTANT:
# Never reset or overwrite driving.csv from finance.py
if not os.path.exists(DRIVING_FILE):
    pd.DataFrame(columns=["date", "earnings"]).to_csv(DRIVING_FILE, index=False)

finance_df = pd.read_csv(FINANCE_FILE)
monthly_df = pd.read_csv(MONTHLY_FILE)

if list(finance_df.columns) != finance_required_columns:
    finance_df = pd.DataFrame(columns=finance_required_columns)
    finance_df.to_csv(FINANCE_FILE, index=False)

if list(monthly_df.columns) != monthly_required_columns:
    monthly_df = pd.DataFrame(columns=monthly_required_columns)
    monthly_df.to_csv(MONTHLY_FILE, index=False)

# =========================================================
# HELPERS
# =========================================================
def save_finance(df):
    backup_csv(FINANCE_FILE)
    df.to_csv(FINANCE_FILE, index=False)


def save_monthly(df):
    backup_csv(MONTHLY_FILE)
    df.to_csv(MONTHLY_FILE, index=False)


def load_finance():
    if not os.path.exists(FINANCE_FILE):
        return pd.DataFrame(columns=finance_required_columns)
    try:
        df = pd.read_csv(FINANCE_FILE)
        if df.empty:
            return pd.DataFrame(columns=finance_required_columns)
        return df
    except Exception:
        return pd.DataFrame(columns=finance_required_columns)


def load_monthly():
    if not os.path.exists(MONTHLY_FILE):
        return pd.DataFrame(columns=monthly_required_columns)
    try:
        df = pd.read_csv(MONTHLY_FILE)
        if df.empty:
            return pd.DataFrame(columns=monthly_required_columns)
        return df
    except Exception:
        return pd.DataFrame(columns=monthly_required_columns)


def load_driving():
    # Read only. Never reset.
    if not os.path.exists(DRIVING_FILE):
        return pd.DataFrame()
    try:
        df = pd.read_csv(DRIVING_FILE)
        if df.empty:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()


def get_days_in_month(date_str):
    dt = pd.to_datetime(date_str)
    return calendar.monthrange(dt.year, dt.month)[1]


def get_daily_fixed_share(monthly_expenses_df, selected_date_str):
    if monthly_expenses_df.empty:
        return 0.0

    total_monthly = monthly_expenses_df["amount"].apply(safe_float).sum()
    days = get_days_in_month(selected_date_str)

    if days <= 0:
        return 0.0

    return round(total_monthly / days, 2)


def get_driving_income_for_date(driving_data, selected_date_str):
    """
    Your driving.py saves income in:
    - date
    - earnings

    So finance.py should read ONLY those fields safely.
    """
    if driving_data.empty:
        return 0.0

    if "date" not in driving_data.columns:
        return 0.0

    if "earnings" not in driving_data.columns:
        return 0.0

    temp_df = driving_data.copy()
    temp_df["date"] = temp_df["date"].astype(str)
    temp_df["earnings"] = temp_df["earnings"].apply(safe_float)

    day_rows = temp_df[temp_df["date"] == selected_date_str]

    if day_rows.empty:
        return 0.0

    return round(day_rows["earnings"].sum(), 2)


def get_daily_expenses(finance_data, selected_date_str):
    if finance_data.empty:
        return pd.DataFrame(columns=finance_required_columns)

    temp_df = finance_data.copy()
    temp_df["date"] = temp_df["date"].astype(str)
    return temp_df[temp_df["date"] == selected_date_str].copy()


def get_monthly_net(finance_data, monthly_expenses_df, driving_data, selected_date_str):
    """Calculate month-to-date net profit."""
    try:
        dt = pd.to_datetime(selected_date_str)
    except Exception:
        return 0.0

    year, month = dt.year, dt.month
    days_elapsed = dt.day

    # Month income from driving
    if driving_data.empty or "earnings" not in driving_data.columns:
        monthly_income = 0.0
    else:
        temp = driving_data.copy()
        temp["date"] = pd.to_datetime(temp["date"], errors="coerce")
        temp = temp.dropna(subset=["date"])
        mask = (temp["date"].dt.year == year) & (temp["date"].dt.month == month)
        monthly_income = round(temp.loc[mask, "earnings"].apply(safe_float).sum(), 2)

    # Month variable expenses
    if finance_data.empty:
        monthly_var = 0.0
    else:
        temp = finance_data.copy()
        temp["date"] = pd.to_datetime(temp["date"], errors="coerce")
        temp = temp.dropna(subset=["date"])
        mask = (temp["date"].dt.year == year) & (temp["date"].dt.month == month)
        monthly_var = round(temp.loc[mask, "amount"].apply(safe_float).sum(), 2)

    # Fixed share so far this month
    days_in_month = get_days_in_month(selected_date_str)
    monthly_fixed_total = monthly_expenses_df["amount"].apply(safe_float).sum() if not monthly_expenses_df.empty else 0.0
    monthly_fixed_so_far = round(monthly_fixed_total / days_in_month * days_elapsed, 2) if days_in_month > 0 else 0.0

    return round(monthly_income - monthly_var - monthly_fixed_so_far, 2)


def get_summary(finance_data, monthly_expenses_df, driving_data, selected_date_str):
    income = get_driving_income_for_date(driving_data, selected_date_str)

    day_expenses_df = get_daily_expenses(finance_data, selected_date_str)
    variable_expenses = (
        round(day_expenses_df["amount"].apply(safe_float).sum(), 2)
        if not day_expenses_df.empty
        else 0.0
    )

    fixed_share = get_daily_fixed_share(monthly_expenses_df, selected_date_str)
    total_expenses = round(variable_expenses + fixed_share, 2)
    net_profit = round(income - total_expenses, 2)
    monthly_net = get_monthly_net(finance_data, monthly_expenses_df, driving_data, selected_date_str)

    return {
        "income": income,
        "variable_expenses": variable_expenses,
        "fixed_share": fixed_share,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "monthly_net": monthly_net,
    }


# =========================================================
# SESSION STATE
# =========================================================
if "edit_daily_index" not in st.session_state:
    st.session_state.edit_daily_index = None

if "edit_monthly_index" not in st.session_state:
    st.session_state.edit_monthly_index = None

# =========================================================
# INJECT THEME
# =========================================================
inject_theme()
nav_menu("Finance")

# =========================================================
# LOAD DATA
# =========================================================
finance_df = load_finance()
monthly_df = load_monthly()
driving_df = load_driving()

if not finance_df.empty:
    finance_df["date"] = finance_df["date"].astype(str)
    finance_df["category"] = finance_df["category"].astype(str)
    finance_df["amount"] = finance_df["amount"].apply(safe_float)

if not monthly_df.empty:
    monthly_df["name"] = monthly_df["name"].astype(str)
    monthly_df["amount"] = monthly_df["amount"].apply(safe_float)

if not driving_df.empty and "date" in driving_df.columns:
    driving_df["date"] = driving_df["date"].astype(str)

if not driving_df.empty and "earnings" in driving_df.columns:
    driving_df["earnings"] = driving_df["earnings"].apply(safe_float)

# =========================================================
# HEADER
# =========================================================
st.markdown(page_header("Finance", "Track income, daily expenses, and recurring monthly costs"), unsafe_allow_html=True)

# =========================================================
# SELECT DATE
# =========================================================
selected_date = st.date_input("Select Finance Date", value=date.today())
selected_date_str = str(selected_date)

# refresh summary based on selected date
summary = get_summary(finance_df, monthly_df, driving_df, selected_date_str)

# =========================================================
# TOP SUMMARY CARDS
# =========================================================
_net_color = POS if summary["net_profit"] >= 0 else NEG
_mnet_color = POS if summary["monthly_net"] >= 0 else NEG
st.markdown(
    f"""
    <div class="summary-row">
        <div class="summary-card">
            <div class="summary-label">Today Income</div>
            <div class="summary-value">${summary["income"]:.2f}</div>
        </div>
        <div class="summary-card">
            <div class="summary-label">Today Expenses</div>
            <div class="summary-value">${summary["total_expenses"]:.2f}</div>
        </div>
        <div class="summary-card">
            <div class="summary-label">Today Net</div>
            <div class="summary-value" style="color:{_net_color}">${summary["net_profit"]:.2f}</div>
        </div>
        <div class="summary-card">
            <div class="summary-label">Month Net (to date)</div>
            <div class="summary-value" style="color:{_mnet_color}">${summary["monthly_net"]:.2f}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Budget alerts
daily_spent = summary["variable_expenses"]
monthly_var_spent = 0.0
if not finance_df.empty:
    temp = finance_df.copy()
    temp["date"] = pd.to_datetime(temp["date"], errors="coerce")
    temp = temp.dropna(subset=["date"])
    dt = pd.to_datetime(selected_date_str)
    mask = (temp["date"].dt.year == dt.year) & (temp["date"].dt.month == dt.month)
    monthly_var_spent = round(temp.loc[mask, "amount"].apply(safe_float).sum(), 2)

if daily_spent > DAILY_BUDGET:
    st.markdown(f'<div class="error-box">Over daily budget! Spent ${daily_spent:.2f} / ${DAILY_BUDGET:.2f} limit</div>', unsafe_allow_html=True)
elif daily_spent >= DAILY_BUDGET * 0.8:
    st.markdown(f'<div class="warning-box">Approaching daily budget: ${daily_spent:.2f} / ${DAILY_BUDGET:.2f}</div>', unsafe_allow_html=True)

if monthly_var_spent > MONTHLY_BUDGET:
    st.markdown(f'<div class="error-box">Over monthly budget! Spent ${monthly_var_spent:.2f} / ${MONTHLY_BUDGET:.2f} limit</div>', unsafe_allow_html=True)
elif monthly_var_spent >= MONTHLY_BUDGET * 0.8:
    st.markdown(f'<div class="warning-box">Approaching monthly budget: ${monthly_var_spent:.2f} / ${MONTHLY_BUDGET:.2f}</div>', unsafe_allow_html=True)

# =========================================================
# MAIN 2-COLUMN LAYOUT
# =========================================================
left_col, right_col = st.columns([1.0, 1.0], gap="large")

with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Daily Finance Input</div>', unsafe_allow_html=True)

    auto_income = get_driving_income_for_date(driving_df, selected_date_str)
    if auto_income > 0:
        st.markdown(
            f'<div class="c-muted" style="font-size:13px;margin-bottom:12px">Driving income auto-detected: <span class="c-pos" style="font-weight:600">${auto_income:.2f}</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="c-muted" style="font-size:13px;margin-bottom:12px">No driving income found for this date yet.</div>',
            unsafe_allow_html=True,
        )

    with st.form("daily_finance_form"):
        st.number_input(
            "Daily Income",
            min_value=0.0,
            value=float(auto_income),
            step=1.0,
            disabled=True,
        )

        category = st.selectbox(
            "Expense Category",
            EXPENSE_CATEGORIES,
        )

        expense_amount = st.number_input(
            "Expense Amount",
            min_value=0.0,
            value=0.0,
            step=1.0,
        )

        submitted = st.form_submit_button("Save Daily Finance")

        if submitted:
            if expense_amount > 0:
                new_row = pd.DataFrame([{
                    "date": selected_date_str,
                    "category": category,
                    "amount": round(float(expense_amount), 2),
                }])

                finance_df = pd.concat([finance_df, new_row], ignore_index=True)
                save_finance(finance_df)

                st.success("Daily expense saved.")
                st.rerun()
            else:
                st.warning("Enter an expense amount greater than 0.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Daily Expenses</div>', unsafe_allow_html=True)

    day_expenses_df = get_daily_expenses(finance_df, selected_date_str)

    if day_expenses_df.empty:
        st.info("No daily expense records for this date.")
    else:
        day_expenses_df = day_expenses_df.reset_index()

        for i, row in day_expenses_df.iterrows():
            original_index = int(row["index"])
            display_index = i + 1

            st.markdown(
                f"""
                <div class="record-card">
                    {detail_row(f"{display_index}. {clean_text(row['category'])}", f"${safe_float(row['amount']):.2f}", "negative")}
                </div>
                """,
                unsafe_allow_html=True,
            )

            c1, c2, c3 = st.columns([1, 1, 5])

            with c1:
                if st.button("Edit", key=f"edit_daily_{original_index}"):
                    st.session_state.edit_daily_index = original_index

            with c2:
                if st.button("Delete", key=f"delete_daily_{original_index}"):
                    finance_df = finance_df.drop(index=original_index).reset_index(drop=True)
                    save_finance(finance_df)
                    st.session_state.edit_daily_index = None
                    st.success("Daily expense deleted.")
                    st.rerun()

            if st.session_state.edit_daily_index == original_index:
                with st.form(f"edit_daily_form_{original_index}"):
                    options = EXPENSE_CATEGORIES
                    current_category = clean_text(row["category"])
                    if current_category not in options:
                        current_category = "Other"

                    new_category = st.selectbox(
                        "Edit Category",
                        options,
                        index=options.index(current_category),
                    )

                    new_amount = st.number_input(
                        "Edit Amount",
                        min_value=0.0,
                        value=float(safe_float(row["amount"])),
                        step=1.0,
                        key=f"edit_amount_{original_index}",
                    )

                    ec1, ec2 = st.columns(2)

                    with ec1:
                        save_edit = st.form_submit_button("Save Changes")
                    with ec2:
                        cancel_edit = st.form_submit_button("Cancel")

                    if save_edit:
                        finance_df.loc[original_index, "category"] = new_category
                        finance_df.loc[original_index, "amount"] = round(float(new_amount), 2)
                        save_finance(finance_df)
                        st.session_state.edit_daily_index = None
                        st.success("Daily expense updated.")
                        st.rerun()

                    if cancel_edit:
                        st.session_state.edit_daily_index = None
                        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Monthly Recurring Expenses</div>', unsafe_allow_html=True)

    with st.form("monthly_expense_form"):
        monthly_name = st.text_input("Recurring Expense Name")
        monthly_amount = st.number_input(
            "Recurring Amount",
            min_value=0.0,
            value=0.0,
            step=1.0,
        )

        monthly_submitted = st.form_submit_button("Save Monthly Expense")

        if monthly_submitted:
            name_clean = clean_text(monthly_name)

            if not name_clean:
                st.warning("Enter a recurring expense name.")
            elif monthly_amount <= 0:
                st.warning("Enter an amount greater than 0.")
            else:
                duplicate_exists = False
                if not monthly_df.empty:
                    duplicate_exists = (
                        monthly_df["name"]
                        .astype(str)
                        .str.strip()
                        .str.lower()
                        .eq(name_clean.lower())
                        .any()
                    )

                if duplicate_exists:
                    st.warning("This recurring expense already exists.")
                else:
                    new_monthly = pd.DataFrame([{
                        "name": name_clean,
                        "amount": round(float(monthly_amount), 2),
                    }])

                    monthly_df = pd.concat([monthly_df, new_monthly], ignore_index=True)
                    save_monthly(monthly_df)

                    st.success("Monthly recurring expense saved.")
                    st.rerun()

    if monthly_df.empty:
        st.info("No monthly recurring expense saved yet.")
    else:
        for idx, row in monthly_df.reset_index().iterrows():
            original_index = int(row["index"])
            display_index = idx + 1

            st.markdown(
                f"""
                <div class="record-card">
                    {detail_row(f"{display_index}. {clean_text(row['name'])}", f"${safe_float(row['amount']):.2f}", "negative")}
                </div>
                """,
                unsafe_allow_html=True,
            )

            m1, m2, m3 = st.columns([1, 1, 5])

            with m1:
                if st.button("Edit", key=f"edit_monthly_{original_index}"):
                    st.session_state.edit_monthly_index = original_index

            with m2:
                if st.button("Delete", key=f"delete_monthly_{original_index}"):
                    monthly_df = monthly_df.drop(index=original_index).reset_index(drop=True)
                    save_monthly(monthly_df)
                    st.session_state.edit_monthly_index = None
                    st.success("Monthly expense deleted.")
                    st.rerun()

            if st.session_state.edit_monthly_index == original_index:
                with st.form(f"edit_monthly_form_{original_index}"):
                    new_name = st.text_input("Edit Name", value=clean_text(row["name"]))
                    new_amount = st.number_input(
                        "Edit Amount",
                        min_value=0.0,
                        value=float(safe_float(row["amount"])),
                        step=1.0,
                        key=f"monthly_amount_{original_index}",
                    )

                    mc1, mc2 = st.columns(2)

                    with mc1:
                        save_monthly_edit = st.form_submit_button("Save Changes")
                    with mc2:
                        cancel_monthly_edit = st.form_submit_button("Cancel")

                    if save_monthly_edit:
                        monthly_df.loc[original_index, "name"] = clean_text(new_name)
                        monthly_df.loc[original_index, "amount"] = round(float(new_amount), 2)
                        save_monthly(monthly_df)
                        st.session_state.edit_monthly_index = None
                        st.success("Monthly expense updated.")
                        st.rerun()

                    if cancel_monthly_edit:
                        st.session_state.edit_monthly_index = None
                        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Finance Dashboard</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="c-muted" style="font-size:13px;margin-bottom:14px">Viewing: {selected_date_str}</div>',
        unsafe_allow_html=True,
    )

    if summary["income"] > 0:
        st.markdown(
            f'{status_badge(f"Total Income: ${summary['income']:.2f}", POS)}',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="c-muted" style="font-size:13px;margin-bottom:8px">No income recorded for this date.</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'{status_badge(f"Variable Expenses: ${summary['variable_expenses']:.2f}", NEG)}',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'{status_badge(f"Fixed Share: ${summary['fixed_share']:.2f}", NEG)}',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'{status_badge(f"Total Expenses: ${summary['total_expenses']:.2f}", NEG)}',
        unsafe_allow_html=True,
    )

    _net_cls = "positive" if summary["net_profit"] >= 0 else "negative"
    _mnet_cls = "positive" if summary["monthly_net"] >= 0 else "negative"
    st.markdown(
        f'{detail_row("Today Net", f"${summary['net_profit']:.2f}", _net_cls)}',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'{detail_row("Month Net (to date)", f"${summary['monthly_net']:.2f}", _mnet_cls)}',
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Expense Breakdown</div>', unsafe_allow_html=True)

    breakdown_rows = []
    day_expenses_df = get_daily_expenses(finance_df, selected_date_str)

    if not day_expenses_df.empty:
        grouped = day_expenses_df.groupby("category", as_index=False)["amount"].sum()

        for _, row in grouped.iterrows():
            breakdown_rows.append({
                "Category": clean_text(row["category"]),
                "Amount": f"${safe_float(row['amount']):.2f}",
            })

    fixed_share = get_daily_fixed_share(monthly_df, selected_date_str)
    if fixed_share > 0:
        breakdown_rows.append({
            "Category": "Monthly Fixed Share",
            "Amount": f"${fixed_share:.2f}",
        })

    if breakdown_rows:
        breakdown_df = pd.DataFrame(breakdown_rows)
        st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
    else:
        st.info("No finance or driving record saved for this date yet.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Manage Expense Categories</div>', unsafe_allow_html=True)
st.markdown('<div class="c-muted" style="font-size:13px;margin-bottom:12px">Add or remove categories. Changes apply after page reload.</div>', unsafe_allow_html=True)

new_cat = st.text_input("Add new category")
if st.button("Add Category") and new_cat.strip():
    if new_cat.strip() not in EXPENSE_CATEGORIES:
        EXPENSE_CATEGORIES.append(new_cat.strip())
        if os.path.exists(SETTINGS_FILE):
            try:
                _settings = pd.read_csv(SETTINGS_FILE)
                _settings.loc[0, "expense_categories"] = ",".join(EXPENSE_CATEGORIES)
                _settings.to_csv(SETTINGS_FILE, index=False)
                st.success(f"Added '{new_cat.strip()}'")
                st.rerun()
            except Exception:
                st.error("Failed to save category")
    else:
        st.warning("Category already exists")

_cat_badges = " ".join([status_badge(c, ACCENT) for c in EXPENSE_CATEGORIES])
st.markdown(f'<div style="margin-top:12px">{_cat_badges}</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)