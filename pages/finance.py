import calendar
from datetime import date

import pandas as pd
import streamlit as st
from theme import inject_theme, nav_menu, page_header, detail_row, section_card, status_badge, ACCENT, POS, NEG
from utils import (
    clean_text, safe_float,
    load_finance, load_monthly_expenses, load_driving, load_settings,
    save_finance_df, save_monthly_expenses_df,
    FINANCE_COLUMNS, MONTHLY_EXPENSES_COLUMNS,
)

st.set_page_config(page_title="Finance", page_icon="💰", layout="wide", initial_sidebar_state="collapsed")

# ── Cache helpers ─────────────────────────────────────────────────────
@st.cache_data(ttl=15)
def _load_finance():
    df = load_finance()
    if not df.empty:
        df["date"] = df["date"].astype(str)
        df["category"] = df["category"].astype(str)
    return df


@st.cache_data(ttl=15)
def _load_monthly():
    return load_monthly_expenses()


@st.cache_data(ttl=15)
def _load_driving():
    df = load_driving()
    if not df.empty and "date" in df.columns:
        df["date"] = df["date"].astype(str)
    return df


def _invalidate():
    _load_finance.clear()
    _load_monthly.clear()
    _load_driving.clear()


def save_finance(df):
    save_finance_df(df)
    _invalidate()


def save_monthly(df):
    save_monthly_expenses_df(df)
    _invalidate()


# ── Settings ─────────────────────────────────────────────────────────
DAILY_BUDGET = 50.0
MONTHLY_BUDGET = 1500.0
DEFAULT_CATEGORIES = ["Food", "Transport", "Bills", "Shopping", "Health", "Family", "Other"]
EXPENSE_CATEGORIES = DEFAULT_CATEGORIES[:]

try:
    _settings = load_settings()
    if not _settings.empty:
        if "daily_budget" in _settings.columns:
            DAILY_BUDGET = float(_settings.loc[0, "daily_budget"])
        if "monthly_budget" in _settings.columns:
            MONTHLY_BUDGET = float(_settings.loc[0, "monthly_budget"])
        if "expense_categories" in _settings.columns:
            raw = str(_settings.loc[0, "expense_categories"]).strip()
            if raw and raw.lower() != "nan":
                EXPENSE_CATEGORIES = [c.strip() for c in raw.split(",") if c.strip()]
except Exception:
    pass


# =========================================================
# HELPERS
# =========================================================
def get_days_in_month(date_str):
    dt = pd.to_datetime(date_str)
    return calendar.monthrange(dt.year, dt.month)[1]


def get_daily_fixed_share(monthly_expenses_df, selected_date_str):
    if monthly_expenses_df.empty:
        return 0.0
    total_monthly = monthly_expenses_df["amount"].apply(safe_float).sum()
    days = get_days_in_month(selected_date_str)
    return round(total_monthly / days, 2) if days > 0 else 0.0


def get_driving_income_for_date(driving_data, selected_date_str):
    if driving_data.empty or "date" not in driving_data.columns or "earnings" not in driving_data.columns:
        return 0.0
    temp_df = driving_data.copy()
    temp_df["date"] = temp_df["date"].astype(str)
    temp_df["earnings"] = temp_df["earnings"].apply(safe_float)
    day_rows = temp_df[temp_df["date"] == selected_date_str]
    return round(day_rows["earnings"].sum(), 2) if not day_rows.empty else 0.0


def get_daily_expenses(finance_data, selected_date_str):
    if finance_data.empty:
        return pd.DataFrame(columns=FINANCE_COLUMNS)
    temp_df = finance_data.copy()
    temp_df["date"] = temp_df["date"].astype(str)
    return temp_df[temp_df["date"] == selected_date_str].copy()


def get_monthly_net(finance_data, monthly_expenses_df, driving_data, selected_date_str):
    try:
        dt = pd.to_datetime(selected_date_str)
    except Exception:
        return 0.0
    year, month = dt.year, dt.month
    days_elapsed = dt.day

    monthly_income = 0.0
    if not driving_data.empty and "earnings" in driving_data.columns:
        temp = driving_data.copy()
        temp["date"] = pd.to_datetime(temp["date"], errors="coerce")
        temp = temp.dropna(subset=["date"])
        mask = (temp["date"].dt.year == year) & (temp["date"].dt.month == month)
        monthly_income = round(temp.loc[mask, "earnings"].apply(safe_float).sum(), 2)

    monthly_var = 0.0
    if not finance_data.empty:
        temp = finance_data.copy()
        temp["date"] = pd.to_datetime(temp["date"], errors="coerce")
        temp = temp.dropna(subset=["date"])
        mask = (temp["date"].dt.year == year) & (temp["date"].dt.month == month)
        monthly_var = round(temp.loc[mask, "amount"].apply(safe_float).sum(), 2)

    days_in_month = get_days_in_month(selected_date_str)
    monthly_fixed_total = monthly_expenses_df["amount"].apply(safe_float).sum() if not monthly_expenses_df.empty else 0.0
    monthly_fixed_so_far = round(monthly_fixed_total / days_in_month * days_elapsed, 2) if days_in_month > 0 else 0.0
    return round(monthly_income - monthly_var - monthly_fixed_so_far, 2)


