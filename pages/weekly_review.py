import os
import calendar
from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Weekly Review", page_icon="📅", layout="wide")

# =========================================================
# PATHS
# =========================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

PLANNER_FILE  = os.path.join(DATA_DIR, "planner.csv")
DRIVING_FILE  = os.path.join(DATA_DIR, "driving.csv")
FINANCE_FILE  = os.path.join(DATA_DIR, "finance.csv")
MONTHLY_FILE  = os.path.join(DATA_DIR, "monthly_expenses.csv")
EXERCISE_FILE = os.path.join(DATA_DIR, "exercise.csv")


# =========================================================
# SAFE HELPERS
# =========================================================
def safe_read_csv(path, columns=None):
    if not os.path.exists(path):
        return pd.DataFrame(columns=columns or [])
    try:
        df = pd.read_csv(path)
        return pd.DataFrame(columns=columns or list(df.columns)) if df.empty else df
    except Exception:
        return pd.DataFrame(columns=columns or [])


def safe_float(value):
    try:
        return 0.0 if pd.isna(value) else float(value)
    except Exception:
        return 0.0


def safe_bool(value):
    return str(value).strip().lower() == "true"


def get_days_in_month(date_obj):
    return calendar.monthrange(date_obj.year, date_obj.month)[1]


# =========================================================
# DATA LOADERS
# =========================================================
@st.cache_data(ttl=15)
def load_planner():
    df = safe_read_csv(PLANNER_FILE)
    if df.empty:
        return df
    if "date" in df.columns:
        df["date"] = df["date"].astype(str)
    for col in ["focus_done", "run_done", "income_done"]:
        if col in df.columns:
            df[col] = df[col].apply(safe_bool)
    if "score" in df.columns:
        df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0).astype(int)
    return df


@st.cache_data(ttl=15)
def load_driving():
    df = safe_read_csv(DRIVING_FILE)
    if not df.empty:
        if "date" in df.columns:
            df["date"] = df["date"].astype(str)
        if "earnings" in df.columns:
            df["earnings"] = df["earnings"].apply(safe_float)
    return df


@st.cache_data(ttl=15)
def load_finance():
    df = safe_read_csv(FINANCE_FILE)
    if not df.empty:
        if "date" in df.columns:
            df["date"] = df["date"].astype(str)
        if "amount" in df.columns:
            df["amount"] = df["amount"].apply(safe_float)
    return df


@st.cache_data(ttl=15)
def load_monthly():
    df = safe_read_csv(MONTHLY_FILE)
    if not df.empty and "amount" in df.columns:
        df["amount"] = df["amount"].apply(safe_float)
    return df


@st.cache_data(ttl=15)
def load_exercise():
    df = safe_read_csv(EXERCISE_FILE)
    if not df.empty and "date" in df.columns:
        df["date"] = df["date"].astype(str)
    return df


# =========================================================
# WEEKLY CALCULATIONS
# =========================================================
today_obj = date.today()
week_start = today_obj - timedelta(days=6)
week_dates = [str(week_start + timedelta(days=i)) for i in range(7)]

planner_df  = load_planner()
driving_df  = load_driving()
finance_df  = load_finance()
monthly_df  = load_monthly()
exercise_df = load_exercise()

# --- Income ---
week_income = 0.0
if not driving_df.empty and "date" in driving_df.columns and "earnings" in driving_df.columns:
    mask = driving_df["date"].isin(week_dates)
    week_income = round(driving_df.loc[mask, "earnings"].sum(), 2)

# --- Variable expenses ---
week_variable_exp = 0.0
if not finance_df.empty and "date" in finance_df.columns and "amount" in finance_df.columns:
    mask = finance_df["date"].isin(week_dates)
    week_variable_exp = round(finance_df.loc[mask, "amount"].sum(), 2)

# --- Fixed daily share * 7 ---
daily_fixed_share = 0.0
if not monthly_df.empty and "amount" in monthly_df.columns:
    total_fixed = monthly_df["amount"].apply(safe_float).sum()
    days_in_month = get_days_in_month(today_obj)
    daily_fixed_share = round(total_fixed / days_in_month, 2) if days_in_month > 0 else 0.0
week_fixed = round(daily_fixed_share * 7, 2)

week_total_exp = round(week_variable_exp + week_fixed, 2)
week_net = round(week_income - week_total_exp, 2)

# --- Avg score ---
week_avg_score = 0.0
if not planner_df.empty and "score" in planner_df.columns and "date" in planner_df.columns:
    mask = planner_df["date"].isin(week_dates)
    week_scores = planner_df.loc[mask]
    if not week_scores.empty:
        week_avg_score = round(week_scores["score"].mean(), 1)

# --- Exercise count ---
exercise_count = 0
if not exercise_df.empty and "date" in exercise_df.columns and "status" in exercise_df.columns:
    mask = exercise_df["date"].isin(week_dates)
    week_ex = exercise_df.loc[mask]
    exercise_count = int(week_ex["status"].apply(
        lambda v: str(v).strip().lower() in ("done", "completed", "yes")
    ).sum())

