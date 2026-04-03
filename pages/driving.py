import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, time as dtime

st.set_page_config(page_title="Driving", page_icon="🚗", layout="wide")

st.markdown("""
<style>
:root {
    --accent: #8a7055;
    --pos: #5a9a6a; --neg: #b87070;
    --border: 1px solid rgba(0,0,0,0.07);
    --shadow: 0 1px 3px rgba(0,0,0,0.04);
    --radius: 18px;
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
html:not([data-theme="dark"]) .stApp { background-color: #f5f0e8 !important; color: #3a3028 !important; }
html:not([data-theme="dark"]) section[data-testid="stSidebar"] > div:first-child { background-color: #ede8de !important; }
html:not([data-theme="dark"]) header[data-testid="stHeader"] { background-color: #f5f0e8 !important; }
.stDecoration { display: none !important; }
html, body, [class*="css"] { font-family: Georgia, 'Times New Roman', serif !important; }
.block-container {
    max-width: 1200px;
    padding-top: 4rem !important;
    padding-bottom: 4rem !important;
}
div[data-testid="stForm"] {
    border: none !important; padding: 0 !important; background: transparent !important;
}
div[data-testid="stTextInput"] input {
    border-radius: 12px !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
    font-family: Georgia, serif !important;
}
div.stButton > button {
    border-radius: 12px !important;
    border: 1px solid rgba(0,0,0,0.14) !important;
    font-weight: 400 !important;
    font-family: Georgia, serif !important;
    background: var(--secondary-background-color) !important;
    color: inherit !important;
}
div.stButton > button:hover {
    border-color: var(--accent) !important;
}
</style>
""", unsafe_allow_html=True)

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
_dark = st.session_state["dark_mode"]
_bg    = "#0e1117" if _dark else "#f5f0e8"
_sbg   = "#161b22" if _dark else "#ede8de"
_color = "#fafafa" if _dark else "#3a3028"
st.markdown(f"""<style>
.stApp {{ background-color: {_bg} !important; color: {_color} !important; }}
section[data-testid="stSidebar"] > div:first-child {{ background-color: {_sbg} !important; }}
header[data-testid="stHeader"] {{ background-color: {_bg} !important; }}
</style>""", unsafe_allow_html=True)

st.title("🚗 Driving Command Center")
st.subheader("Track your driving performance and daily income")
st.markdown("---")

DATA_FOLDER = "data"
DRIVING_FILE = os.path.join(DATA_FOLDER, "driving.csv")

os.makedirs(DATA_FOLDER, exist_ok=True)

required_columns = [
    "date",
    "day_type",
    "start_time",
    "end_time",
    "hours_driven",
    "earnings",
    "hourly_rate",
    "target_status"
]

# =========================
# FILE SETUP
# =========================
if not os.path.exists(DRIVING_FILE):
    pd.DataFrame(columns=required_columns).to_csv(DRIVING_FILE, index=False)

driving_df = pd.read_csv(DRIVING_FILE)

# Reset if structure mismatch
if list(driving_df.columns) != required_columns:
    driving_df = pd.DataFrame(columns=required_columns)
    driving_df.to_csv(DRIVING_FILE, index=False)

driving_df = pd.read_csv(DRIVING_FILE)

# Clean types
if not driving_df.empty:
    driving_df["date"] = driving_df["date"].astype(str)

    numeric_cols = [
        "hours_driven",
        "earnings",
        "hourly_rate"
    ]
    for col in numeric_cols:
        driving_df[col] = pd.to_numeric(driving_df[col], errors="coerce").fillna(0.0)

today = str(date.today())

# =========================
# DATE SELECTOR
# =========================
selected_date = str(st.date_input("📅 Select Driving Date", value=date.today()))

# Prefill
selected_row_data = driving_df[driving_df["date"] == selected_date]

def parse_time(val, default_hour=8):
    try:
        if pd.isna(val) or str(val).strip() in ("", "nan"):
            return dtime(default_hour, 0)
        return datetime.strptime(str(val).strip(), "%H:%M").time()
    except Exception:
        return dtime(default_hour, 0)

prefill_day_type = "Driving"
prefill_start_time = dtime(8, 0)
prefill_end_time = dtime(18, 0)
prefill_earnings = 0.0

