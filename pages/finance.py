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
    load_gold_assets, save_gold_assets_df,
    load_liabilities, save_liabilities_df,
    load_cpf, save_cpf_df,
    load_medisave, save_medisave_df,
    load_property, save_property_df,
    load_settings, clean_text,
    filter_by_exact_date, filter_by_month, month_days,
)


@st.cache_data(ttl=300)
def load_all_finance_data():
    """Batch-load all sheets in one cached call."""
    return {
        "finance": load_finance(),
        "monthly_expenses": load_monthly_expenses(),
        "settings": load_settings(),
        "assets": load_assets(),
        "gold_assets": load_gold_assets(),
        "liabilities": load_liabilities(),
        "cpf": load_cpf(),
        "medisave": load_medisave(),
        "property": load_property(),
    }


def save_and_rerun():
    """Clear batch cache and rerun so saved data is visible immediately."""
    load_all_finance_data.clear()
    st.rerun()


def fmt(v):
    """Format amount: $0.00 for zero, no decimals otherwise."""
    return "$0.00" if v == 0 else f"${v:,.0f}"

inject_theme()
nav_menu("Finance")

st.markdown(
    '<script>document.querySelectorAll("input[type=text]").forEach(i=>i.setAttribute("autocomplete","off"));'
    'new MutationObserver(()=>document.querySelectorAll("input[type=text]").forEach(i=>i.setAttribute("autocomplete","off")))'
    '.observe(document.body,{childList:true,subtree:true});</script>',
    unsafe_allow_html=True,
)


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

st.markdown(page_header("Finance", ""), unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center;font-style:italic;font-size:28px;margin:18px 0;">Attention Is All You Need</div>',
    unsafe_allow_html=True,
)

today = date.today()

# — Load all data upfront (single cached batch) —
_data = load_all_finance_data()
finance_df = _data["finance"]
monthly_df = _data["monthly_expenses"]
settings_df = _data["settings"]
assets_df = _data["assets"]
gold_assets_df = _data["gold_assets"]
liabilities_df = _data["liabilities"]
cpf_df = _data["cpf"]
medisave_df = _data["medisave"]
property_df = _data["property"]

gold_sgd_per_gram = fetch_gold_price_sgd_per_gram()
gold_discount = 0.85
total_gold_value = 0.0
if not gold_assets_df.empty and gold_sgd_per_gram is not None and gold_sgd_per_gram > 0:
    for _, gr in gold_assets_df.iterrows():
        total_gold_value += float(gr["weight_grams"]) * (gold_sgd_per_gram * float(gr["purity"])) * gold_discount

categories_default = ["Food", "Transport", "Shopping", "Bills", "Health", "Entertainment", "Other"]
if not settings_df.empty and "expense_categories" in settings_df.columns:
    raw = clean_text(settings_df.loc[0, "expense_categories"])
    if raw:
        parsed = [c.strip() for c in raw.split(",") if c.strip()]
        if parsed:
            categories_default = parsed

# — Precompute month figures —
month_df = filter_by_month(finance_df, today.year, today.month)
month_income = float(month_df[month_df["category"] == "Income"]["amount"].sum()) if not month_df.empty else 0.0
month_daily_exp = float(month_df[month_df["category"] != "Income"]["amount"].sum()) if not month_df.empty else 0.0
month_fixed = float(monthly_df["amount"].sum()) if not monthly_df.empty else 0.0
month_net = month_income - month_daily_exp - month_fixed
days = month_days(today.year, today.month)
month_label = today.strftime("%B %Y")

# ============================================================
# 1 — DAY SUMMARY
# ============================================================
selected_date = st.date_input("View date", value=today, key="view_date")
day_label = "Today" if selected_date == today else selected_date.strftime("%d %b %Y")
st.markdown(f'<div class="section-title">\U0001f4ca {day_label} Summary</div>', unsafe_allow_html=True)

today_df = filter_by_exact_date(finance_df, selected_date)
today_income = float(today_df[today_df["category"] == "Income"]["amount"].sum()) if not today_df.empty else 0.0
today_expense = float(today_df[today_df["category"] != "Income"]["amount"].sum()) if not today_df.empty else 0.0
today_net = today_income - today_expense

