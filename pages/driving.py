import streamlit as st
import pandas as pd
from datetime import datetime, date, time as dtime
from theme import inject_theme, nav_menu, page_header, metric_card, section_card, detail_row, status_badge, ACCENT, POS, NEG
from utils import (
    load_driving, load_settings, save_driving_df,
    DRIVING_COLUMNS, safe_float,
)

st.set_page_config(page_title="Driving", page_icon="🚗", layout="wide", initial_sidebar_state="collapsed")

inject_theme()
nav_menu("Driving")

st.markdown(page_header("Driving", "Income tracking"), unsafe_allow_html=True)

# ── Load settings for targets ─────────────────────────────────────────
DAILY_TARGET = 250.0
HOURLY_TARGET = 30.0
try:
    _settings = load_settings()
    if "daily_income_target" in _settings.columns and not _settings.empty:
        DAILY_TARGET = float(_settings.loc[0, "daily_income_target"])
    if "hourly_rate_target" in _settings.columns and not _settings.empty:
        HOURLY_TARGET = float(_settings.loc[0, "hourly_rate_target"])
except Exception:
    pass

# ── Cache helpers ─────────────────────────────────────────────────────
@st.cache_data(ttl=15)
def _load_driving():
    df = load_driving()
    if "date" in df.columns:
        df["date"] = df["date"].astype(str)
    return df


def _invalidate():
    _load_driving.clear()


driving_df = _load_driving()
today = str(date.today())

# =========================
# DATE SELECTOR
# =========================
selected_date = str(st.date_input("📅 Select Driving Date", value=date.today()))

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
    prefill_earnings = safe_float(row0["earnings"])

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
        earnings = st.number_input("Total Earnings", min_value=0.0, step=1.0, value=float(prefill_earnings))
        submitted = st.form_submit_button("Save Record")

        if submitted:
            if day_type == "Off Day":
                new_row = pd.DataFrame([{
                    "date": selected_date, "day_type": "Off Day",
                    "start_time": "", "end_time": "",
                    "hours_driven": 0.0, "earnings": 0.0,
                    "hourly_rate": 0.0, "target_status": "Rest Day",
                }])
                updated = driving_df[driving_df["date"] != selected_date]
                updated = pd.concat([updated, new_row], ignore_index=True)
                save_driving_df(updated)
                _invalidate()
                st.success(f"😴 Off day saved for {selected_date}.")
                st.rerun()
            else:
                start_dt = datetime.combine(date.today(), start_time)
                end_dt = datetime.combine(date.today(), end_time)
                hours_driven = (end_dt - start_dt).total_seconds() / 3600
                if hours_driven < 0:
                    hours_driven += 24
                if hours_driven <= 0:
                    st.error("Start and end time cannot be the same.")
                else:
                    hourly_rate = float(earnings) / hours_driven if hours_driven > 0 else 0.0
                    target_status = "Target Achieved" if float(earnings) >= DAILY_TARGET else "Below Target"
                    new_row = pd.DataFrame([{
                        "date": selected_date, "day_type": "Driving",
                        "start_time": start_time.strftime("%H:%M"),
                        "end_time": end_time.strftime("%H:%M"),
                        "hours_driven": round(hours_driven, 2),
                        "earnings": round(float(earnings), 2),
                        "hourly_rate": round(hourly_rate, 2),
                        "target_status": target_status,
                    }])
                    updated = driving_df[driving_df["date"] != selected_date]
                    updated = pd.concat([updated, new_row], ignore_index=True)
                    updated = updated.sort_values("date", ascending=False)
                    save_driving_df(updated)
                    _invalidate()
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
            earn_val = safe_float(row['earnings'])
            earn_color = POS if earn_val >= DAILY_TARGET else NEG
            st.markdown(
                metric_card("Earnings", f"${earn_val:.2f}", f"Target: ${DAILY_TARGET:.0f}", color=earn_color),
                unsafe_allow_html=True
            )
            hours_val = safe_float(row['hours_driven'])
            rate_val = safe_float(row['hourly_rate'])
            rate_cls = "positive" if rate_val >= HOURLY_TARGET else "negative"
            details_html = (
                detail_row("Date", selected_date)
                + detail_row("Start Time", str(row['start_time']))
                + detail_row("End Time", str(row['end_time']))
                + detail_row("Hours Driven", f"{hours_val:.2f}")
                + detail_row("Hourly Rate", f"${rate_val:.2f}/hr", cls=rate_cls)
            )
            st.markdown(section_card("Session Details", details_html), unsafe_allow_html=True)
            badge_html = status_badge("Target Achieved", POS) if row["target_status"] == "Target Achieved" else status_badge(f"Below ${DAILY_TARGET:.0f} Target", NEG)
            rate_badge = status_badge(f"Good Rate (>= ${HOURLY_TARGET:.0f}/hr)", POS) if rate_val >= HOURLY_TARGET else status_badge(f"Rate Below ${HOURLY_TARGET:.0f}/hr", NEG)
            st.markdown(f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px">{badge_html} {rate_badge}</div>', unsafe_allow_html=True)
    else:
        st.markdown(metric_card("Status", "No Data", f"No record for {selected_date}"), unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<p class="c-muted">Finance page handles expenses. Driving page only tracks income.</p>', unsafe_allow_html=True)