def get_summary(finance_data, monthly_expenses_df, driving_data, selected_date_str):
    income = get_driving_income_for_date(driving_data, selected_date_str)
    day_expenses_df = get_daily_expenses(finance_data, selected_date_str)
    variable_expenses = round(day_expenses_df["amount"].apply(safe_float).sum(), 2) if not day_expenses_df.empty else 0.0
    fixed_share = get_daily_fixed_share(monthly_expenses_df, selected_date_str)
    total_expenses = round(variable_expenses + fixed_share, 2)
    net_profit = round(income - total_expenses, 2)
    monthly_net = get_monthly_net(finance_data, monthly_expenses_df, driving_data, selected_date_str)
    return {"income": income, "variable_expenses": variable_expenses, "fixed_share": fixed_share,
            "total_expenses": total_expenses, "net_profit": net_profit, "monthly_net": monthly_net}


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
finance_df = _load_finance()
monthly_df = _load_monthly()
driving_df = _load_driving()

# =========================================================
# HEADER
# =========================================================
st.markdown(page_header("Finance", "Track income, daily expenses, and recurring monthly costs"), unsafe_allow_html=True)

selected_date = st.date_input("Select Finance Date", value=date.today())
selected_date_str = str(selected_date)
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
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Daily Finance Input</div>', unsafe_allow_html=True)
    auto_income = get_driving_income_for_date(driving_df, selected_date_str)
    if auto_income > 0:
        st.markdown(f'<div class="c-muted" style="font-size:13px;margin-bottom:12px">Driving income auto-detected: <span class="c-pos" style="font-weight:600">${auto_income:.2f}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="c-muted" style="font-size:13px;margin-bottom:12px">No driving income found for this date yet.</div>', unsafe_allow_html=True)

    with st.form("daily_finance_form"):
        category = st.selectbox("Expense Category", EXPENSE_CATEGORIES)
        expense_amount = st.number_input("Expense Amount", min_value=0.0, value=0.0, step=1.0)
        submitted = st.form_submit_button("Save Daily Finance")
        if submitted:
            if expense_amount > 0:
                new_row = pd.DataFrame([{"date": selected_date_str, "category": category, "amount": round(float(expense_amount), 2)}])
                updated = pd.concat([finance_df, new_row], ignore_index=True)
                save_finance(updated)
                st.success("Daily expense saved.")
                st.rerun()
            else:
                st.warning("Enter an expense amount greater than 0.")

with right_col:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Finance Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="c-muted" style="font-size:13px;margin-bottom:14px">Viewing: {selected_date_str}</div>', unsafe_allow_html=True)
    if summary["income"] > 0:
        income_text = f"Total Income: ${summary['income']:.2f}"
        st.markdown(status_badge(income_text, POS), unsafe_allow_html=True)
    else:
        st.markdown('<div class="c-muted" style="font-size:13px;margin-bottom:8px">No income recorded for this date.</div>', unsafe_allow_html=True)
    var_text = f"Variable Expenses: ${summary['variable_expenses']:.2f}"
    fixed_text = f"Fixed Share: ${summary['fixed_share']:.2f}"
    total_text = f"Total Expenses: ${summary['total_expenses']:.2f}"
    st.markdown(status_badge(var_text, NEG), unsafe_allow_html=True)
    st.markdown(status_badge(fixed_text, NEG), unsafe_allow_html=True)
    st.markdown(status_badge(total_text, NEG), unsafe_allow_html=True)
    _net_cls = "positive" if summary["net_profit"] >= 0 else "negative"
    _mnet_cls = "positive" if summary["monthly_net"] >= 0 else "negative"
    net_val = f"${summary['net_profit']:.2f}"
    mnet_val = f"${summary['monthly_net']:.2f}"
    st.markdown(detail_row("Today Net", net_val, _net_cls), unsafe_allow_html=True)
    st.markdown(detail_row("Month Net (to date)", mnet_val, _mnet_cls), unsafe_allow_html=True)

# =========================================================
# ROW 2: Daily Expenses + Expense Breakdown
# =========================================================
left_col2, right_col2 = st.columns([1.0, 1.0], gap="large")