cols = st.columns(3)
with cols[0]:
    st.markdown(metric_card("Income", fmt(today_income), color="var(--accent-2)"), unsafe_allow_html=True)
with cols[1]:
    st.markdown(metric_card("Expenses", fmt(today_expense), color="var(--neg)"), unsafe_allow_html=True)
with cols[2]:
    net_color = "var(--accent-2)" if today_net >= 0 else "var(--neg)"
    st.markdown(metric_card("Net", fmt(today_net), color=net_color), unsafe_allow_html=True)

# ============================================================
# 2 — LOG INCOME
# ============================================================
st.markdown('<div class="section-title">\U0001f4b5 Log Income</div>', unsafe_allow_html=True)
inc_date = st.date_input("Date", value=today, key="inc_date")
inc_amount = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f", key="inc_amount")
if st.button("Save Income", use_container_width=True, key="save_inc"):
    if inc_amount > 0:
        new_row = pd.DataFrame([{"date": str(inc_date), "category": "Income", "amount": float(inc_amount)}])
        save_finance_df(pd.concat([finance_df, new_row], ignore_index=True))
        st.success(f"Income saved: {fmt(inc_amount)}")
        save_and_rerun()
    else:
        st.warning("Enter an amount greater than zero.")

st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

# ============================================================
# 3 — LOG EXPENSE
# ============================================================
st.markdown('<div class="section-title">\U0001f4b8 Log Expense</div>', unsafe_allow_html=True)
exp_date = st.date_input("Date", value=today, key="exp_date")
exp_cat = st.selectbox("Category", categories_default, key="exp_cat")
exp_amount = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f", key="exp_amount")
if st.button("Save Expense", use_container_width=True, key="save_exp"):
    if exp_amount > 0:
        new_row = pd.DataFrame([{"date": str(exp_date), "category": exp_cat, "amount": float(exp_amount)}])
        save_finance_df(pd.concat([finance_df, new_row], ignore_index=True))
        st.success(f"Expense saved: {exp_cat} \u2014 {fmt(exp_amount)}")
        save_and_rerun()
    else:
        st.warning("Enter an amount greater than zero.")

st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

# ============================================================
# 3b — TRANSACTION HISTORY (today)
# ============================================================
with st.expander(f"{day_label} Transactions ({len(today_df)} entries)"):
    if not today_df.empty:
        for idx in today_df.index:
            r = finance_df.loc[idx]
            cat = r["category"]
            amt = float(r["amount"])
            is_income = cat == "Income"
            color = "var(--accent-2)" if is_income else "var(--neg)"
            sign = "+" if is_income else "-"
            row_cols = st.columns([6, 2])
            with row_cols[0]:
                st.markdown(
                    f'<div class="list-row"><span>{cat}</span>'
                    f'<span class="amount" style="color:{color};">{sign}{fmt(amt)}</span></div>',
                    unsafe_allow_html=True,
                )
            with row_cols[1]:
                if st.button("Delete", key=f"del_tx_{idx}", use_container_width=True):
                    save_finance_df(finance_df.drop(idx).reset_index(drop=True))
                    save_and_rerun()
    else:
        st.markdown(
            f'<div class="list-row" style="justify-content:center;opacity:0.7;">No transactions for {day_label.lower()}.</div>',
            unsafe_allow_html=True,
        )

st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

# ============================================================
# 4 — MONTH SUMMARY
# ============================================================
st.markdown('<div class="section-title">\U0001f4c5 Month Summary</div>', unsafe_allow_html=True)

st.markdown(metric_card("Fixed (Recurring)", fmt(month_fixed), sub=f"{fmt(month_fixed/days)}/day", color="var(--neg)"), unsafe_allow_html=True)

# ============================================================
# 5 — MONTHLY RECURRING
# ============================================================
st.markdown('<div class="section-title">\U0001f501 Monthly Recurring</div>', unsafe_allow_html=True)

fx_name = st.text_input("Name", key="fx_name", placeholder="e.g. Rent")
fx_amount = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f", key="fx_amount")
if st.button("Add Fixed Expense", use_container_width=True, key="add_fx"):
    name = fx_name.strip()
    if name and fx_amount > 0:
        new_row = pd.DataFrame([{"name": name, "amount": float(fx_amount)}])
        save_monthly_expenses_df(pd.concat([monthly_df, new_row], ignore_index=True))
        st.success(f"Added {name}: {fmt(fx_amount)}")
        save_and_rerun()
    else:
        st.warning("Provide a name and an amount.")

