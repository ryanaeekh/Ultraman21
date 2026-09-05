import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Countdown", page_icon="⏳", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header, metric_card, progress_bar
from utils import load_countdown_log, save_countdown_log_df

inject_theme()
nav_menu("Countdown")

# ── Constants ───────────────────────────────────────────────────────
START_DATE = date(2026, 9, 17)
END_DATE = date(2028, 9, 17)
TOTAL_DAYS = 730

today = date.today()

st.markdown(page_header("Countdown", "730 days. No excuses."), unsafe_allow_html=True)

# ============================================================
# HERO COUNTDOWN
# ============================================================
days_remaining = (END_DATE - today).days
days_completed = (today - START_DATE).days
elapsed_clamped = max(0, min(TOTAL_DAYS, days_completed))
pct_elapsed = (elapsed_clamped / TOTAL_DAYS) * 100 if TOTAL_DAYS > 0 else 0.0
day_number = min(elapsed_clamped + 1, TOTAL_DAYS) if today >= START_DATE else 0

if today < START_DATE:
    headline_value = f"{(START_DATE - today).days:,}"
    headline_sub = "days until the challenge starts"
elif days_remaining > 0:
    headline_value = f"{days_remaining:,}"
    headline_sub = f"days until {END_DATE.strftime('%d %b %Y')}"
elif days_remaining == 0:
    headline_value = "TODAY"
    headline_sub = "final day"
else:
    headline_value = f"+{abs(days_remaining):,}"
    headline_sub = "days past the finish line"

