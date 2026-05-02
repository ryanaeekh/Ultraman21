import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="B.Mission", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header, metric_card, progress_bar
from utils import (
    load_bmission_goals, save_bmission_goals_df,
    load_bmission_milestones, save_bmission_milestones_df,
    clean_text,
)

inject_theme()
nav_menu("B.Mission")

# ── Constants ───────────────────────────────────────────────────────
DISCHARGE_DATE = date(2027, 10, 4)
START_DATE = date(2025, 1, 1)

FIXED_MILESTONES = [
    "Clear all outstanding debts",
    "Build $10,000 emergency fund",
    "Have profitable trading system",
    "First condo deposit saved",
    "Stable monthly income > $5,000",
]

STATUS_OPTIONS = ["Not Started", "In Progress", "Done"]

DAILY_REMINDERS = [
    "Every day you waste, the climb gets steeper. Move.",
    "Discharge isn't a finish line. It's a checkpoint. Build the plan now.",
    "Discomfort today buys freedom tomorrow. Pay it.",
    "You've already proven you can survive. Now prove you can win.",
    "No one is coming. You are the rescue plan.",
    "The version of you on Oct 4 2027 is being built right now, today.",
    "Excuses don't pay debts. Action does.",
    "Stop asking if it's possible. Start asking what it costs.",
    "Comfort is the slowest form of failure. Refuse it.",
    "The clock doesn't pause for your bad mood.",
    "Earn first. Rest after. In that order.",
    "A bad day worked is better than a good day wasted.",
    "Your future self is watching what you do at 9pm tonight.",
    "Quiet, consistent, daily — that's how comebacks are built.",
    "If it doesn't move you forward, why are you doing it?",
    "Discipline is remembering what you really want.",
    "The shortcut is showing up every single day.",
    "Pain you choose beats pain that chooses you.",
    "Don't be impressive. Be unrecoverable from.",
    "Today is one of the days that decides everything. Act like it.",
    "Cut the dead weight. Habits, people, thoughts — all of it.",
    "Hope is not a plan. Discipline is.",
    "Make the move that the broke version of you can't make.",
    "You don't need motivation. You need a deadline. You have one.",
    "Soft choices today, hard life forever. Pick.",
    "Your circumstances were dealt to you. Your response is yours.",
    "The work is the prayer. Get back to it.",
    "Stop negotiating with yourself. Execute.",
    "Money lost can be earned again. Time spent crying cannot.",
    "Build like the next 18 months are the only 18 months you get.",
]

MINDSET_QUOTES = [
    ("Fall down seven times, stand up eight.", "Japanese proverb"),
    ("Rock bottom became the solid foundation on which I rebuilt my life.", "J.K. Rowling"),
    ("It's not whether you get knocked down; it's whether you get up.", "Vince Lombardi"),
]

# ── Date math ───────────────────────────────────────────────────────
today = date.today()
days_remaining = (DISCHARGE_DATE - today).days
weeks_remaining = days_remaining / 7
months_remaining = days_remaining / 30.44

total_span = (DISCHARGE_DATE - START_DATE).days
elapsed = (today - START_DATE).days
pct_elapsed = max(0.0, min(100.0, (elapsed / total_span) * 100)) if total_span > 0 else 0.0

# ── Header ──────────────────────────────────────────────────────────
st.markdown(page_header("B.Mission", "Discharge: 4 October 2027"), unsafe_allow_html=True)

# ── Hero countdown ──────────────────────────────────────────────────
if days_remaining > 0:
    headline_value = f"{days_remaining:,}"
    headline_sub = f"days until 4 Oct 2027"
elif days_remaining == 0:
    headline_value = "TODAY"
    headline_sub = "discharge day"
else:
    headline_value = f"+{abs(days_remaining):,}"
    headline_sub = "days past discharge"

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
    st.markdown(metric_card("Weeks left", f"{weeks_remaining:,.1f}", color="var(--accent-2)"), unsafe_allow_html=True)
with cols[1]:
    st.markdown(metric_card("Months left", f"{months_remaining:,.1f}", color="var(--accent-2)"), unsafe_allow_html=True)
with cols[2]:
    st.markdown(metric_card("Time elapsed", f"{pct_elapsed:.1f}%", sub=f"since {START_DATE.strftime('%b %Y')}", color="var(--accent-2)"), unsafe_allow_html=True)

st.markdown(
    f'<div style="margin:18px 0 4px;">{progress_bar(pct_elapsed)}</div>'
    f'<div style="text-align:right;font-size:12px;color:var(--text3);">'
    f'{elapsed:,} of {total_span:,} days</div>',
    unsafe_allow_html=True,
)