with st.expander(f"Monthly Recurring ({len(monthly_df)} items)"):
    if not monthly_df.empty:
        for idx, r in monthly_df.iterrows():
            row_cols = st.columns([6, 2])
            with row_cols[0]:
                st.markdown(
                    f'<div class="list-row"><span>{r["name"]}</span>'
                    f'<span class="amount">{fmt(float(r["amount"]))}</span></div>',
                    unsafe_allow_html=True,
                )
            with row_cols[1]:
                if st.button("Remove", key=f"rm_fx_{idx}", use_container_width=True):
                    save_monthly_expenses_df(monthly_df.drop(idx).reset_index(drop=True))
                    save_and_rerun()
    else:
        st.markdown(
            '<div class="list-row" style="justify-content:center;opacity:0.7;">No recurring expenses yet.</div>',
            unsafe_allow_html=True,
        )

# ============================================================
# 6 — NET WORTH SUMMARY
# ============================================================
st.markdown('<div class="section-title">\U0001f4b0 Net Worth</div>', unsafe_allow_html=True)

alltime_income = float(finance_df[finance_df["category"] == "Income"]["amount"].sum()) if not finance_df.empty else 0.0
alltime_expenses = float(finance_df[finance_df["category"] != "Income"]["amount"].sum()) if not finance_df.empty else 0.0

nw_assets_items = float(assets_df["amount"].sum()) if not assets_df.empty else 0.0
nw_total_assets = nw_assets_items + total_gold_value + alltime_income

nw_liab_items = float(liabilities_df["amount"].sum()) if not liabilities_df.empty else 0.0
nw_total_liabilities = nw_liab_items + alltime_expenses

nw_net = nw_total_assets - nw_total_liabilities

nw1 = st.columns(3)
with nw1[0]:
    st.markdown(metric_card("Total Assets", fmt(nw_total_assets), sub=f"Assets {fmt(nw_assets_items)} + Gold {fmt(total_gold_value)} + Income {fmt(alltime_income)}", color="var(--accent-2)"), unsafe_allow_html=True)
with nw1[1]:
    st.markdown(metric_card("Total Liabilities", fmt(nw_total_liabilities), sub=f"Liabilities {fmt(nw_liab_items)} + Expenses {fmt(alltime_expenses)}", color="var(--neg)"), unsafe_allow_html=True)
with nw1[2]:
    nw_color = "var(--accent-2)" if nw_net >= 0 else "var(--neg)"
    st.markdown(metric_card("Net Worth", fmt(nw_net), color=nw_color), unsafe_allow_html=True)

# ============================================================
# 7 — ASSETS
# ============================================================
st.markdown('<div class="section-title">\U0001f3e6 Assets</div>', unsafe_allow_html=True)

asset_name = st.text_input("Name", key="asset_name", placeholder="e.g. Savings Account")
asset_amount = st.number_input("Amount", min_value=0.0, step=100.0, format="%.2f", key="asset_amount")
if st.button("Add Asset", use_container_width=True, key="add_asset"):
    name = asset_name.strip()
    if name and asset_amount > 0:
        new_row = pd.DataFrame([{"name": name, "amount": float(asset_amount)}])
        save_assets_df(pd.concat([assets_df, new_row], ignore_index=True))
        st.success(f"Added {name}: {fmt(asset_amount)}")
        save_and_rerun()
    else:
        st.warning("Provide a name and an amount.")

