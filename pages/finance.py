import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Finance", page_icon="\U0001f4b0", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header, metric_card
from utils import (
    load_finance, save_finance_df,
    load_monthly_expenses, save_monthly_expenses_df,
    load_assets, save_assets_df,
    load_liabilities, save_liabilities_df,
    load_settings, clean_text,
    filter_by_exact_date, filter_by_month, month_days,
)

inject_theme()
nav_menu("Finance")


@st.cache_data(ttl=3600)
def fetch_gold_price_sgd_per_gram():
    """Fetch gold price in SGD/g from GoldAPI. Returns None on failure."""
    try:
        resp = requests.get(
            "https://www.goldapi.io/api/XAU/SGD",
            headers={"x-access-token": "goldapi-19lctk19mo1a4qqd-io"},
            timeout=10,
        )
        resp.raise_for_status()
        sgd_per_oz = float(resp.json()["price"])
        return sgd_per_oz / 31.1035
    except Exception:
        return None

st.markdown(page_header("Finance", "Your money operating system"), unsafe_allow_html=True)

today = date.today()

finance_df = load_finance()
monthly_df = load_monthly_expenses()
settings_df = load_settings()

categories_default = ["Food", "Transport", "Shopping", "Bills", "Health", "Entertainment", "Other"]
if not settings_df.empty and "expense_categories" in settings_df.columns:
    raw = clean_text(settings_df.loc[0, "expense_categories"])
    if raw:
        parsed = [c.strip() for c in raw.split(",") if c.strip()]
        if parsed:
            categories_default = parsed

# ============================================================
# SECTION 1 — LOG INCOME
# ============================================================
st.markdown('<div class="section-title">\U0001f4b5 Log Income</div>', unsafe_allow_html=True)
inc_date = st.date_input("Date", value=today, key="inc_date")
inc_amount = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f", key="inc_amount")
if st.button("Save Income", use_container_width=True, key="save_inc"):
    if inc_amount > 0:
        new_row = pd.DataFrame([{"date": str(inc_date), "category": "Income", "amount": float(inc_amount)}])
        save_finance_df(pd.concat([finance_df, new_row], ignore_index=True))
        st.success(f"Income saved: ${inc_amount:,.2f}")
        st.rerun()
    else:
        st.warning("Enter an amount greater than zero.")

st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

# ============================================================
# SECTION 2 — LOG EXPENSE
# ============================================================
st.markdown('<div class="section-title">\U0001f4b8 Log Expense</div>', unsafe_allow_html=True)
exp_date = st.date_input("Date", value=today, key="exp_date")
exp_cat = st.selectbox("Category", categories_default, key="exp_cat")
exp_amount = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f", key="exp_amount")
if st.button("Save Expense", use_container_width=True, key="save_exp"):
    if exp_amount > 0:
        new_row = pd.DataFrame([{"date": str(exp_date), "category": exp_cat, "amount": float(exp_amount)}])
        save_finance_df(pd.concat([finance_df, new_row], ignore_index=True))
        st.success(f"Expense saved: {exp_cat} \u2014 ${exp_amount:,.2f}")
        st.rerun()
    else:
        st.warning("Enter an amount greater than zero.")

st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

# ============================================================
# SECTION 3 — TODAY SUMMARY
# ============================================================
st.markdown('<div class="section-title">\U0001f4ca Today Summary</div>', unsafe_allow_html=True)

today_df = filter_by_exact_date(finance_df, today)
today_income = float(today_df[today_df["category"] == "Income"]["amount"].sum()) if not today_df.empty else 0.0
today_expense = float(today_df[today_df["category"] != "Income"]["amount"].sum()) if not today_df.empty else 0.0
today_net = today_income - today_expense

cols = st.columns(3)
with cols[0]:
    st.markdown(metric_card("Income", f"${today_income:,.2f}", color="var(--accent-2)"), unsafe_allow_html=True)
with cols[1]:
    st.markdown(metric_card("Expenses", f"${today_expense:,.2f}", color="var(--neg)"), unsafe_allow_html=True)
with cols[2]:
    net_color = "var(--accent-2)" if today_net >= 0 else "var(--neg)"
    st.markdown(metric_card("Net", f"${today_net:,.2f}", color=net_color), unsafe_allow_html=True)

# ============================================================
# SECTION 4 — MONTHLY RECURRING
# ============================================================
st.markdown('<div class="section-title">\U0001f501 Monthly Recurring</div>', unsafe_allow_html=True)