# ── Daily reminder ──────────────────────────────────────────────────
reminder = DAILY_REMINDERS[today.toordinal() % len(DAILY_REMINDERS)]
st.markdown(
    f'<div class="card" style="margin-top:24px;border-left:4px solid var(--neg);'
    f'padding:18px 22px;">'
    f'<div class="section-title" style="color:var(--neg);">\U0001f6a8 Today&#39;s Reminder</div>'
    f'<div style="font-size:18px;font-weight:600;line-height:1.5;color:var(--text);">'
    f'{reminder}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Mission targets ─────────────────────────────────────────────────
st.markdown('<div class="section-title" style="margin-top:32px;">\U0001f3af Mission Targets</div>', unsafe_allow_html=True)

goals_df = load_bmission_goals()

with st.expander("➕ Add new target"):
    with st.form("add_goal_form", clear_on_submit=True):
        g_cols = st.columns([3, 2, 2])
        new_goal = g_cols[0].text_input("Goal", placeholder="e.g. Pay off CC debt")
        new_target = g_cols[1].date_input("Target date", value=today + timedelta(days=30))
        new_status = g_cols[2].selectbox("Status", STATUS_OPTIONS, index=0)
        new_notes = st.text_input("Notes", placeholder="Optional context")
        if st.form_submit_button("Add target", use_container_width=True):
            if new_goal.strip():
                row = pd.DataFrame([{
                    "goal": new_goal.strip(),
                    "target_date": str(new_target),
                    "status": new_status,
                    "notes": new_notes.strip(),
                }])
                save_bmission_goals_df(pd.concat([goals_df, row], ignore_index=True))
                st.rerun()
            else:
                st.warning("Goal name is required.")

if goals_df.empty:
    st.markdown('<div class="list-row" style="justify-content:center;opacity:0.7;">No targets yet. Add one above.</div>', unsafe_allow_html=True)
else:
    for idx, r in goals_df.iterrows():
        goal = clean_text(r.get("goal", ""))
        tgt_str = clean_text(r.get("target_date", ""))
        status = clean_text(r.get("status", "")) or "Not Started"
        notes = clean_text(r.get("notes", ""))

        tgt_parsed = pd.to_datetime(tgt_str, errors="coerce")
        days_left = (tgt_parsed.date() - today).days if pd.notna(tgt_parsed) else None

        status_color = {
            "Done": "var(--pos)",
            "In Progress": "var(--accent-2)",
            "Not Started": "var(--text3)",
        }.get(status, "var(--text3)")

        days_label = ""
        if days_left is not None:
            if days_left < 0:
                days_label = f'<span style="color:var(--neg);">{abs(days_left)}d overdue</span>'
            elif days_left == 0:
                days_label = f'<span style="color:var(--neg);">due today</span>'
            else:
                days_label = f'<span style="color:var(--text2);">{days_left}d left</span>'

        with st.container(border=True):
            row_cols = st.columns([5, 2, 2, 1.2, 1])
            with row_cols[0]:
                st.markdown(
                    f'<div style="font-weight:600;font-size:16px;">{goal}</div>'
                    + (f'<div style="font-size:13px;color:var(--text2);margin-top:2px;">{notes}</div>' if notes else ""),
                    unsafe_allow_html=True,
                )
            with row_cols[1]:
                new_status_pick = st.selectbox(
                    "Status", STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(status) if status in STATUS_OPTIONS else 0,
                    key=f"goal_status_{idx}",
                    label_visibility="collapsed",
                )
                if new_status_pick != status:
                    goals_df.at[idx, "status"] = new_status_pick
                    save_bmission_goals_df(goals_df)
                    st.rerun()
            with row_cols[2]:
                st.markdown(
                    f'<div style="font-size:13px;color:var(--text2);">{tgt_str or "—"}</div>'
                    f'<div style="font-size:12px;margin-top:2px;">{days_label}</div>',
                    unsafe_allow_html=True,
                )
            with row_cols[3]:
                st.markdown(
                    f'<span class="badge" style="color:{status_color};background:{status_color}15;">{status}</span>',
                    unsafe_allow_html=True,
                )
            with row_cols[4]:
                if st.button("\U0001f5d1️", key=f"goal_del_{idx}", use_container_width=True):
                    save_bmission_goals_df(goals_df.drop(idx).reset_index(drop=True))
                    st.rerun()

# ── Financial milestones ────────────────────────────────────────────
st.markdown('<div class="section-title" style="margin-top:32px;">\U0001f4b0 Financial Milestones</div>', unsafe_allow_html=True)

milestones_df = load_bmission_milestones()


def _is_done(value) -> bool:
    return str(value).strip().lower() in ("true", "1", "yes", "done")


existing_names = set(clean_text(m) for m in milestones_df.get("milestone", pd.Series([], dtype=object)))
missing_fixed = [m for m in FIXED_MILESTONES if m not in existing_names]
if missing_fixed:
    seed = pd.DataFrame([{"milestone": m, "done": "False"} for m in missing_fixed])
    milestones_df = pd.concat([milestones_df, seed], ignore_index=True)
    save_bmission_milestones_df(milestones_df)
    milestones_df = load_bmission_milestones()

ordered_rows = []
for fm in FIXED_MILESTONES:
    match = milestones_df[milestones_df["milestone"].astype(str) == fm]
    if not match.empty:
        ordered_rows.append((match.index[0], match.iloc[0], True))
for idx, r in milestones_df.iterrows():
    name = clean_text(r.get("milestone", ""))
    if name and name not in FIXED_MILESTONES:
        ordered_rows.append((idx, r, False))

done_count = sum(1 for _, r, _ in ordered_rows if _is_done(r.get("done", "")))
total_count = len(ordered_rows)
st.markdown(
    f'<div style="font-size:13px;color:var(--text2);margin-bottom:10px;">'
    f'{done_count} of {total_count} complete</div>',
    unsafe_allow_html=True,
)

for idx, r, is_fixed in ordered_rows:
    name = clean_text(r.get("milestone", ""))
    done = _is_done(r.get("done", ""))
    m_cols = st.columns([0.6, 8, 1])
    with m_cols[0]:
        new_done = st.checkbox("done", value=done, key=f"ms_chk_{idx}", label_visibility="collapsed")
    with m_cols[1]:
        decoration = "line-through" if new_done else "none"
        opacity = "0.55" if new_done else "1"
        tag = ' <span class="badge" style="color:var(--text3);background:var(--accent-soft);font-size:10px;">custom</span>' if not is_fixed else ""
        st.markdown(
            f'<div style="font-size:15px;text-decoration:{decoration};opacity:{opacity};'
            f'padding-top:4px;">{name}{tag}</div>',
            unsafe_allow_html=True,
        )
    with m_cols[2]:
        if not is_fixed:
            if st.button("\U0001f5d1️", key=f"ms_del_{idx}", use_container_width=True):
                save_bmission_milestones_df(milestones_df.drop(idx).reset_index(drop=True))
                st.rerun()

    if new_done != done:
        milestones_df.at[idx, "done"] = "True" if new_done else "False"
        save_bmission_milestones_df(milestones_df)
        st.rerun()

with st.expander("➕ Add custom milestone"):
    with st.form("add_milestone_form", clear_on_submit=True):
        new_ms = st.text_input("Milestone", placeholder="e.g. Open SRS account")
        if st.form_submit_button("Add milestone", use_container_width=True):
            if new_ms.strip():
                row = pd.DataFrame([{"milestone": new_ms.strip(), "done": "False"}])
                save_bmission_milestones_df(pd.concat([milestones_df, row], ignore_index=True))
                st.rerun()
            else:
                st.warning("Milestone name is required.")

# ── Time allocation ─────────────────────────────────────────────────
st.markdown('<div class="section-title" style="margin-top:32px;">⏱️ Time Allocation</div>', unsafe_allow_html=True)

if days_remaining > 0:
    working_days = int(round(days_remaining * 6 / 7))
    rest_days = days_remaining - working_days
else:
    working_days = 0
    rest_days = 0

t_cols = st.columns(3)
with t_cols[0]:
    st.markdown(metric_card("Total days left", f"{max(days_remaining, 0):,}", color="var(--text)"), unsafe_allow_html=True)
with t_cols[1]:
    st.markdown(metric_card("Working days", f"{working_days:,}", sub="6 days/week", color="var(--accent-2)"), unsafe_allow_html=True)
with t_cols[2]:
    st.markdown(metric_card("Rest days", f"{rest_days:,}", sub="1 day/week", color="var(--text2)"), unsafe_allow_html=True)

daily_target = st.number_input(
    "Daily income target ($)",
    min_value=0.0, value=200.0, step=10.0,
    key="bm_daily_target",
)
potential = daily_target * working_days
st.markdown(
    f'<div class="card" style="margin-top:14px;text-align:center;padding:24px;">'
    f'<div style="font-size:14px;color:var(--text2);text-transform:uppercase;letter-spacing:0.16em;">'
    f'If you earn <span style="color:var(--accent-2);font-weight:700;">${daily_target:,.0f}</span> per working day</div>'
    f'<div style="font-size:48px;font-weight:800;line-height:1;margin:12px 0;'
    f'background:var(--gradient-hero);-webkit-background-clip:text;'
    f'-webkit-text-fill-color:transparent;background-clip:text;">'
    f'${potential:,.0f}</div>'
    f'<div style="font-size:13px;color:var(--text3);">'
    f'total earnings possible before discharge ({working_days:,} working days)</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Mindset section ─────────────────────────────────────────────────
st.markdown('<div class="section-title" style="margin-top:32px;">\U0001f9e0 Mindset</div>', unsafe_allow_html=True)

for quote, author in MINDSET_QUOTES:
    st.markdown(
        f'<div class="card" style="margin-bottom:14px;padding:22px 26px;'
        f'border-left:3px solid var(--accent);">'
        f'<div style="font-size:20px;font-style:italic;line-height:1.5;color:var(--text);">'
        f'“{quote}”</div>'
        f'<div style="margin-top:10px;font-size:13px;color:var(--text2);'
        f'text-transform:uppercase;letter-spacing:0.14em;">— {author}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
