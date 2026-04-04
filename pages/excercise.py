import os
from datetime import date

import pandas as pd
import streamlit as st

from theme import inject_theme, nav_menu, page_header, metric_card, section_card, status_badge as theme_badge, progress_bar, ACCENT, POS
from utils import safe_float, clean_text as safe_text, backup_csv

st.set_page_config(page_title="Exercise", page_icon="🏃", layout="wide", initial_sidebar_state="collapsed")

# =========================================================
# PATHS
# =========================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
EXERCISE_FILE = os.path.join(DATA_DIR, "exercise.csv")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

BACKUP_FOLDER = os.path.join(DATA_DIR, "backups")
os.makedirs(BACKUP_FOLDER, exist_ok=True)

EXERCISE_COLUMNS = [
    "date",
    "status",
    "type",
    "duration",
    "km",
    "pace",
    "notes",
]

# =========================================================
# HELPERS
# =========================================================
def safe_read_csv(path, columns=None):
    if not os.path.exists(path):
        return pd.DataFrame(columns=columns or [])
    try:
        df = pd.read_csv(path)
        if df.empty:
            return pd.DataFrame(columns=columns or list(df.columns))
        return df
    except Exception:
        return pd.DataFrame(columns=columns or [])


def ensure_columns(df, columns):
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    return df[columns]


def save_exercise_df(df):
    backup_csv(EXERCISE_FILE)
    df = ensure_columns(df, EXERCISE_COLUMNS)
    df.to_csv(EXERCISE_FILE, index=False)


def calculate_pace(duration_min, km):
    duration_min = safe_float(duration_min)
    km = safe_float(km)

    if km <= 0:
        return "-"

    pace = duration_min / km
    minutes = int(pace)
    seconds = int(round((pace - minutes) * 60))

    if seconds == 60:
        minutes += 1
        seconds = 0

    return f"{minutes}:{seconds:02d} /km"


def get_today_row(df, selected_date_str):
    if df.empty or "date" not in df.columns:
        return None

    temp = df.copy()
    temp["date"] = temp["date"].astype(str)
    rows = temp[temp["date"] == selected_date_str]

    if rows.empty:
        return None
    return rows.iloc[0]


def get_status_badge(status):
    s = safe_text(status).lower()
    if s in ["done", "completed", "yes"]:
        return "✅ Completed"
    elif s in ["rest", "off"]:
        return "🛌 Rest Day"
    elif s in ["planned", "scheduled"]:
        return "📌 Planned"
    return "⚪ Logged"


# =========================================================
# LOAD DATA
# =========================================================
exercise_df = safe_read_csv(EXERCISE_FILE, EXERCISE_COLUMNS)
exercise_df = ensure_columns(exercise_df, EXERCISE_COLUMNS)

if not exercise_df.empty:
    exercise_df["duration"] = exercise_df["duration"].apply(safe_float)
    exercise_df["km"] = exercise_df["km"].apply(safe_float)

today_str = str(date.today())
today_row = get_today_row(exercise_df, today_str)

# =========================================================
# THEME
# =========================================================
inject_theme()
nav_menu("Exercise")

# =========================================================
# HEADER
# =========================================================
st.markdown(page_header("Exercise", "Track your runs, workout time, and total progress to date."), unsafe_allow_html=True)

if today_row is not None:
    today_status_text = get_status_badge(today_row.get("status", ""))
    today_type = safe_text(today_row.get("type", "")) or "No type"
    today_km = safe_float(today_row.get("km", 0))
    today_duration = safe_float(today_row.get("duration", 0))
    today_pace = safe_text(today_row.get("pace", "")) or calculate_pace(today_duration, today_km)
    hero_text = f"{today_status_text} &bull; {today_type} &bull; {today_km:.2f} km &bull; {today_duration:.0f} min &bull; {today_pace}"
else:
    hero_text = "No exercise logged for today yet — put one entry in and start stacking the days."