fx_name = st.text_input("Name", key="fx_name", placeholder="e.g. Rent")
fx_amount = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f", key="fx_amount")
if st.button("Add Fixed Expense", use_container_width=True, key="add_fx"):
    name = fx_name.strip()
    if name and fx_amount > 0:
        new_row = pd.DataFrame([{"name": name, "amount": float(fx_amount)}])
        save_monthly_expenses_df(pd.concat([monthly_df, new_row], ignore_index=True))
        st.success(f"Added {name}: ${fx_amount:,.2f}")
        st.rerun()
    else:
        st.warning("Provide a name and an amount.")

with st.expander(f"Monthly Recurring ({len(monthly_df)} items)"):
    if not monthly_df.empty:
        for idx, r in monthly_df.iterrows():
            row_cols = st.columns([6, 2])
            with row_cols[0]:
                st.markdown(
                    f'<div class="list-row"><span>{r["name"]}</span>'
                    f'<span class="amount">${float(r["amount"]):,.2f}</span></div>',
                    unsafe_allow_html=True,
                )
            with row_cols[1]:
                if st.button("Remove", key=f"rm_fx_{idx}", use_container_width=True):
                    save_monthly_expenses_df(monthly_df.drop(idx).reset_index(drop=True))
                    st.rerun()
    else:
        st.markdown(
            '<div class="list-row" style="justify-content:center;opacity:0.7;">No recurring expenses yet.</div>',
            unsafe_allow_html=True,
        )

# ============================================================
# SECTION 5 — ASSETS
# ============================================================
st.markdown('<div class="section-title">\U0001f3e6 Assets</div>', unsafe_allow_html=True)

assets_df = load_assets()

asset_name = st.text_input("Name", key="asset_name", placeholder="e.g. Savings Account")
asset_amount = st.number_input("Amount", min_value=0.0, step=100.0, format="%.2f", key="asset_amount")
if st.button("Add Asset", use_container_width=True, key="add_asset"):
    name = asset_name.strip()
    if name and asset_amount > 0:
        new_row = pd.DataFrame([{"name": name, "amount": float(asset_amount)}])
        save_assets_df(pd.concat([assets_df, new_row], ignore_index=True))
        st.success(f"Added {name}: ${asset_amount:,.2f}")
        st.rerun()
    else:
        st.warning("Provide a name and an amount.")

with st.expander(f"Assets ({len(assets_df)} items)"):
    if not assets_df.empty:
        for idx, r in assets_df.iterrows():
            row_cols = st.columns([6, 2])
            with row_cols[0]:
                st.markdown(
                    f'<div class="list-row"><span>{r["name"]}</span>'
                    f'<span class="amount">${float(r["amount"]):,.2f}</span></div>',
                    unsafe_allow_html=True,
                )
            with row_cols[1]:
                if st.button("Remove", key=f"rm_asset_{idx}", use_container_width=True):
                    save_assets_df(assets_df.drop(idx).reset_index(drop=True))
                    st.rerun()
    else:
        st.markdown(
            '<div class="list-row" style="justify-content:center;opacity:0.7;">No assets yet.</div>',
            unsafe_allow_html=True,
        )

    # — Gold Asset Calculator —
    st.markdown("---")
    st.markdown('<div class="section-title">Gold Asset Calculator (916 / 22k)</div>', unsafe_allow_html=True)
    gold_sgd_per_gram = fetch_gold_price_sgd_per_gram()
    if gold_sgd_per_gram is not None:
        st.markdown(
            f'<div class="list-row"><span>Live Gold Price</span>'
            f'<span class="amount">SGD ${gold_sgd_per_gram:,.2f}/g</span></div>',
            unsafe_allow_html=True,
        )
    else:
        gold_sgd_per_gram = st.number_input(
            "Gold price (SGD/g)", min_value=0.0, step=1.0, format="%.2f", key="gold_manual_price"
        )
    gold_weight = st.number_input("Weight (grams)", min_value=0.0, step=1.0, format="%.2f", key="gold_weight")
    gold_purity = 0.916
    gold_discount = 0.85
    gold_value = gold_weight * (gold_sgd_per_gram * gold_purity) * gold_discount
    if gold_weight > 0 and gold_sgd_per_gram > 0:
        st.markdown(
            f'<div class="list-row" style="font-weight:700;"><span>Your Gold Value (916)</span>'
            f'<span class="amount">SGD ${gold_value:,.2f}</span></div>',
            unsafe_allow_html=True,
        )
        if st.button("Add to Assets", use_container_width=True, key="add_gold_asset"):
            name = f"Gold ({gold_weight:g}g 916)"
            new_row = pd.DataFrame([{"name": name, "amount": float(gold_value)}])
            save_assets_df(pd.concat([assets_df, new_row], ignore_index=True))
            st.success(f"Added {name}: SGD ${gold_value:,.2f}")
            st.rerun()

# ============================================================
# SECTION 6 — LIABILITIES
# ============================================================
st.markdown('<div class="section-title">\U0001f4c9 Liabilities</div>', unsafe_allow_html=True)

