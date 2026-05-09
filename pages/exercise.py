import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Exercise", page_icon="\U0001f3c3", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header, metric_card
from utils import (
    load_exercise, save_exercise_df, filter_by_exact_date,
    load_strength_log, save_strength_log_df,
)

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

# Notes (moved here, above strength log)
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

# ── Strength Training Log ─────────────────────────────────
st.markdown(
    '<div class="section-title" style="margin-top:8px;">\U0001f4aa Strength Training Log</div>',
    unsafe_allow_html=True,
)

strength_log_df = load_strength_log()
today = date.today()
today_str = str(today)

STRENGTH_DAYS = [
    ("Monday — Upper Body", "Monday", [
        "Warm up 5 min",
        "Push ups 3x12-15",
        "Wide push ups 3x12",
        "Diamond push ups 3x10",
        "Pike push ups 3x10",
        "Tricep dips 3x12",
        "Plank 3x45sec",
        "Side plank 2x30sec each",
        "Cool down 5 min stretch",
    ]),
    ("Thursday — Lower Body", "Thursday", [
        "Warm up 5 min",
        "Squats 3x15",
        "Lunges 3x12 each",
        "Bulgarian split squats 3x10 each",
        "Glute bridges 3x15",
        "Calf raises 3x20",
        "Wall sit 3x45sec",
        "Leg raises 3x15",
        "Cool down 5 min stretch",
    ]),
    ("Saturday — Full Body Core", "Saturday", [
        "Warm up 5 min",
        "Squats 3x15",
        "Push ups 3x12",
        "Lunges 3x10 each",
        "Plank 3x60sec",
        "Mountain climbers 3x20",
        "Glute bridges 3x15",
        "Crunches 3x20",
        "Superman hold 3x30sec",
        "Cool down 5 min stretch",
    ]),
]

for _label, _day_key, _exercises in STRENGTH_DAYS:
    with st.expander(_label, expanded=False):
        _existing = strength_log_df[
            (strength_log_df["date"].astype(str) == today_str)
            & (strength_log_df["day"].astype(str) == _day_key)
        ]
        _done_set = set(
            _existing[
                _existing["completed"].astype(str).str.lower().isin(["yes", "true", "1"])
            ]["exercise"].astype(str).tolist()
        )

        _checks = []
        for _i, _ex in enumerate(_exercises):
            _val = st.checkbox(
                _ex,
                value=(_ex in _done_set),
                key=f"strength_{_day_key}_{_i}",
            )
            _checks.append((_ex, _val))

        _done_count = sum(1 for _, c in _checks if c)
        _total = len(_checks)
        st.markdown(
            f'<div style="margin:8px 0 12px;padding:10px 14px;'
            f'border:1px solid var(--border);border-radius:var(--radius-md);'
            f'background:var(--accent-soft);text-align:center;'
            f'font-family:var(--font-display);font-size:13px;color:var(--text2);'
            f'letter-spacing:0.06em;">'
            f'<span style="color:var(--accent-2);font-weight:700;font-size:16px;">'
            f'{_done_count}/{_total}</span> completed</div>',
            unsafe_allow_html=True,
        )

        if st.button(
            f"Save {_day_key} log",
            use_container_width=True,
            key=f"save_strength_{_day_key}",
        ):
            _others = strength_log_df[
                ~(
                    (strength_log_df["date"].astype(str) == today_str)
                    & (strength_log_df["day"].astype(str) == _day_key)
                )
            ]
            _new_rows = pd.DataFrame([
                {
                    "date": today_str,
                    "day": _day_key,
                    "exercise": _ex,
                    "completed": "Yes" if _c else "No",
                }
                for _ex, _c in _checks
            ])
            _updated = pd.concat([_others, _new_rows], ignore_index=True)
            with st.spinner("Saving..."):
                save_strength_log_df(_updated)
            st.success(f"{_day_key} log saved.")
            st.rerun()

# ── Past Sessions (InnerWork style) ─────────────────────
total_sessions = int(len(exercise_df)) + int(len(strength_log_df["date"].unique())) if not strength_log_df.empty else int(len(exercise_df))

