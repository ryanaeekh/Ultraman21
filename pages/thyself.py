import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Thyself", page_icon="\U0001f9d8", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header
from utils import (
    load_thyself_checkin, save_thyself_checkin_df,
    load_thyself_patterns, save_thyself_patterns_df,
    load_thyself_gratitude, save_thyself_gratitude_df,
    load_thyself_mood, save_thyself_mood_df,
    load_thyself_weekly, save_thyself_weekly_df,
    clean_text,
)

inject_theme()
nav_menu("Thyself")

today = date.today()
today_str = str(today)

# ── Header ────────────────────────────────────────────────
st.markdown(page_header("Know Thyself", "The examined life"), unsafe_allow_html=True)
st.markdown(
    '<div style="margin:-12px 0 28px;font-size:12px;color:var(--text3);">'
    'Resource: <a href="https://thewisdomoftrauma.com/" target="_blank" '
    'style="color:var(--text2);text-decoration:none;border-bottom:1px dotted var(--text3);">'
    'The Wisdom of Trauma</a></div>',
    unsafe_allow_html=True,
)

# ── Load all data once ────────────────────────────────────
checkin_df = load_thyself_checkin()
patterns_df = load_thyself_patterns()
gratitude_df = load_thyself_gratitude()
mood_df = load_thyself_mood()
weekly_df = load_thyself_weekly()


# =========================================================
# SECTION 1 — DAILY CHECK-IN
# =========================================================
def calc_streak(df: pd.DataFrame) -> int:
    if df.empty or "date" not in df.columns:
        return 0
    parsed = pd.to_datetime(df["date"], errors="coerce").dropna().dt.date
    if parsed.empty:
        return 0
    days = set(parsed)
    if today in days:
        cursor = today
    elif (today - timedelta(days=1)) in days:
        cursor = today - timedelta(days=1)
    else:
        return 0
    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


streak = calc_streak(checkin_df)
streak_html = (
    f'<div style="display:inline-block;font-size:13px;font-weight:600;'
    f'font-family:var(--font-display);padding:6px 16px;border-radius:20px;'
    f'color:var(--accent);background:var(--accent-soft);'
    f'border:1px solid var(--border);margin-bottom:16px;">'
    f'{streak} consecutive {"day" if streak == 1 else "days"} logged</div>'
) if streak > 0 else (
    '<div style="display:inline-block;font-size:13px;color:var(--text3);'
    'padding:6px 16px;border:1px solid var(--border);border-radius:20px;'
    'margin-bottom:16px;">No active streak.</div>'
)
st.markdown(streak_html, unsafe_allow_html=True)

st.markdown('<div class="section-title">Daily Check-in</div>', unsafe_allow_html=True)

today_checkin = checkin_df[checkin_df["date"].astype(str) == today_str]
existing_body = clean_text(today_checkin.iloc[0]["body_feeling"]) if not today_checkin.empty else ""
existing_fear = clean_text(today_checkin.iloc[0]["fear_driven"]) if not today_checkin.empty else ""
existing_needs = clean_text(today_checkin.iloc[0]["needs"]) if not today_checkin.empty else ""
try:
    existing_tension = int(float(today_checkin.iloc[0]["tension_score"])) if not today_checkin.empty else 5
except (ValueError, TypeError):
    existing_tension = 5

body_feeling = st.text_area(
    "How am I feeling right now, in my body?",
    value=existing_body,
    key="thy_body",
    height=100,
)
fear_driven = st.text_area(
    "Am I putting others first out of fear today?",
    value=existing_fear,
    key="thy_fear",
    height=100,
)
needs = st.text_area(
    "What do I need today?",
    value=existing_needs,
    key="thy_needs",
    height=100,
)
tension_score = st.slider(
    "Body tension (morning) — 1 very relaxed, 10 very tense",
    min_value=1, max_value=10,
    value=max(1, min(10, existing_tension)),
    key="thy_tension",
)

if st.button("Save check-in", use_container_width=True, key="save_checkin"):
    new_row = pd.DataFrame([{
        "date": today_str,
        "body_feeling": body_feeling.strip(),
        "fear_driven": fear_driven.strip(),
        "needs": needs.strip(),
        "tension_score": int(tension_score),
    }])
    others = checkin_df[checkin_df["date"].astype(str) != today_str]
    updated = pd.concat([others, new_row], ignore_index=True)
    with st.spinner("Saving..."):
        save_thyself_checkin_df(updated)
    st.success("Check-in saved.")
    st.rerun()