st.markdown(
    f"""
    <div class="hero-banner">
        <div class="hero-label">Today's Exercise Status</div>
        <div class="hero-value">{hero_text}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# METRICS
# =========================================================
total_runs = 0
total_km = 0.0
total_minutes = 0.0

if not exercise_df.empty:
    done_df = exercise_df.copy()
    done_df["status"] = done_df["status"].astype(str).str.lower()
    done_df = done_df[done_df["status"].isin(["done", "completed", "yes"])]

    total_runs = len(done_df)
    total_km = done_df["km"].apply(safe_float).sum()
    total_minutes = done_df["duration"].apply(safe_float).sum()

m1, m2, m3 = st.columns(3, gap="large")

with m1:
    today_km_val = safe_float(today_row.get("km", 0)) if today_row is not None else 0
    st.markdown(
        metric_card("Today's Run", f"{today_km_val:.2f} km", "Distance logged for today's entry"),
        unsafe_allow_html=True,
    )

with m2:
    today_dur_val = safe_float(today_row.get("duration", 0)) if today_row is not None else 0
    st.markdown(
        metric_card("Today's Time", f"{today_dur_val:.0f} min", "Workout / run duration for today"),
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        metric_card("Total Run To Date", f"{total_km:.2f} km", f"{total_runs} completed session(s) &bull; {total_minutes:.0f} total min"),
        unsafe_allow_html=True,
    )

# =========================================================
# FORM + TODAY SUMMARY
# =========================================================
left_col, right_col = st.columns([1.1, 0.9], gap="large")

with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Log / Update Today\'s Exercise</div>', unsafe_allow_html=True)

    default_status = "done"
    default_type = "Run"
    default_duration = 0.0
    default_km = 0.0
    default_notes = ""

    if today_row is not None:
        default_status = safe_text(today_row.get("status", "done")) or "done"
        default_type = safe_text(today_row.get("type", "Run")) or "Run"
        default_duration = safe_float(today_row.get("duration", 0))
        default_km = safe_float(today_row.get("km", 0))
        default_notes = safe_text(today_row.get("notes", ""))

    selected_date = st.date_input("Date", value=date.today())
    status = st.selectbox(
        "Status",
        ["done", "planned", "rest", "off"],
        index=["done", "planned", "rest", "off"].index(default_status) if default_status in ["done", "planned", "rest", "off"] else 0
    )
    exercise_type = st.selectbox(
        "Exercise Type",
        ["Run", "Walk", "Gym", "Cycle", "Stretch", "Recovery", "Other"],
        index=["Run", "Walk", "Gym", "Cycle", "Stretch", "Recovery", "Other"].index(default_type)
        if default_type in ["Run", "Walk", "Gym", "Cycle", "Stretch", "Recovery", "Other"]
        else 0
    )

    c1, c2 = st.columns(2)
    with c1:
        duration = st.number_input("Time (minutes)", min_value=0.0, value=float(default_duration), step=1.0)
    with c2:
        km = st.number_input("How many km", min_value=0.0, value=float(default_km), step=0.1)

    pace = calculate_pace(duration, km)
    st.caption(f"Calculated Pace: {pace}")

    notes = st.text_area("Notes", value=default_notes, placeholder="Example: Easy 5km run, tired legs, evening session")

    save_btn = st.button("Save / Update Today", use_container_width=True)

    selected_date_str = str(selected_date)

    if save_btn:
        pace_value = calculate_pace(duration, km)

        new_row = {
            "date": selected_date_str,
            "status": status,
            "type": exercise_type,
            "duration": round(float(duration), 2),
            "km": round(float(km), 2),
            "pace": pace_value,
            "notes": notes.strip(),
        }

        if exercise_df.empty:
            updated_df = pd.DataFrame([new_row], columns=EXERCISE_COLUMNS)
        else:
            temp_df = exercise_df.copy()
            temp_df["date"] = temp_df["date"].astype(str)

            if selected_date_str in temp_df["date"].values:
                temp_df.loc[temp_df["date"] == selected_date_str, EXERCISE_COLUMNS] = list(new_row.values())
                updated_df = temp_df
            else:
                updated_df = pd.concat([temp_df, pd.DataFrame([new_row])], ignore_index=True)

        save_exercise_df(updated_df)
        st.success("Exercise saved.")
        st.rerun()

    st.markdown(
        '<div class="c-muted" style="font-size:13px;margin-top:8px;">One date = one exercise record. Saving again on the same date updates that entry instead of creating duplicates.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Today Summary</div>', unsafe_allow_html=True)

    if today_row is None:
        st.markdown('<div class="warning-box">No exercise logged for today yet.</div>', unsafe_allow_html=True)
    else:
        badge_text = get_status_badge(today_row.get('status', ''))
        st.write(f"**Status:** {badge_text}")
        st.write(f"**Type:** {safe_text(today_row.get('type', '-')) or '-'}")
        st.write(f"**Distance:** {safe_float(today_row.get('km', 0)):.2f} km")
        st.write(f"**Time:** {safe_float(today_row.get('duration', 0)):.0f} min")
        current_pace = safe_text(today_row.get("pace", "")) or calculate_pace(
            safe_float(today_row.get("duration", 0)),
            safe_float(today_row.get("km", 0))
        )
        st.write(f"**Pace:** {current_pace}")
        st.write(f"**Notes:** {safe_text(today_row.get('notes', '-')) or '-'}")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Quick Insight</div>', unsafe_allow_html=True)

    if total_km <= 0:
        st.write("Start with simple consistency first. One logged session begins the streak.")
    elif total_km < 20:
        st.write("Good start. Build the habit before worrying too much about performance.")
    elif total_km < 100:
        st.write("You are building real mileage now. Protect recovery and keep the rhythm steady.")
    else:
        st.write("You already have meaningful volume. Focus on consistency, pace control, and recovery quality.")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# HISTORY
# =========================================================
st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Exercise History</div>', unsafe_allow_html=True)

if exercise_df.empty:
    st.info("No exercise records yet.")
else:
    history_df = exercise_df.copy()
    history_df["duration"] = history_df["duration"].apply(safe_float)
    history_df["km"] = history_df["km"].apply(safe_float)
    history_df["date"] = history_df["date"].astype(str)
    history_df = history_df.sort_values(by="date", ascending=False)

    display_df = history_df.rename(
        columns={
            "date": "Date",
            "status": "Status",
            "type": "Type",
            "duration": "Time (min)",
            "km": "KM",
            "pace": "Pace",
            "notes": "Notes",
        }
    )

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Run trend chart (last 14 sessions with km > 0)
    run_chart_df = history_df[history_df["km"] > 0].sort_values("date").tail(14)
    if not run_chart_df.empty:
        st.markdown('<div class="section-title" style="margin-top:20px;">Distance Trend (last 14 sessions)</div>', unsafe_allow_html=True)
        chart_data = run_chart_df.set_index("date")[["km"]]
        st.line_chart(chart_data, height=180)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Delete a record</div>', unsafe_allow_html=True)
    date_options = history_df["date"].tolist()
    delete_date = st.selectbox("Select date to delete", date_options)

    if st.button("Delete Selected Record", type="secondary"):
        updated_df = history_df[history_df["date"] != delete_date].copy()
        save_exercise_df(updated_df)
        st.success("Exercise record deleted.")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