total_asset_items = len(assets_df) + len(gold_assets_df)
with st.expander(f"Assets ({total_asset_items} items)"):
    if not assets_df.empty:
        for idx, r in assets_df.iterrows():
            row_cols = st.columns([6, 2])
            with row_cols[0]:
                st.markdown(
                    f'<div class="list-row"><span>{r["name"]}</span>'
                    f'<span class="amount">{fmt(float(r["amount"]))}</span></div>',
                    unsafe_allow_html=True,
                )
            with row_cols[1]:
                if st.button("Remove", key=f"rm_asset_{idx}", use_container_width=True):
                    save_assets_df(assets_df.drop(idx).reset_index(drop=True))
                    save_and_rerun()

    # — Gold assets (live-calculated) —
    if not gold_assets_df.empty:
        st.markdown("---")
        st.markdown('<div class="section-title">Gold Holdings (live price)</div>', unsafe_allow_html=True)
        for idx, gr in gold_assets_df.iterrows():
            w = float(gr["weight_grams"])
            p = float(gr["purity"])
            if gold_sgd_per_gram is not None and gold_sgd_per_gram > 0:
                val = w * (gold_sgd_per_gram * p) * gold_discount
                val_label = f"SGD {fmt(val)}"
            else:
                val_label = "price unavailable"
            row_cols = st.columns([6, 2])
            with row_cols[0]:
                st.markdown(
                    f'<div class="list-row"><span>{gr["name"]} ({w:g}g)</span>'
                    f'<span class="amount">{val_label}</span></div>',
                    unsafe_allow_html=True,
                )
            with row_cols[1]:
                if st.button("Remove", key=f"rm_gold_{idx}", use_container_width=True):
                    save_gold_assets_df(gold_assets_df.drop(idx).reset_index(drop=True))
                    save_and_rerun()

    if assets_df.empty and gold_assets_df.empty:
        st.markdown(
            '<div class="list-row" style="justify-content:center;opacity:0.7;">No assets yet.</div>',
            unsafe_allow_html=True,
        )

# ============================================================
# 8 — GOLD CALCULATOR
# ============================================================
st.markdown('<div class="section-title">Gold Asset Calculator (916 / 22k)</div>', unsafe_allow_html=True)
if gold_sgd_per_gram is not None:
    st.markdown(
        f'<div class="list-row"><span>Live Gold Price</span>'
        f'<span class="amount">SGD {fmt(gold_sgd_per_gram)}/g</span></div>',
        unsafe_allow_html=True,
    )
else:
    gold_sgd_per_gram = st.number_input(
        "Gold price (SGD/g)", min_value=0.0, step=1.0, format="%.2f", key="gold_manual_price"
    )
gold_weight = st.number_input("Weight (grams)", min_value=0.0, step=1.0, format="%.2f", key="gold_weight")
gold_purity = 0.916
gold_value = gold_weight * (gold_sgd_per_gram * gold_purity) * gold_discount
if gold_weight > 0 and gold_sgd_per_gram > 0:
    st.markdown(
        f'<div class="list-row" style="font-weight:700;"><span>Your Gold Value (916)</span>'
        f'<span class="amount">SGD {fmt(gold_value)}</span></div>',
        unsafe_allow_html=True,
    )
    if st.button("Add Gold", use_container_width=True, key="add_gold_asset"):
        new_row = pd.DataFrame([{"name": "Gold 916", "weight_grams": float(gold_weight), "purity": 0.916}])
        save_gold_assets_df(pd.concat([gold_assets_df, new_row], ignore_index=True))
        st.success(f"Added Gold 916: {gold_weight:g}g")
        save_and_rerun()

# ============================================================
# 9 — LIABILITIES
# ============================================================
st.markdown('<div class="section-title">\U0001f4c9 Liabilities</div>', unsafe_allow_html=True)

liab_name = st.text_input("Name", key="liab_name", placeholder="e.g. Car Loan")
liab_amount = st.number_input("Amount", min_value=0.0, step=100.0, format="%.2f", key="liab_amount")
if st.button("Add Liability", use_container_width=True, key="add_liab"):
    name = liab_name.strip()
    if name and liab_amount > 0:
        new_row = pd.DataFrame([{"name": name, "amount": float(liab_amount)}])
        save_liabilities_df(pd.concat([liabilities_df, new_row], ignore_index=True))
        st.success(f"Added {name}: {fmt(liab_amount)}")
        save_and_rerun()
    else:
        st.warning("Provide a name and an amount.")