if not selected_row_data.empty:
    row0 = selected_row_data.iloc[0]
    prefill_day_type = row0["day_type"] if row0["day_type"] in ["Driving", "Off Day"] else "Driving"
    prefill_start_time = parse_time(row0["start_time"], default_hour=8)
    prefill_end_time = parse_time(row0["end_time"], default_hour=18)
    prefill_earnings = float(row0["earnings"])

col1, col2 = st.columns(2)

# =========================
# INPUT SECTION
# =========================
with col1:
    st.header("📝 Enter Driving Data")
    st.caption(f"Saving record for: {selected_date}")

    with st.form("driving_form"):
        day_type = st.selectbox(
            "Day Type",
            ["Driving", "Off Day"],
            index=0 if prefill_day_type == "Driving" else 1
        )

        start_time = st.time_input("Start Time", value=prefill_start_time)
        end_time = st.time_input("End Time", value=prefill_end_time)

        earnings = st.number_input(
            "Total Earnings",
            min_value=0.0,
            step=1.0,
            value=float(prefill_earnings)
        )

        submitted = st.form_submit_button("Save Record")

        if submitted:

            # OFF DAY
            if day_type == "Off Day":
                new_row = pd.DataFrame([{
                    "date": selected_date,
                    "day_type": "Off Day",
                    "start_time": "",
                    "end_time": "",
                    "hours_driven": 0.0,
                    "earnings": 0.0,
                    "hourly_rate": 0.0,
                    "target_status": "Rest Day"
                }])

                driving_df = driving_df[driving_df["date"] != selected_date]
                driving_df = pd.concat([driving_df, new_row], ignore_index=True)
                driving_df.to_csv(DRIVING_FILE, index=False)

                st.success(f"😴 Off day saved for {selected_date}.")
                st.rerun()

            # DRIVING DAY
            else:
                start_dt = datetime.combine(date.today(), start_time)
                end_dt = datetime.combine(date.today(), end_time)

                hours_driven = (end_dt - start_dt).total_seconds() / 3600

                # Handle overnight session (e.g. 22:00 → 03:00 next day)
                if hours_driven < 0:
                    hours_driven += 24

                if hours_driven <= 0:
                    st.error("Start and end time cannot be the same.")
                else:
                    hourly_rate = float(earnings) / hours_driven if hours_driven > 0 else 0.0
                    target_status = "Target Achieved" if float(earnings) >= 250 else "Below Target"

                    new_row = pd.DataFrame([{
                        "date": selected_date,
                        "day_type": "Driving",
                        "start_time": start_time.strftime("%H:%M"),
                        "end_time": end_time.strftime("%H:%M"),
                        "hours_driven": round(hours_driven, 2),
                        "earnings": round(float(earnings), 2),
                        "hourly_rate": round(hourly_rate, 2),
                        "target_status": target_status
                    }])

                    driving_df = driving_df[driving_df["date"] != selected_date]
                    driving_df = pd.concat([driving_df, new_row], ignore_index=True)
                    driving_df = driving_df.sort_values("date", ascending=False)
                    driving_df.to_csv(DRIVING_FILE, index=False)

                    st.success(f"🚗 Driving record saved for {selected_date}.")
                    st.rerun()

# =========================
# DASHBOARD
# =========================
with col2:
    st.header("📊 Driving Dashboard")

    selected_data = driving_df[driving_df["date"] == selected_date]

    if not selected_data.empty:
        row = selected_data.iloc[0]

        st.write(f"**Viewing Date:** {selected_date}")
        st.write(f"**Day Type:** {row['day_type']}")

        if row["day_type"] == "Off Day":
            st.info("😴 Rest Day — No driving recorded")
        else:
            st.write(f"**Start Time:** {row['start_time']}")
            st.write(f"**End Time:** {row['end_time']}")
            st.write(f"**Hours Driven:** {float(row['hours_driven']):.2f}")
            st.write(f"**Earnings:** ${float(row['earnings']):.2f}")
            st.write(f"**Hourly Rate:** ${float(row['hourly_rate']):.2f}/hr")

            if row["target_status"] == "Target Achieved":
                st.success("✅ Target Achieved")
            else:
                st.warning("⚠️ Below $250 Target")

            if float(row["hourly_rate"]) >= 30:
                st.success("💪 Good hourly rate")
            else:
                st.warning("📉 Hourly rate below $30/hr")
    else:
        st.info("No driving record saved for this date yet.")

# =========================
# NOTE
# =========================
st.markdown("---")
st.caption("Finance page handles expenses. Driving page only tracks income.")