st.markdown(
    f'<div class="card" style="margin-top:20px;text-align:center;padding:36px 24px;">'
    f'<div class="section-title">⏳ Countdown</div>'
    f'<div style="font-size:84px;font-weight:800;line-height:1;letter-spacing:-0.04em;'
    f'background:var(--gradient-hero);-webkit-background-clip:text;'
    f'-webkit-text-fill-color:transparent;background-clip:text;margin:8px 0;">'
    f'{headline_value}</div>'
    f'<div style="font-size:15px;color:var(--text2);text-transform:uppercase;'
    f'letter-spacing:0.18em;">{headline_sub}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

cols = st.columns(3)
with cols[0]:
    st.markdown(metric_card("Days Completed", f"{elapsed_clamped:,}", color="var(--accent-2)"), unsafe_allow_html=True)
with cols[1]:
    st.markdown(metric_card("Days Remaining", f"{max(days_remaining, 0):,}", color="var(--accent-2)"), unsafe_allow_html=True)
with cols[2]:
    st.markdown(metric_card("Progress", f"{pct_elapsed:.1f}%", color="var(--accent-2)"), unsafe_allow_html=True)

st.markdown(
    f'<div style="margin:18px 0 4px;">{progress_bar(pct_elapsed)}</div>'
    f'<div style="text-align:right;font-size:12px;color:var(--text3);">'
    f'Day {day_number} of {TOTAL_DAYS}</div>',
    unsafe_allow_html=True,
)

# ============================================================
# DAILY CHECKLIST
# ============================================================
st.markdown('<div class="section-title" style="margin-top:32px;">✅ Daily Checklist</div>', unsafe_allow_html=True)

countdown_df = load_countdown_log()
today_str = str(today)
today_row = countdown_df[countdown_df["date"] == today_str]
saved_earning = bool(today_row.iloc[0]["earning_done"]) if not today_row.empty else False
saved_exercise = bool(today_row.iloc[0]["exercise_done"]) if not today_row.empty else False

earning_done = st.checkbox("$250 Daily Earning (target: $6,500/month)", value=saved_earning, key="cd_earning_done")
exercise_done = st.checkbox("Exercise", value=saved_exercise, key="cd_exercise_done")

if st.button("Save Today", use_container_width=True, key="cd_save"):
    remaining_df = countdown_df[countdown_df["date"] != today_str]
    new_row = pd.DataFrame([{"date": today_str, "earning_done": earning_done, "exercise_done": exercise_done}])
    save_countdown_log_df(pd.concat([remaining_df, new_row], ignore_index=True))
    st.success("Saved.")
    st.rerun()

completed_today = int(saved_earning) + int(saved_exercise)
st.markdown(
    f'<div style="text-align:center;font-size:14px;color:var(--text2);margin-top:6px;">'
    f'{completed_today}/2 completed today</div>',
    unsafe_allow_html=True,
)

# ============================================================
# STREAK TRACKER
# ============================================================
st.markdown('<div class="section-title" style="margin-top:32px;">\U0001f525 Streak Tracker</div>', unsafe_allow_html=True)


def _perfect_days(df: pd.DataFrame) -> set:
    if df.empty:
        return set()
    parsed = pd.to_datetime(df["date"], errors="coerce")
    mask = df["earning_done"].astype(bool) & df["exercise_done"].astype(bool)
    return set(parsed[mask].dropna().dt.date)


def _current_streak(perfect_days: set, ref_day: date) -> int:
    if ref_day in perfect_days:
        cursor = ref_day
    elif (ref_day - timedelta(days=1)) in perfect_days:
        cursor = ref_day - timedelta(days=1)
    else:
        return 0
    streak = 0
    while cursor in perfect_days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def _best_streak(perfect_days: set) -> int:
    best = 0
    for d in perfect_days:
        if (d - timedelta(days=1)) not in perfect_days:
            run = 0
            cursor = d
            while cursor in perfect_days:
                run += 1
                cursor += timedelta(days=1)
            best = max(best, run)
    return best


perfect_days = _perfect_days(countdown_df)
current_streak = _current_streak(perfect_days, today)
best_streak = _best_streak(perfect_days)
total_perfect = len(perfect_days)

streak_cols = st.columns(3)
with streak_cols[0]:
    st.markdown(metric_card("Current Streak", f"{current_streak}", sub="days", color="var(--accent-2)"), unsafe_allow_html=True)
with streak_cols[1]:
    st.markdown(metric_card("Best Streak", f"{best_streak}", sub="days", color="var(--accent-2)"), unsafe_allow_html=True)
with streak_cols[2]:
    st.markdown(metric_card("Perfect Days", f"{total_perfect}", sub=f"of {day_number} elapsed", color="var(--accent-2)"), unsafe_allow_html=True)

# ============================================================
# PAST LOG
# ============================================================
st.markdown('<div class="section-title" style="margin-top:32px;">\U0001f4dc Past Log</div>', unsafe_allow_html=True)

show_all = st.checkbox("Show all", value=False, key="cd_show_all")
st.caption("Last 30 days by default" if not show_all else "Showing all entries")

log_df = countdown_df.copy()
log_df["date_parsed"] = pd.to_datetime(log_df["date"], errors="coerce")
log_df = log_df.dropna(subset=["date_parsed"]).sort_values("date_parsed", ascending=False)

if not show_all:
    cutoff = pd.Timestamp(today - timedelta(days=30))
    log_df = log_df[log_df["date_parsed"] >= cutoff]

if log_df.empty:
    st.markdown('<div class="list-row" style="justify-content:center;opacity:0.7;">No entries yet.</div>', unsafe_allow_html=True)
else:
    header_cols = st.columns([3, 3, 3, 1.2])
    for c, label in zip(header_cols, ["Date", "Earning Done", "Exercise Done", ""]):
        c.markdown(
            f'<div style="font-family:var(--font-display);font-size:11px;'
            f'text-transform:uppercase;letter-spacing:0.1em;color:var(--text2);">{label}</div>',
            unsafe_allow_html=True,
        )
    with st.container(height=420):
        for idx, r in log_df.iterrows():
            row_cols = st.columns([3, 3, 3, 1.2])
            with row_cols[0]:
                st.markdown(f'<div class="list-row">{r["date_parsed"].strftime("%d %b %Y")}</div>', unsafe_allow_html=True)
            with row_cols[1]:
                mark = "✅" if r["earning_done"] else "❌"
                st.markdown(f'<div class="list-row" style="justify-content:center;">{mark}</div>', unsafe_allow_html=True)
            with row_cols[2]:
                mark = "✅" if r["exercise_done"] else "❌"
                st.markdown(f'<div class="list-row" style="justify-content:center;">{mark}</div>', unsafe_allow_html=True)
            with row_cols[3]:
                if st.button("\U0001f5d1️", key=f"cd_del_{idx}", use_container_width=True):
                    save_countdown_log_df(countdown_df.drop(idx).reset_index(drop=True))
                    st.rerun()