with st.expander(f"Past Sessions ({total_sessions} total)", expanded=False):
    if exercise_df.empty and strength_log_df.empty:
        st.markdown('<div class="list-row" style="justify-content:center;opacity:0.7;">No sessions yet.</div>', unsafe_allow_html=True)
    else:
        ctrl_cols = st.columns([6, 4])
        with ctrl_cols[0]:
            search = st.text_input(
                "Search",
                value="",
                key="exercise_search",
                placeholder="Search type, day, notes...",
                label_visibility="collapsed",
            )
        with ctrl_cols[1]:
            show_all = st.checkbox("Show all", value=False, key="exercise_show_all")
            st.caption("Last 30 days by default" if not show_all else "Showing all sessions")

        # Build unified session list (cardio + strength)
        unified = []

        # Cardio rows
        if not exercise_df.empty:
            cardio = exercise_df.copy()
            cardio["date_parsed"] = pd.to_datetime(cardio["date"], errors="coerce")
            cardio = cardio.dropna(subset=["date_parsed"])
            for idx, r in cardio.iterrows():
                unified.append({
                    "date_parsed": r["date_parsed"],
                    "date_str": r["date_parsed"].strftime("%Y-%m-%d"),
                    "kind": "cardio",
                    "type": str(r.get("type", "")),
                    "duration": float(r.get("duration", 0) or 0),
                    "km": float(r.get("km", 0) or 0),
                    "pace": str(r.get("pace", "")).strip(),
                    "notes": str(r.get("notes", "")).strip(),
                    "idx": idx,
                })

        # Strength rows (group by date+day)
        if not strength_log_df.empty:
            sl = strength_log_df.copy()
            sl["date_parsed"] = pd.to_datetime(sl["date"], errors="coerce")
            sl = sl.dropna(subset=["date_parsed"])
            grouped = sl.groupby(["date_parsed", "day"])
            for (dp, day), group in grouped:
                done = group[group["completed"].astype(str).str.lower().isin(["yes", "true", "1"])]
                unified.append({
                    "date_parsed": dp,
                    "date_str": dp.strftime("%Y-%m-%d"),
                    "kind": "strength",
                    "day": str(day),
                    "done_count": len(done),
                    "total_count": len(group),
                    "exercises": group[["exercise", "completed"]].values.tolist(),
                })

        # Filter by date
        if not show_all:
            cutoff = pd.Timestamp(today - timedelta(days=30))
            unified = [u for u in unified if u["date_parsed"] >= cutoff]

        # Search filter
        if search.strip():
            needle = search.strip().lower()
            def _match(u):
                if u["kind"] == "cardio":
                    return needle in u["type"].lower() or needle in u["notes"].lower()
                return needle in u["day"].lower()
            unified = [u for u in unified if _match(u)]

        if not unified:
            st.markdown('<div class="list-row" style="justify-content:center;opacity:0.7;">No matching sessions.</div>', unsafe_allow_html=True)
        else:
            unified.sort(key=lambda x: x["date_parsed"], reverse=True)

            with st.container(height=520):
                # Group by date string
                from itertools import groupby
                for day_str, items in groupby(unified, key=lambda x: x["date_str"]):
                    items = list(items)
                    label = items[0]["date_parsed"].strftime("%A, %d %B %Y")
                    count = len(items)
                    st.markdown(
                        f'<div style="font-family:var(--font-display);font-size:13px;'
                        f'text-transform:uppercase;letter-spacing:0.1em;color:var(--text2);'
                        f'margin:14px 0 8px;border-bottom:1px solid var(--border);'
                        f'padding-bottom:6px;">{label} '
                        f'<span style="color:var(--text3);font-size:11px;">'
                        f'({count} {"session" if count == 1 else "sessions"})</span></div>',
                        unsafe_allow_html=True,
                    )
                    for item in items:
                        if item["kind"] == "cardio":
                            pace_val = item["pace"] if item["pace"] else "—"
                            meta_html = (
                                f'<span style="color:var(--accent);font-weight:600;">{item["type"]}</span>'
                                f' · <span style="color:var(--text2);">{item["duration"]:.0f} min</span>'
                                f' · <span style="color:var(--text2);">{item["km"]:.2f} km</span>'
                                f' · <span style="color:var(--text2);">{pace_val}</span>'
                            )
                            body_html = ""
                            if item["notes"]:
                                body_html = (
                                    f'<div style="white-space:pre-wrap;font-size:14px;line-height:1.6;'
                                    f'color:var(--text);opacity:0.88;margin-top:6px;">{item["notes"]}</div>'
                                )
                            row_cols = st.columns([8, 2])
                            with row_cols[0]:
                                st.markdown(
                                    f'<div style="margin-bottom:4px;">{meta_html}</div>{body_html}'
                                    f'<div style="margin-bottom:14px;"></div>',
                                    unsafe_allow_html=True,
                                )
                            with row_cols[1]:
                                if st.button("Delete", key=f"del_cardio_{item['idx']}", use_container_width=True):
                                    save_exercise_df(exercise_df.drop(item["idx"]).reset_index(drop=True))
                                    st.rerun()
                        else:
                            pct = int(100 * item["done_count"] / item["total_count"]) if item["total_count"] else 0
                            meta_html = (
                                f'<span style="color:var(--accent);font-weight:600;">\U0001f4aa {item["day"]}</span>'
                                f' · <span style="color:var(--accent-2);font-weight:700;">{item["done_count"]}/{item["total_count"]} done</span>'
                                f' <span style="color:var(--text3);">({pct}%)</span>'
                            )
                            ex_lines = ""
                            for ex_name, completed in item["exercises"]:
                                done = str(completed).lower() in ["yes", "true", "1"]
                                tick = "✅" if done else "⬜"
                                color = "var(--text)" if done else "var(--text3)"
                                ex_lines += (
                                    f'<div style="font-size:13px;color:{color};margin:2px 0;">'
                                    f'{tick} {ex_name}</div>'
                                )
                            row_cols = st.columns([8, 2])
                            with row_cols[0]:
                                st.markdown(
                                    f'<div style="margin-bottom:6px;">{meta_html}</div>'
                                    f'<div style="padding-left:8px;margin-bottom:14px;">{ex_lines}</div>',
                                    unsafe_allow_html=True,
                                )
                            with row_cols[1]:
                                if st.button("Delete", key=f"del_str_{item['date_str']}_{item['day']}", use_container_width=True):
                                    keep = strength_log_df[
                                        ~(
                                            (strength_log_df["date"].astype(str) == item["date_str"])
                                            & (strength_log_df["day"].astype(str) == item["day"])
                                        )
                                    ]
                                    save_strength_log_df(keep.reset_index(drop=True))
                                    st.rerun()


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