liabilities_df = load_liabilities()

liab_name = st.text_input("Name", key="liab_name", placeholder="e.g. Car Loan")
liab_amount = st.number_input("Amount", min_value=0.0, step=100.0, format="%.2f", key="liab_amount")
if st.button("Add Liability", use_container_width=True, key="add_liab"):
    name = liab_name.strip()
    if name and liab_amount > 0:
        new_row = pd.DataFrame([{"name": name, "amount": float(liab_amount)}])
        save_liabilities_df(pd.concat([liabilities_df, new_row], ignore_index=True))
        st.success(f"Added {name}: ${liab_amount:,.2f}")
        st.rerun()
    else:
        st.warning("Provide a name and an amount.")

with st.expander(f"Liabilities ({len(liabilities_df)} items)"):
    if not liabilities_df.empty:
        for idx, r in liabilities_df.iterrows():
            row_cols = st.columns([6, 2])
            with row_cols[0]:
                st.markdown(
                    f'<div class="list-row"><span>{r["name"]}</span>'
                    f'<span class="amount">${float(r["amount"]):,.2f}</span></div>',
                    unsafe_allow_html=True,
                )
            with row_cols[1]:
                if st.button("Remove", key=f"rm_liab_{idx}", use_container_width=True):
                    save_liabilities_df(liabilities_df.drop(idx).reset_index(drop=True))
                    st.rerun()
    else:
        st.markdown(
            '<div class="list-row" style="justify-content:center;opacity:0.7;">No liabilities yet.</div>',
            unsafe_allow_html=True,
        )

# ============================================================
# SECTION 7 — MONTH SUMMARY
# ============================================================
st.markdown('<div class="section-title">\U0001f4c5 Month Summary</div>', unsafe_allow_html=True)

month_df = filter_by_month(finance_df, today.year, today.month)
month_income = float(month_df[month_df["category"] == "Income"]["amount"].sum()) if not month_df.empty else 0.0
month_daily_exp = float(month_df[month_df["category"] != "Income"]["amount"].sum()) if not month_df.empty else 0.0
month_fixed = float(monthly_df["amount"].sum()) if not monthly_df.empty else 0.0
month_net = month_income - month_daily_exp - month_fixed
days = month_days(today.year, today.month)
month_label = today.strftime("%B %Y")

g1 = st.columns(2)
with g1[0]:
    st.markdown(metric_card("Income", f"${month_income:,.2f}", sub=month_label, color="var(--accent-2)"), unsafe_allow_html=True)
with g1[1]:
    st.markdown(metric_card("Variable Expenses", f"${month_daily_exp:,.2f}", sub="Logged this month", color="var(--neg)"), unsafe_allow_html=True)

g2 = st.columns(2)
with g2[0]:
    st.markdown(metric_card("Fixed (Recurring)", f"${month_fixed:,.2f}", sub=f"${month_fixed/days:,.2f}/day", color="var(--neg)"), unsafe_allow_html=True)
with g2[1]:
    net_color = "var(--accent-2)" if month_net >= 0 else "var(--neg)"
    st.markdown(metric_card("Net", f"${month_net:,.2f}", sub=month_label, color=net_color), unsafe_allow_html=True)

# ============================================================
# SECTION 8 — NET WORTH
# ============================================================
st.markdown('<div class="section-title">\U0001f4b0 Net Worth</div>', unsafe_allow_html=True)

nw_assets_items = float(assets_df["amount"].sum()) if not assets_df.empty else 0.0
nw_total_assets = month_income + nw_assets_items

nw_liab_items = float(liabilities_df["amount"].sum()) if not liabilities_df.empty else 0.0
nw_total_liabilities = month_daily_exp + month_fixed + nw_liab_items

nw_net = nw_total_assets - nw_total_liabilities

nw1 = st.columns(3)
with nw1[0]:
    st.markdown(metric_card("Total Assets", f"${nw_total_assets:,.2f}", sub=f"Income ${month_income:,.2f} + Assets ${nw_assets_items:,.2f}", color="var(--accent-2)"), unsafe_allow_html=True)
with nw1[1]:
    st.markdown(metric_card("Total Liabilities", f"${nw_total_liabilities:,.2f}", sub=f"Variable ${month_daily_exp:,.2f} + Recurring ${month_fixed:,.2f} + Liabilities ${nw_liab_items:,.2f}", color="var(--neg)"), unsafe_allow_html=True)
with nw1[2]:
    nw_color = "var(--accent-2)" if nw_net >= 0 else "var(--neg)"
    st.markdown(metric_card("Net Worth", f"${nw_net:,.2f}", color=nw_color), unsafe_allow_html=True)