with st.expander(f"Liabilities ({len(liabilities_df)} items)"):
    if not liabilities_df.empty:
        for idx, r in liabilities_df.iterrows():
            row_cols = st.columns([6, 2])
            with row_cols[0]:
                st.markdown(
                    f'<div class="list-row"><span>{r["name"]}</span>'
                    f'<span class="amount">{fmt(float(r["amount"]))}</span></div>',
                    unsafe_allow_html=True,
                )
            with row_cols[1]:
                if st.button("Remove", key=f"rm_liab_{idx}", use_container_width=True):
                    save_liabilities_df(liabilities_df.drop(idx).reset_index(drop=True))
                    save_and_rerun()
    else:
        st.markdown(
            '<div class="list-row" style="justify-content:center;opacity:0.7;">No liabilities yet.</div>',
            unsafe_allow_html=True,
        )

# ============================================================
# 10 — CPF
# ============================================================
st.markdown('<div class="section-title">\U0001f3e2 CPF</div>', unsafe_allow_html=True)

current_cpf = float(cpf_df.iloc[0]["amount"]) if not cpf_df.empty else 0.0

st.markdown(
    f'<div class="list-row"><span>CPF Account</span>'
    f'<span class="amount">{fmt(current_cpf)}</span></div>',
    unsafe_allow_html=True,
)
cpf_amount = st.number_input("Update Amount", min_value=0.0, step=100.0, format="%.2f", value=current_cpf, key="cpf_amount")
if st.button("Save CPF", use_container_width=True, key="save_cpf"):
    save_cpf_df(pd.DataFrame([{"name": "CPF Account", "amount": float(cpf_amount)}]))
    st.success(f"CPF updated: {fmt(cpf_amount)}")
    save_and_rerun()

# ============================================================
# 11 — MEDISAVE
# ============================================================
st.markdown('<div class="section-title">\U0001f3e5 Medisave</div>', unsafe_allow_html=True)

current_medisave = float(medisave_df.iloc[0]["amount"]) if not medisave_df.empty else 0.0

st.markdown(
    f'<div class="list-row"><span>Medisave Account</span>'
    f'<span class="amount">{fmt(current_medisave)}</span></div>',
    unsafe_allow_html=True,
)
ms_amount = st.number_input("Update Amount", min_value=0.0, step=100.0, format="%.2f", value=current_medisave, key="ms_amount")
if st.button("Save Medisave", use_container_width=True, key="save_ms"):
    save_medisave_df(pd.DataFrame([{"name": "Medisave Account", "amount": float(ms_amount)}]))
    st.success(f"Medisave updated: {fmt(ms_amount)}")
    save_and_rerun()

# ============================================================
# 12 — PROPERTY
# ============================================================
st.markdown('<div class="section-title">\U0001f3e0 Property</div>', unsafe_allow_html=True)

current_property = float(property_df.iloc[0]["amount"]) if not property_df.empty else 0.0

st.markdown(
    f'<div class="list-row"><span>Property</span>'
    f'<span class="amount">{fmt(current_property)}</span></div>',
    unsafe_allow_html=True,
)
prop_amount = st.number_input("Update Amount", min_value=0.0, step=1000.0, format="%.2f", value=current_property, key="prop_amount")
if st.button("Save Property", use_container_width=True, key="save_prop"):
    save_property_df(pd.DataFrame([{"name": "Property", "amount": float(prop_amount), "notes": ""}]))
    st.success(f"Property updated: {fmt(prop_amount)}")
    save_and_rerun()

# — CPF, Medisave & Property totals (informational) —
total_cpf = float(cpf_df["amount"].sum()) if not cpf_df.empty else 0.0
total_medisave = float(medisave_df["amount"].sum()) if not medisave_df.empty else 0.0
total_property = float(property_df["amount"].sum()) if not property_df.empty else 0.0

st.markdown(
    '<div style="text-align:center;opacity:0.6;margin-top:18px;font-size:0.85rem;">'
    'Not included in Net Worth</div>',
    unsafe_allow_html=True,
)
nw2 = st.columns(3)
with nw2[0]:
    st.markdown(metric_card("CPF", fmt(total_cpf), color="var(--accent)"), unsafe_allow_html=True)
with nw2[1]:
    st.markdown(metric_card("Medisave", fmt(total_medisave), color="var(--accent)"), unsafe_allow_html=True)
with nw2[2]:
    st.markdown(metric_card("Property", fmt(total_property), color="var(--accent)"), unsafe_allow_html=True)