# --- Best / worst day ---
best_day = "N/A"
worst_day = "N/A"
if not planner_df.empty and "score" in planner_df.columns and "date" in planner_df.columns:
    mask = planner_df["date"].isin(week_dates)
    week_plan = planner_df.loc[mask].copy()
    if not week_plan.empty:
        best_day = week_plan.loc[week_plan["score"].idxmax(), "date"]
        worst_day = week_plan.loc[week_plan["score"].idxmin(), "date"]

# --- Day-by-day data ---
day_rows = []
for d in week_dates:
    score = 0
    if not planner_df.empty and "date" in planner_df.columns and "score" in planner_df.columns:
        rows = planner_df[planner_df["date"] == d]
        if not rows.empty:
            score = int(rows.iloc[0]["score"])

    income = 0.0
    if not driving_df.empty and "date" in driving_df.columns and "earnings" in driving_df.columns:
        rows = driving_df[driving_df["date"] == d]
        if not rows.empty:
            income = round(rows["earnings"].sum(), 2)

    expense = 0.0
    if not finance_df.empty and "date" in finance_df.columns and "amount" in finance_df.columns:
        rows = finance_df[finance_df["date"] == d]
        if not rows.empty:
            expense = round(rows["amount"].sum(), 2)

    day_net = round(income - expense - daily_fixed_share, 2)
    day_rows.append({"Date": d, "Score": score, "Income": income, "Expense": expense, "Net": day_net})


