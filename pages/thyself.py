import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Thyself", page_icon="\U0001f9d8", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header
from utils import (
    load_thyself_checkin, save_thyself_checkin_df,
    load_thyself_patterns, save_thyself_patterns_df,
    load_thyself_gratitude, save_thyself_gratitude_df,
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

# ── Daily Reminder (rotating quote) ───────────────────────
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
    f'<div style="margin:0 0 28px;padding:24px 20px;'
    f'border-top:1px solid var(--border);border-bottom:1px solid var(--border);'
    f'text-align:center;font-style:italic;font-size:16px;line-height:1.7;'
    f'color:var(--text);font-family:var(--font-display);opacity:0.92;">'
    f'{quote_today}</div>',
    unsafe_allow_html=True,
)

# ── Load all data once ────────────────────────────────────
checkin_df = load_thyself_checkin()
patterns_df = load_thyself_patterns()
gratitude_df = load_thyself_gratitude()
weekly_df = load_thyself_weekly()


# =========================================================
# SECTION 1 — DAILY CHECK-IN
# =========================================================
st.markdown('<div class="section-title">Daily Check-in</div>', unsafe_allow_html=True)

BODY_OPTIONS = ["Calm", "Anxious", "Heavy", "Light", "Tense", "Numb", "Tired", "Alive", "Okay", "Overwhelmed"]

today_checkin = checkin_df[checkin_df["date"].astype(str) == today_str]
existing_body = clean_text(today_checkin.iloc[0]["body_feeling"]) if not today_checkin.empty else ""
body_index = BODY_OPTIONS.index(existing_body) if existing_body in BODY_OPTIONS else 0

body_feeling = st.selectbox(
    "How am I feeling right now, in my body?",
    BODY_OPTIONS,
    index=body_index,
    key="thy_body",
)

if st.button("Save check-in", use_container_width=True, key="save_checkin"):
    new_row = pd.DataFrame([{
        "date": today_str,
        "body_feeling": body_feeling,
    }])
    others = checkin_df[checkin_df["date"].astype(str) != today_str]
    updated = pd.concat([others, new_row], ignore_index=True)
    with st.spinner("Saving..."):
        save_thyself_checkin_df(updated)
    st.success("Check-in saved.")
    st.rerun()

# Past Check-ins (all entries)
with st.expander("Past Check-ins", expanded=False):
    if checkin_df.empty:
        st.markdown(
            '<div class="list-row" style="justify-content:center;opacity:0.7;">'
            'No check-ins yet.</div>',
            unsafe_allow_html=True,
        )
    else:
        ci_view = checkin_df.copy()
        ci_view["_date_parsed"] = pd.to_datetime(ci_view["date"], errors="coerce")
        ci_view = ci_view.dropna(subset=["_date_parsed"]).sort_values("_date_parsed", ascending=False)

        if ci_view.empty:
            st.markdown(
                '<div class="list-row" style="justify-content:center;opacity:0.7;">'
                'No check-ins yet.</div>',
                unsafe_allow_html=True,
            )
        else:
            display = ci_view[["date", "body_feeling"]].copy()
            display.columns = ["Date", "Body Feeling"]
            st.dataframe(display, use_container_width=True, hide_index=True)


# =========================================================
# SECTION 2 — SELF-AWARENESS
# =========================================================
st.markdown('<div class="section-title">Self-awareness</div>', unsafe_allow_html=True)

today_gratitude = gratitude_df[gratitude_df["date"].astype(str) == today_str]
existing_gratitude = clean_text(today_gratitude.iloc[0]["gratitude_note"]) if not today_gratitude.empty else ""

gratitude_index = 1 if existing_gratitude == "No" else 0  # default Yes

gratitude_choice = st.radio(
    "Did I stay with myself today instead of abandoning myself?",
    ["Yes", "No"],
    index=gratitude_index,
    horizontal=True,
    key="thy_gratitude",
)

# Counts from all gratitude entries
gratitude_series = (
    gratitude_df["gratitude_note"].astype(str).str.strip()
    if not gratitude_df.empty else pd.Series(dtype=str)
)
stayed_count = int((gratitude_series == "Yes").sum())
abandoned_count = int((gratitude_series == "No").sum())