with left_col2:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Daily Expenses</div>', unsafe_allow_html=True)
    day_expenses_df = get_daily_expenses(finance_df, selected_date_str)
    if day_expenses_df.empty:
        st.info("No daily expense records for this date.")
    else:
        day_expenses_df = day_expenses_df.reset_index()
        for i, row in day_expenses_df.iterrows():
            original_index = int(row["index"])
            display_index = i + 1
            label = f"{display_index}. {clean_text(row['category'])}"
            amount = f"${safe_float(row['amount']):.2f}"
            st.markdown(f'<div class="record-card">{detail_row(label, amount, "negative")}</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 1, 5])
            with c1:
                if st.button("Edit", key=f"edit_daily_{original_index}"):
                    st.session_state.edit_daily_index = original_index
            with c2:
                if st.button("Delete", key=f"delete_daily_{original_index}"):
                    updated = finance_df.drop(index=original_index).reset_index(drop=True)
                    save_finance(updated)
                    st.session_state.edit_daily_index = None
                    st.success("Daily expense deleted.")
                    st.rerun()
            if st.session_state.edit_daily_index == original_index:
                with st.form(f"edit_daily_form_{original_index}"):
                    options = EXPENSE_CATEGORIES
                    current_category = clean_text(row["category"])
                    if current_category not in options:
                        current_category = "Other"
                    new_category = st.selectbox("Edit Category", options, index=options.index(current_category))
                    new_amount = st.number_input("Edit Amount", min_value=0.0, value=float(safe_float(row["amount"])), step=1.0, key=f"edit_amount_{original_index}")
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

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Monthly Recurring Expenses</div>', unsafe_allow_html=True)
    with st.form("monthly_expense_form"):
        monthly_name = st.text_input("Recurring Expense Name")
        monthly_amount = st.number_input("Recurring Amount", min_value=0.0, value=0.0, step=1.0)
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
                    duplicate_exists = monthly_df["name"].astype(str).str.strip().str.lower().eq(name_clean.lower()).any()
                if duplicate_exists:
                    st.warning("This recurring expense already exists.")
                else:
                    new_monthly = pd.DataFrame([{"name": name_clean, "amount": round(float(monthly_amount), 2)}])
                    updated = pd.concat([monthly_df, new_monthly], ignore_index=True)
                    save_monthly(updated)
                    st.success("Monthly recurring expense saved.")
                    st.rerun()

    if monthly_df.empty:
        st.info("No monthly recurring expense saved yet.")
    else:
        for idx, row in monthly_df.reset_index().iterrows():
            original_index = int(row["index"])
            display_index = idx + 1
            label = f"{display_index}. {clean_text(row['name'])}"
            amount = f"${safe_float(row['amount']):.2f}"
            st.markdown(f'<div class="record-card">{detail_row(label, amount, "negative")}</div>', unsafe_allow_html=True)
            m1, m2, m3 = st.columns([1, 1, 5])
            with m1:
                if st.button("Edit", key=f"edit_monthly_{original_index}"):
                    st.session_state.edit_monthly_index = original_index
            with m2:
                if st.button("Delete", key=f"delete_monthly_{original_index}"):
                    updated = monthly_df.drop(index=original_index).reset_index(drop=True)
                    save_monthly(updated)
                    st.session_state.edit_monthly_index = None
                    st.success("Monthly expense deleted.")
                    st.rerun()
            if st.session_state.edit_monthly_index == original_index:
                with st.form(f"edit_monthly_form_{original_index}"):
                    new_name = st.text_input("Edit Name", value=clean_text(row["name"]))
                    new_amount = st.number_input("Edit Amount", min_value=0.0, value=float(safe_float(row["amount"])), step=1.0, key=f"monthly_amount_{original_index}")
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

with right_col2:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Expense Breakdown</div>', unsafe_allow_html=True)
    breakdown_rows = []
    day_expenses_df2 = get_daily_expenses(finance_df, selected_date_str)
    if not day_expenses_df2.empty:
        grouped = day_expenses_df2.groupby("category", as_index=False)["amount"].sum()
        for _, row in grouped.iterrows():
            breakdown_rows.append({"Category": clean_text(row["category"]), "Amount": f"${safe_float(row['amount']):.2f}"})
    fixed_share = get_daily_fixed_share(monthly_df, selected_date_str)
    if fixed_share > 0:
        breakdown_rows.append({"Category": "Monthly Fixed Share", "Amount": f"${fixed_share:.2f}"})
    if breakdown_rows:
        st.dataframe(pd.DataFrame(breakdown_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No finance or driving record saved for this date yet.")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Manage Expense Categories</div>', unsafe_allow_html=True)
st.markdown('<div class="c-muted" style="font-size:13px;margin-bottom:12px">Add or remove categories. Changes apply after page reload.</div>', unsafe_allow_html=True)
new_cat = st.text_input("Add new category")
if st.button("Add Category") and new_cat.strip():
    if new_cat.strip() not in EXPENSE_CATEGORIES:
        EXPENSE_CATEGORIES.append(new_cat.strip())
        try:
            _settings = load_settings()
            _settings.loc[0, "expense_categories"] = ",".join(EXPENSE_CATEGORIES)
            from utils import save_settings_df
            save_settings_df(_settings)
            st.success(f"Added '{new_cat.strip()}'")
            st.rerun()
        except Exception:
            st.error("Failed to save category")
    else:
        st.warning("Category already exists")

_cat_badges = " ".join([status_badge(c, ACCENT) for c in EXPENSE_CATEGORIES])
st.markdown(f'<div style="margin-top:12px">{_cat_badges}</div>', unsafe_allow_html=True)