# =========================================================
# SECTION 2 — DAILY REMINDER
# =========================================================
QUOTES = [
    "Trauma is not what happens to you. It is what happens inside you as a result of what happens to you. — Gabor Maté",
    "The attempt to escape from pain creates more pain. — Gabor Maté",
    "Authenticity is not a luxury. It is a survival imperative. — Gabor Maté",
    "Safety is not the absence of threat. It is the presence of connection. — Gabor Maté",
    "When the body says no, the cost is often paid in disease. — Gabor Maté",
    "Healing begins when we stop abandoning ourselves. — Gabor Maté",
    "The greatest damage done by neglect, trauma or emotional loss is not the immediate pain they inflict but the long-term distortions they induce. — Gabor Maté",
    "Recovery is the slow practice of choosing yourself, again and again. — Pete Walker",
    "You are not a problem to be solved. You are a person to be witnessed. — Pete Walker",
    "Self-compassion is the antidote to the inner critic. — Pete Walker",
    "Grieving is the work that lets the past become the past. — Pete Walker",
    "The fawn response is the survival strategy of pleasing others to stay safe. — Pete Walker",
    "Healing is non-linear. Setbacks are part of the path. — Pete Walker",
    "Re-parenting yourself is the quiet, daily work of becoming whole. — Pete Walker",
    "Three things cannot be long hidden: the sun, the moon, and the truth. — Buddha",
    "You yourself, as much as anybody in the entire universe, deserve your love and affection. — Buddha",
    "What you think, you become. What you feel, you attract. What you imagine, you create. — Buddha",
    "Pain is inevitable. Suffering is optional. — Buddha",
    "Peace comes from within. Do not seek it without. — Buddha",
    "The mind is everything. What you think, you become. — Buddha",
]

quote_today = QUOTES[today.toordinal() % len(QUOTES)]

st.markdown(
    f'<div style="margin:32px 0 28px;padding:24px 20px;'
    f'border-top:1px solid var(--border);border-bottom:1px solid var(--border);'
    f'text-align:center;font-style:italic;font-size:16px;line-height:1.7;'
    f'color:var(--text);font-family:var(--font-display);opacity:0.92;">'
    f'{quote_today}</div>',
    unsafe_allow_html=True,
)


# =========================================================
# SECTION 3 — PATTERN TRACKER
# =========================================================
st.markdown('<div class="section-title">Pattern Tracker</div>', unsafe_allow_html=True)

PATTERN_OPTIONS = [
    "People pleasing",
    "Suppressing emotion",
    "Overworking",
    "Isolating",
    "Seeking approval",
    "Other",
]

pattern_type = st.selectbox(
    "Pattern noticed",
    PATTERN_OPTIONS,
    key="thy_pattern_type",
)
pattern_notes = st.text_area(
    "Describe what happened — just observe, don't judge",
    value="",
    key="thy_pattern_notes",
    height=140,
)
trigger = st.text_input(
    "What happened just before the feeling shifted? (optional)",
    value="",
    key="thy_trigger",
)

st.markdown(
    '<div style="margin:12px 0 18px;padding:12px 16px;'
    'font-style:italic;color:var(--text2);font-size:14px;'
    'border-left:3px solid var(--accent);background:var(--accent-soft);'
    'border-radius:6px;">'
    'What would you say to a friend who did the same thing?</div>',
    unsafe_allow_html=True,
)

if st.button("Save pattern entry", use_container_width=True, key="save_pattern"):
    if pattern_notes.strip():
        new_row = pd.DataFrame([{
            "date": today_str,
            "pattern_type": pattern_type,
            "pattern_notes": pattern_notes.strip(),
            "trigger": trigger.strip(),
        }])
        updated = pd.concat([patterns_df, new_row], ignore_index=True)
        with st.spinner("Saving..."):
            save_thyself_patterns_df(updated)
        st.success("Pattern logged.")
        st.rerun()
    else:
        st.warning("Add a note before saving.")


# =========================================================
# SECTION 4 — GRATITUDE (SELF-AWARENESS)
# =========================================================
st.markdown('<div class="section-title">Self-awareness</div>', unsafe_allow_html=True)

today_gratitude = gratitude_df[gratitude_df["date"].astype(str) == today_str]
existing_gratitude = clean_text(today_gratitude.iloc[0]["gratitude_note"]) if not today_gratitude.empty else ""

gratitude_note = st.text_area(
    "One moment today where you stayed with yourself instead of abandoning yourself.",
    value=existing_gratitude,
    key="thy_gratitude",
    height=120,
)

if st.button("Save", use_container_width=True, key="save_gratitude"):
    if gratitude_note.strip():
        new_row = pd.DataFrame([{
            "date": today_str,
            "gratitude_note": gratitude_note.strip(),
        }])
        others = gratitude_df[gratitude_df["date"].astype(str) != today_str]
        updated = pd.concat([others, new_row], ignore_index=True)
        with st.spinner("Saving..."):
            save_thyself_gratitude_df(updated)
        st.success("Saved.")
        st.rerun()
    else:
        st.warning("Write something before saving.")


# =========================================================
# SECTION 5 — MOOD & BODY CHECK
# =========================================================
st.markdown('<div class="section-title">Mood & Body</div>', unsafe_allow_html=True)

today_mood = mood_df[mood_df["date"].astype(str) == today_str]
existing_morning_word = clean_text(today_mood.iloc[0]["morning_word"]) if not today_mood.empty else ""
existing_evening_word = clean_text(today_mood.iloc[0]["evening_word"]) if not today_mood.empty else ""
try:
    existing_morning_tension = int(float(today_mood.iloc[0]["morning_tension"])) if not today_mood.empty else 5
except (ValueError, TypeError):
    existing_morning_tension = 5