count_cols = st.columns(2)
with count_cols[0]:
    st.markdown(
        f'<div style="padding:14px 18px;border:1px solid var(--border);'
        f'border-radius:var(--radius-md);background:var(--accent-soft);'
        f'text-align:center;margin-top:14px;">'
        f'<div style="font-family:var(--font-display);font-size:11px;'
        f'text-transform:uppercase;letter-spacing:0.12em;color:var(--text2);'
        f'margin-bottom:6px;">Stayed with myself</div>'
        f'<div style="font-family:var(--font-display);font-size:22px;'
        f'font-weight:700;color:var(--accent-2);">{stayed_count}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
with count_cols[1]:
    st.markdown(
        f'<div style="padding:14px 18px;border:1px solid var(--border);'
        f'border-radius:var(--radius-md);background:rgba(201,122,138,0.08);'
        f'text-align:center;margin-top:14px;">'
        f'<div style="font-family:var(--font-display);font-size:11px;'
        f'text-transform:uppercase;letter-spacing:0.12em;color:var(--text2);'
        f'margin-bottom:6px;">Abandoned myself</div>'
        f'<div style="font-family:var(--font-display);font-size:22px;'
        f'font-weight:700;color:var(--neg);">{abandoned_count}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

if st.button("Save", use_container_width=True, key="save_gratitude"):
    new_row = pd.DataFrame([{
        "date": today_str,
        "gratitude_note": gratitude_choice,
    }])
    updated = pd.concat([gratitude_df, new_row], ignore_index=True)
    with st.spinner("Saving..."):
        save_thyself_gratitude_df(updated)
    st.success("Saved.")
    st.rerun()


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

if st.button("Save pattern entry", use_container_width=True, key="save_pattern"):
    new_row = pd.DataFrame([{
        "date": today_str,
        "pattern_type": pattern_type,
    }])
    updated = pd.concat([patterns_df, new_row], ignore_index=True)
    with st.spinner("Saving..."):
        save_thyself_patterns_df(updated)
    st.success("Pattern logged.")
    st.rerun()

# Past Patterns
with st.expander("Past Patterns", expanded=False):
    if patterns_df.empty:
        st.markdown(
            '<div class="list-row" style="justify-content:center;opacity:0.7;">'
            'No pattern entries yet.</div>',
            unsafe_allow_html=True,
        )
    else:
        pat_view = patterns_df.copy()
        pat_view["_date_parsed"] = pd.to_datetime(pat_view["date"], errors="coerce")
        pat_view = pat_view.dropna(subset=["_date_parsed"]).sort_values("_date_parsed", ascending=False)

        col_widths = [3, 4, 2]
        header_cols = st.columns(col_widths)
        for c, label in zip(header_cols, ["Date", "Pattern Type", ""]):
            c.markdown(
                f'<div style="font-family:var(--font-display);font-size:11px;'
                f'text-transform:uppercase;letter-spacing:0.1em;color:var(--text2);'
                f'padding:6px 0;border-bottom:1px solid var(--border);">{label}</div>',
                unsafe_allow_html=True,
            )

        for idx, r in pat_view.iterrows():
            p_date = clean_text(r.get("date", ""))
            p_type = clean_text(r.get("pattern_type", ""))

            row_cols = st.columns(col_widths)
            row_cols[0].markdown(
                f'<div style="font-size:13px;color:var(--text);padding:10px 0;">{p_date}</div>',
                unsafe_allow_html=True,
            )
            row_cols[1].markdown(
                f'<div style="font-size:13px;color:var(--accent);padding:10px 0;">{p_type}</div>',
                unsafe_allow_html=True,
            )
            with row_cols[2]:
                if st.button("Delete", key=f"del_pat_{idx}", use_container_width=True):
                    save_thyself_patterns_df(patterns_df.drop(idx).reset_index(drop=True))
                    st.rerun()


# =========================================================
# SECTION 4 — WEEKLY REFLECTION
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

# Past Weekly Reflections
with st.expander("Past Weekly Reflections", expanded=False):
    if weekly_df.empty:
        st.markdown(
            '<div class="list-row" style="justify-content:center;opacity:0.7;">'
            'No weekly reflections yet.</div>',
            unsafe_allow_html=True,
        )
    else:
        wk_view = weekly_df.copy()
        wk_view["_date_parsed"] = pd.to_datetime(wk_view["date"], errors="coerce")
        wk_view = wk_view.dropna(subset=["_date_parsed"]).sort_values("_date_parsed", ascending=False)

        WK_PROMPTS = [
            ("fear_driven_week", "Where did I put others first from fear this week?"),
            ("chose_self", "Where did I choose myself this week?"),
            ("body_listened", "What did my body tell me that I actually listened to?"),
        ]

        for idx, r in wk_view.iterrows():
            label = r["_date_parsed"].strftime("%A, %d %B %Y")
            row_cols = st.columns([8, 2])
            with row_cols[0]:
                blocks_html = (
                    f'<div style="font-family:var(--font-display);font-size:13px;'
                    f'text-transform:uppercase;letter-spacing:0.1em;color:var(--text2);'
                    f'margin:8px 0 12px;border-bottom:1px solid var(--border);'
                    f'padding-bottom:6px;">{label}</div>'
                )
                for col, prompt in WK_PROMPTS:
                    val = clean_text(r.get(col, ""))
                    if not val:
                        continue
                    blocks_html += (
                        f'<div style="margin-bottom:14px;">'
                        f'<div style="font-family:var(--font-display);font-size:11px;'
                        f'text-transform:uppercase;letter-spacing:0.1em;color:var(--accent);'
                        f'margin-bottom:6px;">{prompt}</div>'
                        f'<div style="white-space:pre-wrap;font-size:14px;line-height:1.7;'
                        f'color:var(--text);">{val}</div>'
                        f'</div>'
                    )
                st.markdown(blocks_html, unsafe_allow_html=True)
            with row_cols[1]:
                if st.button("Delete", key=f"del_wk_{idx}", use_container_width=True):
                    save_thyself_weekly_df(weekly_df.drop(idx).reset_index(drop=True))
                    st.rerun()


# ── Footer note ───────────────────────────────────────────
st.markdown(
    '<div style="margin-top:36px;padding-top:18px;border-top:1px solid var(--border);'
    'font-size:11px;color:var(--text3);text-align:center;">'
    'Your data is stored in Google Sheets. Keep your sheet private.</div>',
    unsafe_allow_html=True,
)