# =========================================================
# STYLING
# =========================================================
st.markdown("""
<style>
/* ── TOKENS ── */
:root {
    --border: 1px solid rgba(0,0,0,0.07);
    --shadow: 0 1px 3px rgba(0,0,0,0.04);
    --radius-lg: 18px; --radius-md: 12px;
    --accent: #8a7055;
    --pos: #5a9a6a; --neg: #b87070;
}
@media (prefers-color-scheme: dark) {
    :root {
        --accent: #b08a65;
        --border: 1px solid rgba(255,255,255,0.07);
        --shadow: 0 1px 3px rgba(0,0,0,0.12);
        --pos: #7ab88a;
    }
}
[data-theme="dark"] {
    --accent: #b08a65;
    --border: 1px solid rgba(255,255,255,0.07);
    --shadow: 0 1px 3px rgba(0,0,0,0.12);
    --pos: #7ab88a;
}

.stDecoration { display: none !important; }
html, body, [class*="css"] { font-family: Georgia, 'Times New Roman', serif !important; }

.block-container { max-width:1200px; padding-top:4rem !important; padding-bottom:4rem !important; }
.metric-card { border:var(--border); border-radius:var(--radius-lg); padding:22px 22px 18px; background:var(--secondary-background-color); box-shadow:var(--shadow); min-height:130px; height:100%; }
.metric-label { font-size:10px; opacity:0.55; margin-bottom:7px; text-transform:uppercase; letter-spacing:0.12em; font-weight:400; }
.metric-value { font-size:2rem; font-weight:500; line-height:1.1; margin-bottom:5px; letter-spacing:-0.02em; }
.metric-sub { font-size:13px; opacity:0.68; line-height:1.6; }
.section-card { border:var(--border); border-radius:var(--radius-lg); padding:24px 28px; background:var(--secondary-background-color); box-shadow:var(--shadow); height:100%; }
.section-title { font-size:1rem; font-weight:500; margin-bottom:1rem; letter-spacing:-0.01em; }
.detail-list { display:grid; gap:0; }
.detail-row { display:flex; justify-content:space-between; align-items:center; gap:16px; padding:11px 0; border-bottom:1px solid rgba(0,0,0,0.05); font-size:0.93rem; }
.detail-row:last-child { border-bottom:none; }
.detail-key { opacity:0.65; } .detail-value { font-weight:500; text-align:right; }
.positive { color: var(--pos); }
.negative { color: var(--neg); }
.day-table { width:100%; border-collapse:collapse; font-size:0.9rem; }
.day-table th { text-align:left; padding:10px 12px; border-bottom:2px solid rgba(0,0,0,0.08); font-size:10px; text-transform:uppercase; letter-spacing:0.12em; opacity:0.55; font-weight:400; }
.day-table td { padding:10px 12px; border-bottom:1px solid rgba(0,0,0,0.05); }
.day-table tr:last-child td { border-bottom:none; }
.page-subtitle { font-size:1rem; opacity:0.6; margin-top:-8px; margin-bottom:20px; }
</style>
""", unsafe_allow_html=True)

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
_dark = st.session_state["dark_mode"]
_bg = "#0e1117" if _dark else "#f5f0e8"
_sbg = "#161b22" if _dark else "#ede8de"
_color = "#fafafa" if _dark else "#3a3028"
st.markdown(f"""<style>
.stApp {{ background-color: {_bg} !important; color: {_color} !important; }}
section[data-testid="stSidebar"] > div:first-child {{ background-color: {_sbg} !important; }}
header[data-testid="stHeader"] {{ background-color: {_bg} !important; }}
</style>""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================
st.title("📅 Weekly Review")
st.markdown(
    '<div class="page-subtitle">'
    + week_start.strftime("%b %d") + " — " + today_obj.strftime("%b %d, %Y")
    + '</div>',
    unsafe_allow_html=True,
)

# =========================================================
# TOP METRIC CARDS
# =========================================================
net_cls = "positive" if week_net > 0 else ("negative" if week_net < 0 else "")
net_sign = "+" if week_net > 0 else ""

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        '<div class="metric-card">'
        '<div class="metric-label">Week Income</div>'
        '<div class="metric-value">$' + f"{week_income:,.2f}" + '</div>'
        '<div class="metric-sub">Driving earnings</div>'
        '</div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        '<div class="metric-card">'
        '<div class="metric-label">Week Expenses</div>'
        '<div class="metric-value">$' + f"{week_total_exp:,.2f}" + '</div>'
        '<div class="metric-sub">Variable $' + f"{week_variable_exp:,.2f}" + ' + Fixed $' + f"{week_fixed:,.2f}" + '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        '<div class="metric-card">'
        '<div class="metric-label">Week Net</div>'
        '<div class="metric-value ' + net_cls + '">' + net_sign + '$' + f"{week_net:,.2f}" + '</div>'
        '<div class="metric-sub">Income minus total expenses</div>'
        '</div>',
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        '<div class="metric-card">'
        '<div class="metric-label">Avg Score</div>'
        '<div class="metric-value">' + str(week_avg_score) + '<span style="font-size:0.5em;opacity:0.5"> /100</span></div>'
        '<div class="metric-sub">7-day execution average</div>'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# =========================================================
# TWO-COLUMN: FINANCIAL BREAKDOWN + EXECUTION SUMMARY
# =========================================================
col_fin, col_exec = st.columns(2)

with col_fin:
    rows_html = ""
    for key, val, cls in [
        ("Driving Income", f"${week_income:,.2f}", "positive" if week_income > 0 else ""),
        ("Variable Expenses", f"${week_variable_exp:,.2f}", "negative" if week_variable_exp > 0 else ""),
        ("Fixed Expenses (7d share)", f"${week_fixed:,.2f}", "negative" if week_fixed > 0 else ""),
        ("Total Expenses", f"${week_total_exp:,.2f}", "negative" if week_total_exp > 0 else ""),
        ("Net Result", (net_sign + "$" + f"{week_net:,.2f}"), net_cls),
    ]:
        rows_html += (
            '<div class="detail-row">'
            '<div class="detail-key">' + key + '</div>'
            '<div class="detail-value ' + cls + '">' + val + '</div>'
            '</div>'
        )

    st.markdown(
        '<div class="section-card">'
        '<div class="section-title">Financial Breakdown</div>'
        '<div class="detail-list">' + rows_html + '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

with col_exec:
    score_cls = "positive" if week_avg_score >= 70 else ("negative" if week_avg_score < 50 else "")
    exec_rows_html = ""
    for key, val, cls in [
        ("Avg Score", str(week_avg_score) + " / 100", score_cls),
        ("Exercise Days", str(exercise_count) + " / 7", "positive" if exercise_count >= 5 else ("negative" if exercise_count < 3 else "")),
        ("Best Day", best_day, ""),
        ("Worst Day", worst_day, ""),
        ("Days Logged", str(len(planner_df[planner_df["date"].isin(week_dates)])) + " / 7" if not planner_df.empty and "date" in planner_df.columns else "0 / 7", ""),
    ]:
        exec_rows_html += (
            '<div class="detail-row">'
            '<div class="detail-key">' + key + '</div>'
            '<div class="detail-value ' + cls + '">' + val + '</div>'
            '</div>'
        )

    st.markdown(
        '<div class="section-card">'
        '<div class="section-title">Execution Summary</div>'
        '<div class="detail-list">' + exec_rows_html + '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# =========================================================
# DAY-BY-DAY TABLE
# =========================================================
table_rows = ""
for row in day_rows:
    net_val = row["Net"]
    net_td_cls = "positive" if net_val > 0 else ("negative" if net_val < 0 else "")
    net_prefix = "+" if net_val > 0 else ""
    score_td_cls = "positive" if row["Score"] >= 70 else ("negative" if row["Score"] < 50 and row["Score"] > 0 else "")
    table_rows += (
        '<tr>'
        '<td>' + row["Date"] + '</td>'
        '<td class="' + score_td_cls + '">' + str(row["Score"]) + '</td>'
        '<td>$' + f'{row["Income"]:,.2f}' + '</td>'
        '<td>$' + f'{row["Expense"]:,.2f}' + '</td>'
        '<td class="' + net_td_cls + '">' + net_prefix + '$' + f'{net_val:,.2f}' + '</td>'
        '</tr>'
    )

st.markdown(
    '<div class="section-card">'
    '<div class="section-title">Day-by-Day Breakdown</div>'
    '<table class="day-table">'
    '<thead><tr><th>Date</th><th>Score</th><th>Income</th><th>Expense</th><th>Net</th></tr></thead>'
    '<tbody>' + table_rows + '</tbody>'
    '</table>'
    '</div>',
    unsafe_allow_html=True,
)