try:
    existing_evening_tension = int(float(today_mood.iloc[0]["evening_tension"])) if not today_mood.empty else 5
except (ValueError, TypeError):
    existing_evening_tension = 5

mood_cols = st.columns(2)
with mood_cols[0]:
    st.markdown(
        '<div style="font-family:var(--font-display);font-size:12px;'
        'text-transform:uppercase;letter-spacing:0.12em;color:var(--text2);'
        'margin-bottom:8px;">Morning</div>',
        unsafe_allow_html=True,
    )
    morning_word = st.text_input(
        "One word",
        value=existing_morning_word,
        key="thy_morning_word",
        max_chars=40,
    )
    morning_tension = st.slider(
        "Tension",
        min_value=1, max_value=10,
        value=max(1, min(10, existing_morning_tension)),
        key="thy_morning_tension",
    )

with mood_cols[1]:
    st.markdown(
        '<div style="font-family:var(--font-display);font-size:12px;'
        'text-transform:uppercase;letter-spacing:0.12em;color:var(--text2);'
        'margin-bottom:8px;">Evening</div>',
        unsafe_allow_html=True,
    )
    evening_word = st.text_input(
        "One word",
        value=existing_evening_word,
        key="thy_evening_word",
        max_chars=40,
    )
    evening_tension = st.slider(
        "Tension",
        min_value=1, max_value=10,
        value=max(1, min(10, existing_evening_tension)),
        key="thy_evening_tension",
    )

if st.button("Save mood & body", use_container_width=True, key="save_mood"):
    new_row = pd.DataFrame([{
        "date": today_str,
        "morning_word": morning_word.strip(),
        "morning_tension": int(morning_tension),
        "evening_word": evening_word.strip(),
        "evening_tension": int(evening_tension),
    }])
    others = mood_df[mood_df["date"].astype(str) != today_str]
    updated = pd.concat([others, new_row], ignore_index=True)
    with st.spinner("Saving..."):
        save_thyself_mood_df(updated)
    st.success("Saved.")
    st.rerun()

# Last 7 days table
if not mood_df.empty:
    recent = mood_df.copy()
    recent["date_parsed"] = pd.to_datetime(recent["date"], errors="coerce")
    recent = recent.dropna(subset=["date_parsed"]).sort_values("date_parsed", ascending=False)
    cutoff = pd.Timestamp(today - timedelta(days=6))
    recent = recent[recent["date_parsed"] >= cutoff]

    if not recent.empty:
        st.markdown(
            '<div style="font-family:var(--font-display);font-size:11px;'
            'text-transform:uppercase;letter-spacing:0.12em;color:var(--text2);'
            'margin:24px 0 8px;">Last 7 days</div>',
            unsafe_allow_html=True,
        )
        display = recent[["date", "morning_word", "morning_tension", "evening_word", "evening_tension"]].copy()
        display.columns = ["Date", "Morning word", "Morning tension", "Evening word", "Evening tension"]
        st.dataframe(display, use_container_width=True, hide_index=True)

        # 7-day tension trend
        chart_df = recent.sort_values("date_parsed").set_index("date_parsed")[
            ["morning_tension", "evening_tension"]
        ]
        chart_df.columns = ["Morning", "Evening"]
        st.markdown(
            '<div style="font-family:var(--font-display);font-size:11px;'
            'text-transform:uppercase;letter-spacing:0.12em;color:var(--text2);'
            'margin:18px 0 8px;">7-day tension trend</div>',
            unsafe_allow_html=True,
        )
        st.line_chart(chart_df)


# =========================================================
# SECTION 6 — WEEKLY REFLECTION
# =========================================================
st.markdown('<div class="section-title">Weekly Reflection</div>', unsafe_allow_html=True)
st.caption("Best done on Sundays.")

fear_driven_week = st.text_area(
    "Where did I put others first from fear this week?",
    value="",
    key="thy_week_fear",
    height=120,
)
chose_self = st.text_area(
    "Where did I choose myself this week?",
    value="",
    key="thy_week_self",
    height=120,
)
body_listened = st.text_area(
    "What did my body tell me that I actually listened to?",
    value="",
    key="thy_week_body",
    height=120,
)

if st.button("Save weekly reflection", use_container_width=True, key="save_weekly"):
    if any(t.strip() for t in (fear_driven_week, chose_self, body_listened)):
        new_row = pd.DataFrame([{
            "date": today_str,
            "fear_driven_week": fear_driven_week.strip(),
            "chose_self": chose_self.strip(),
            "body_listened": body_listened.strip(),
        }])
        updated = pd.concat([weekly_df, new_row], ignore_index=True)
        with st.spinner("Saving..."):
            save_thyself_weekly_df(updated)
        st.success("Reflection saved.")
        st.rerun()
    else:
        st.warning("Write something in at least one field before saving.")


# ── Footer note ───────────────────────────────────────────
st.markdown(
    '<div style="margin-top:36px;padding-top:18px;border-top:1px solid var(--border);'
    'font-size:11px;color:var(--text3);text-align:center;">'
    'Your data is stored in Google Sheets. Keep your sheet private.</div>',
    unsafe_allow_html=True,
)
