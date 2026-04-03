import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, time as dtime
from theme import inject_theme, page_header, metric_card, section_card, detail_row, status_badge, ACCENT, POS, NEG

st.set_page_config(page_title="Driving", page_icon="🚗", layout="wide")

inject_theme()

st.markdown(page_header("Driving", "Income tracking"), unsafe_allow_html=True)

DATA_FOLDER = "data"
DRIVING_FILE = os.path.join(DATA_FOLDER, "driving.csv")

os.makedirs(DATA_FOLDER, exist_ok=True)

BACKUP_FOLDER = os.path.join(DATA_FOLDER, "backups")
os.makedirs(BACKUP_FOLDER, exist_ok=True)

def backup_csv(filepath):
    """Create a timestamped backup before writing."""
    if os.path.exists(filepath):
        from datetime import datetime as dt_cls
        import shutil, glob
        basename = os.path.basename(filepath).replace(".csv", "")
        stamp = dt_cls.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(filepath, os.path.join(BACKUP_FOLDER, f"{basename}_{stamp}.csv"))
        for old in sorted(glob.glob(os.path.join(BACKUP_FOLDER, f"{basename}_*.csv")))[:-20]:
            os.remove(old)

SETTINGS_FILE = os.path.join(DATA_FOLDER, "settings.csv")
DAILY_TARGET = 250.0
HOURLY_TARGET = 30.0
if os.path.exists(SETTINGS_FILE):
    try:
        _settings = pd.read_csv(SETTINGS_FILE)
        if "daily_income_target" in _settings.columns and not _settings.empty:
            DAILY_TARGET = float(_settings.loc[0, "daily_income_target"])
        if "hourly_rate_target" in _settings.columns and not _settings.empty:
            HOURLY_TARGET = float(_settings.loc[0, "hourly_rate_target"])
    except Exception:
        pass

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
    st.markdown('<div class="section-title">Enter Driving Data</div>', unsafe_allow_html=True)
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
                backup_csv(DRIVING_FILE)
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
                    target_status = "Target Achieved" if float(earnings) >= DAILY_TARGET else "Below Target"

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
                    backup_csv(DRIVING_FILE)
                    driving_df.to_csv(DRIVING_FILE, index=False)

                    st.success(f"🚗 Driving record saved for {selected_date}.")
                    st.rerun()

# =========================
# DASHBOARD
# =========================
with col2:
    st.markdown('<div class="section-title">Driving Dashboard</div>', unsafe_allow_html=True)

    selected_data = driving_df[driving_df["date"] == selected_date]

    if not selected_data.empty:
        row = selected_data.iloc[0]

        if row["day_type"] == "Off Day":
            st.markdown(metric_card("Status", "Rest Day", f"No driving on {selected_date}"), unsafe_allow_html=True)
        else:
            # Earnings metric card
            earn_val = float(row['earnings'])
            earn_color = POS if earn_val >= DAILY_TARGET else NEG
            st.markdown(
                metric_card("Earnings", f"${earn_val:.2f}", f"Target: ${DAILY_TARGET:.0f}", color=earn_color),
                unsafe_allow_html=True
            )

            # Detail rows inside a card
            hours_val = float(row['hours_driven'])
            rate_val = float(row['hourly_rate'])
            rate_cls = "positive" if rate_val >= HOURLY_TARGET else "negative"

            details_html = (
                detail_row("Date", selected_date)
                + detail_row("Start Time", str(row['start_time']))
                + detail_row("End Time", str(row['end_time']))
                + detail_row("Hours Driven", f"{hours_val:.2f}")
                + detail_row("Hourly Rate", f"${rate_val:.2f}/hr", cls=rate_cls)
            )
            st.markdown(section_card("Session Details", details_html), unsafe_allow_html=True)

            # Target status badge
            if row["target_status"] == "Target Achieved":
                badge_html = status_badge("Target Achieved", POS)
            else:
                badge_html = status_badge(f"Below ${DAILY_TARGET:.0f} Target", NEG)

            # Hourly rate badge
            if rate_val >= HOURLY_TARGET:
                rate_badge = status_badge(f"Good Rate (>= ${HOURLY_TARGET:.0f}/hr)", POS)
            else:
                rate_badge = status_badge(f"Rate Below ${HOURLY_TARGET:.0f}/hr", NEG)

            st.markdown(f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px">{badge_html} {rate_badge}</div>', unsafe_allow_html=True)
    else:
        st.markdown(metric_card("Status", "No Data", f"No record for {selected_date}"), unsafe_allow_html=True)

# =========================
# NOTE
# =========================
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<p class="c-muted">Finance page handles expenses. Driving page only tracks income.</p>', unsafe_allow_html=True)
