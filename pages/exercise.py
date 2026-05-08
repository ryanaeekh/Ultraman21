import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Exercise", page_icon="\U0001f3c3", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header, metric_card
from utils import load_exercise, save_exercise_df, filter_by_exact_date

inject_theme()
nav_menu("Exercise")

st.markdown(page_header("Exercise", "Move with intention"), unsafe_allow_html=True)

exercise_df = load_exercise()

# ── Total km ──────────────────────────────────────────────
total_km = float(exercise_df["km"].sum()) if not exercise_df.empty else 0.0
st.markdown(
    f'<div class="card" style="margin-top:20px;text-align:center;">'
    f'<div class="section-title">\U0001f30d Total Distance</div>'
    f'<div class="metric-value" style="font-size:56px;color:var(--text);">{total_km:,.1f} km</div>'
    f'<div class="metric-sub">all sessions to date</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Today Summary ─────────────────────────────────────────
st.markdown('<div class="section-title">\U0001f4a5 Today&#39;s Summary</div>', unsafe_allow_html=True)

today_rows = filter_by_exact_date(exercise_df, date.today())
today_min = float(today_rows["duration"].sum()) if not today_rows.empty else 0.0
today_km = float(today_rows["km"].sum()) if not today_rows.empty else 0.0
today_pace = (today_min / today_km) if today_km > 0 else 0.0

cols = st.columns(3)
with cols[0]:
    st.markdown(metric_card("Minutes", f"{today_min:.0f}", color="var(--accent-2)"), unsafe_allow_html=True)
with cols[1]:
    st.markdown(metric_card("Distance", f"{today_km:.2f} km", color="var(--accent-2)"), unsafe_allow_html=True)
with cols[2]:
    pv = f"{today_pace:.2f}" if today_pace > 0 else "\u2014"
    st.markdown(metric_card("Avg Pace", pv, sub="min/km", color="var(--accent-2)"), unsafe_allow_html=True)

# ── Date ──────────────────────────────────────────────────
sel_date = st.date_input("Date", value=date.today(), key="ex_date")

# ── Type horizontal scroll ────────────────────────────────
if "ex_type" not in st.session_state:
    st.session_state.ex_type = "Run"
types = [("Run", "\U0001f3c3"), ("Walk", "\U0001f6b6"), ("Gym", "\U0001f3cb\ufe0f"), ("Other", "\u2728")]
t_cols = st.columns(len(types))
for i, (t, _) in enumerate(types):
    with t_cols[i]:
        if st.button(t, key=f"type_{t}", use_container_width=True):
            st.session_state.ex_type = t
ex_type = st.session_state.ex_type

type_html = '<div class="type-row">'
for t, emoji in types:
    c = "type-card active" if ex_type == t else "type-card"
    type_html += f'<div class="{c}"><span class="emoji">{emoji}</span>{t}</div>'
type_html += '</div>'
st.markdown(type_html, unsafe_allow_html=True)

# ── Duration / Distance ───────────────────────────────────
dcols = st.columns(2)
with dcols[0]:
    duration = st.number_input("Duration (min)", min_value=0.0, step=5.0, format="%.1f", key="ex_duration")
with dcols[1]:
    km = st.number_input("Distance (km)", min_value=0.0, step=0.1, format="%.2f", key="ex_km")

pace = 0.0
if km > 0 and duration > 0:
    pace = duration / km

pace_text = f"{pace:.2f} min/km" if pace > 0 else "\u2014"
st.markdown(
    f'<div style="text-align:center;margin:10px 0 18px;">'
    f'<span class="glow-badge">Pace \u00b7 {pace_text}</span></div>',
    unsafe_allow_html=True,
)

notes = st.text_input("Notes", key="ex_notes", placeholder="How did it feel?")

btn_cols = st.columns(2)
with btn_cols[0]:
    if st.button("Save Session", use_container_width=True, key="save_ex"):
        new_row = pd.DataFrame([{
            "date": str(sel_date),
            "status": "Done",
            "type": ex_type,
            "duration": float(duration),
            "km": float(km),
            "pace": f"{pace:.2f}" if pace > 0 else "",
            "notes": notes.strip(),
        }])
        save_exercise_df(pd.concat([exercise_df, new_row], ignore_index=True))
        st.success("Session saved.")
        st.rerun()
with btn_cols[1]:
    if st.button("Delete Session", use_container_width=True, key="del_ex"):
        matched = filter_by_exact_date(exercise_df, sel_date)
        if not matched.empty:
            save_exercise_df(exercise_df.drop(matched.index).reset_index(drop=True))
            st.success(f"Session on {sel_date} deleted.")
            st.rerun()
        else:
            st.warning("No session found for this date.")

# ── Last 7 Sessions ───────────────────────────────────────
st.markdown('<div class="section-title">\U0001f4dc Last 7 Sessions</div>', unsafe_allow_html=True)
if exercise_df.empty:
    st.markdown('<div class="list-row" style="justify-content:center;opacity:0.7;">No sessions yet.</div>', unsafe_allow_html=True)
else:
    recent = exercise_df.copy()
    recent["date"] = pd.to_datetime(recent["date"], errors="coerce")
    recent = recent.dropna(subset=["date"]).sort_values("date", ascending=False).head(7)
    rows_html = '<table class="day-table"><thead><tr><th>Date</th><th>Type</th><th>Duration</th><th>Distance</th><th>Pace</th></tr></thead><tbody>'
    for _, r in recent.iterrows():
        d = r["date"].strftime("%d %b")
        pace_val = r.get("pace", "")
        pace_val = pace_val if (isinstance(pace_val, str) and pace_val.strip()) else "\u2014"
        rows_html += (
            f'<tr><td>{d}</td><td>{r.get("type","")}</td>'
            f'<td>{float(r.get("duration",0)):.0f} min</td>'
            f'<td>{float(r.get("km",0)):.2f} km</td>'
            f'<td>{pace_val}</td></tr>'
        )
    rows_html += '</tbody></table>'
    st.markdown(rows_html, unsafe_allow_html=True)


# ── 12 Week Training Plan ─────────────────────────────────
st.markdown(
    '<div class="section-title" style="margin-top:36px;">\U0001f5d3️ 12 Week Training Plan</div>',
    unsafe_allow_html=True,
)


def _plan_table(rows, headers):
    html = '<table class="day-table" style="margin-top:8px;"><thead><tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr></thead><tbody>'
    for row in rows:
        html += '<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>'
    html += '</tbody></table>'
    return html


# Expander 1 — Weekly Structure
with st.expander("Weekly Structure", expanded=False):
    week_rows = [
        ("Monday", "\U0001f3c3 Run", "25–30 min"),
        ("Tuesday", "\U0001f4aa Strength", "40–45 min"),
        ("Wednesday", "\U0001f3c3 Run", "25–30 min"),
        ("Thursday", "\U0001f4aa Strength", "40–45 min"),
        ("Friday", "\U0001f3c3 Run", "25–30 min"),
        ("Saturday", "\U0001f4aa Strength", "40–45 min"),
        ("Sunday", "\U0001f634 Full Rest", "—"),
    ]
    st.markdown(_plan_table(week_rows, ["Day", "Focus", "Duration"]), unsafe_allow_html=True)


# Expander 2 — Running Plan
with st.expander("Running Plan", expanded=False):
    phases = [
        ("Phase 1", "Weeks 1–4", "3 km", "Comfortable pace, build habit"),
        ("Phase 2", "Weeks 5–8", "4 km", "Slightly faster, build endurance"),
        ("Phase 3", "Weeks 9–12", "5 km", "Steady and strong, maintain and push"),
    ]
    phase_cols = st.columns(3)
    for col, (phase, weeks, dist, desc) in zip(phase_cols, phases):
        with col:
            st.markdown(
                f'<div style="padding:18px 16px;border:1px solid var(--border);'
                f'border-radius:var(--radius-md);background:var(--accent-soft);'
                f'box-shadow:var(--shadow);min-height:180px;'
                f'display:flex;flex-direction:column;justify-content:space-between;">'
                f'<div>'
                f'<div style="font-family:var(--font-display);font-size:11px;'
                f'text-transform:uppercase;letter-spacing:0.12em;color:var(--accent);'
                f'margin-bottom:6px;">{phase}</div>'
                f'<div style="font-family:var(--font-display);font-size:13px;'
                f'color:var(--text2);margin-bottom:10px;">{weeks}</div>'
                f'<div style="font-family:var(--font-display);font-size:26px;'
                f'font-weight:700;color:var(--accent-2);margin-bottom:8px;">{dist}</div>'
                f'</div>'
                f'<div style="font-size:13px;color:var(--text);line-height:1.5;'
                f'opacity:0.88;">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


# Expander 3 — Strength Training
with st.expander("Strength Training", expanded=False):
    upper_tab, lower_tab, full_tab = st.tabs([
        "Monday · Upper Body",
        "Thursday · Lower Body",
        "Saturday · Full Body Core",
    ])

    warmup_html = (
        '<div style="padding:10px 14px;margin:4px 0 10px;'
        'border-left:3px solid var(--accent);background:var(--accent-soft);'
        'border-radius:var(--radius-md);font-size:13px;color:var(--text2);">'
        'Warm-up: 5 minutes light cardio + dynamic stretches before starting.'
        '</div>'
    )

    with upper_tab:
        st.markdown(warmup_html, unsafe_allow_html=True)
        upper_rows = [
            ("Push ups", "3 × 12–15"),
            ("Wide push ups", "3 × 12"),
            ("Diamond push ups", "3 × 10"),
            ("Pike push ups", "3 × 10"),
            ("Tricep dips", "3 × 12"),
            ("Plank", "3 × 45 sec"),
            ("Side plank", "2 × 30 sec each side"),
        ]
        st.markdown(_plan_table(upper_rows, ["Exercise", "Sets × Reps"]), unsafe_allow_html=True)

    with lower_tab:
        st.markdown(warmup_html, unsafe_allow_html=True)
        lower_rows = [
            ("Squats", "3 × 15"),
            ("Lunges", "3 × 12 each leg"),
            ("Bulgarian split squats", "3 × 10 each leg"),
            ("Glute bridges", "3 × 15"),
            ("Calf raises", "3 × 20"),
            ("Wall sit", "3 × 45 sec"),
            ("Leg raises", "3 × 15"),
        ]
        st.markdown(_plan_table(lower_rows, ["Exercise", "Sets × Reps"]), unsafe_allow_html=True)

    with full_tab:
        st.markdown(warmup_html, unsafe_allow_html=True)
        full_rows = [
            ("Squats", "3 × 15"),
            ("Push ups", "3 × 12"),
            ("Lunges", "3 × 10 each leg"),
            ("Plank", "3 × 60 sec"),
            ("Mountain climbers", "3 × 20"),
            ("Glute bridges", "3 × 15"),
            ("Crunches", "3 × 20"),
            ("Superman hold", "3 × 30 sec"),
        ]
        st.markdown(_plan_table(full_rows, ["Exercise", "Sets × Reps"]), unsafe_allow_html=True)
