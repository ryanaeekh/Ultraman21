import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Journal", page_icon="\U0001f4d3", layout="wide", initial_sidebar_state="collapsed")

from theme import inject_theme, nav_menu, page_header
from utils import load_journal, save_journal_df, clean_text

inject_theme()
nav_menu("Journal")

today = date.today()
today_str = str(today)
pretty = today.strftime("%A, %d %B %Y")

PROMPTS = [
    "What's one thing you're proud of from yesterday?",
    "What weighed on your mind most this morning?",
    "Who do you want to become in the next year?",
    "What did you avoid today, and why?",
    "What's a small win you can build on tomorrow?",
    "What's draining your energy right now?",
    "What's one belief you held a year ago that no longer fits?",
    "What would you do differently if no one was watching?",
    "What are you grateful for that you usually overlook?",
    "Where did fear show up in your decisions today?",
    "What does \"enough\" look like for you this week?",
    "What's one truth you've been avoiding?",
    "Where are you spending time without intention?",
    "What did your body try to tell you today?",
    "What's the next right thing — not the perfect thing?",
    "Who do you owe a conversation, and what's stopping you?",
    "What's one habit shaping who you're becoming?",
    "What's underneath the frustration you felt today?",
    "If today repeated for a year, what would your life look like?",
    "What do you need to forgive yourself for?",
]

MOODS = ["\U0001f614", "\U0001f610", "\U0001f642", "\U0001f60a", "\U0001f525"]

SESSIONS = ["Morning", "Noon", "Night"]


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


journal_df = load_journal()

streak = calc_streak(journal_df)
streak_html = (
    f'<div style="font-size:18px;font-weight:600;color:var(--accent-2);margin-bottom:8px;">'
    f'\U0001f525 {streak} day streak</div>'
) if streak > 0 else (
    '<div style="font-size:14px;color:var(--text3);margin-bottom:8px;">'
    'No active streak — write today to start one.</div>'
)
st.markdown(streak_html, unsafe_allow_html=True)

st.markdown(page_header(pretty, "A quiet place to think"), unsafe_allow_html=True)

prompt = PROMPTS[today.toordinal() % len(PROMPTS)]
st.markdown(
    f'<div style="font-style:italic;color:var(--text2);font-size:16px;'
    f'padding:12px 16px;border-left:3px solid var(--accent);'
    f'background:var(--accent-soft);border-radius:8px;margin-bottom:18px;">'
    f'{prompt}</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div style="font-size:13px;color:var(--text2);'
    'text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">Mood</div>',
    unsafe_allow_html=True,
)
selected_mood = st.session_state.get("selected_mood", "")
mood_cols = st.columns(5)
for i, m in enumerate(MOODS):
    btn_type = "primary" if selected_mood == m else "secondary"
    if mood_cols[i].button(m, key=f"mood_btn_{i}", type=btn_type, use_container_width=True):
        st.session_state["selected_mood"] = "" if selected_mood == m else m
        st.rerun()

st.markdown(
    '<div style="font-size:13px;color:var(--text2);'
    'text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">Session</div>',
    unsafe_allow_html=True,
)
selected_session = st.session_state.get("selected_session", "")
session_cols = st.columns(3)
for i, s in enumerate(SESSIONS):
    btn_type = "primary" if selected_session == s else "secondary"
    if session_cols[i].button(s, key=f"session_btn_{i}", type=btn_type, use_container_width=True):
        st.session_state["selected_session"] = "" if selected_session == s else s
        st.rerun()

entry = st.text_area("Entry", value="", height=320, key="journal_entry",
                     placeholder="Write freely. No judgement. Just presence.")

word_count = len(st.session_state.get("journal_entry", "").split())
st.markdown(
    f'<div style="text-align:right;font-size:12px;color:var(--text3);margin:-8px 0 12px;">'
    f'{word_count} word{"" if word_count == 1 else "s"}</div>',
    unsafe_allow_html=True,
)

tags_input = st.text_input("Tags", value="", key="journal_tags",
                           placeholder="trading, mindset, family")

if st.button("Save Entry", use_container_width=True, key="save_journal"):
    trimmed = entry.strip()
    if trimmed:
        now_time = datetime.now().strftime("%H:%M")
        clean_tags = ", ".join(t.strip() for t in tags_input.split(",") if t.strip())
        new_row = pd.DataFrame([{
            "date": today_str,
            "time": now_time,
            "session": st.session_state.get("selected_session", ""),
            "entry": trimmed,
            "mood": st.session_state.get("selected_mood", ""),
            "tags": clean_tags,
        }])
        updated = pd.concat([journal_df, new_row], ignore_index=True)
        with st.spinner("Saving..."):
            save_journal_df(updated)
        st.session_state["selected_mood"] = ""
        st.session_state["selected_session"] = ""
        st.success("Entry saved.")
        st.rerun()
    else:
        st.warning("Write something before saving.")

# Past entries
_pe_cols = st.columns([6, 4])
with _pe_cols[0]:
    st.markdown('<div class="section-title">\U0001f4da Past Entries</div>', unsafe_allow_html=True)
with _pe_cols[1]:
    show_all = st.checkbox("Show all", value=False, key="journal_show_all")
    st.caption("Last 30 days by default" if not show_all else "Showing all entries")

search = st.text_input("Search", value="", key="journal_search",
                       placeholder="Search entries and tags...",
                       label_visibility="collapsed")

if journal_df.empty:
    st.markdown('<div class="list-row" style="justify-content:center;opacity:0.7;">No entries yet.</div>', unsafe_allow_html=True)
else:
    all_entries = journal_df.copy()
    all_entries["date_parsed"] = pd.to_datetime(all_entries["date"], errors="coerce")
    all_entries = all_entries.dropna(subset=["date_parsed"]).sort_values("date_parsed", ascending=False)

    if not show_all:
        cutoff = pd.Timestamp(today - timedelta(days=30))
        all_entries = all_entries[all_entries["date_parsed"] >= cutoff]

    if search.strip():
        needle = search.strip().lower()
        entry_match = all_entries["entry"].fillna("").astype(str).str.lower().str.contains(needle, regex=False)
        tags_match = all_entries.get("tags", pd.Series([""] * len(all_entries))).fillna("").astype(str).str.lower().str.contains(needle, regex=False)
        all_entries = all_entries[entry_match | tags_match]

    if all_entries.empty:
        st.markdown('<div class="list-row" style="justify-content:center;opacity:0.7;">No matching entries.</div>', unsafe_allow_html=True)
    else:
        all_entries["_date_key"] = all_entries["date_parsed"].dt.date.astype(str)
        grouped = all_entries.groupby("_date_key")
        for day_str in sorted(grouped.groups.keys(), reverse=True):
            day_entries = grouped.get_group(day_str)
            label = day_entries.iloc[0]["date_parsed"].strftime("%A, %d %B %Y")
            count = len(day_entries)
            with st.expander(f"{label}  ({count} {'entry' if count == 1 else 'entries'})"):
                for idx, r in day_entries.iterrows():
                    time_str = clean_text(r.get("time", ""))
                    session_str = clean_text(r.get("session", ""))
                    mood_str = clean_text(r.get("mood", ""))
                    tags_str = clean_text(r.get("tags", ""))
                    body = clean_text(r["entry"])

                    meta_parts = []
                    if time_str:
                        meta_parts.append(
                            f'<span style="color:var(--accent);font-weight:600;">{time_str}</span>'
                        )
                    if session_str:
                        meta_parts.append(
                            f'<span style="color:var(--text2);font-size:13px;'
                            f'text-transform:uppercase;letter-spacing:0.08em;">{session_str}</span>'
                        )
                    if mood_str:
                        meta_parts.append(
                            f'<span style="font-size:18px;">{mood_str}</span>'
                        )
                    meta_html = " · ".join(meta_parts)

                    badges_html = ""
                    if tags_str:
                        badges_html = " ".join(
                            f'<span style="display:inline-block;padding:2px 10px;'
                            f'margin:0 4px 4px 0;font-size:11px;border-radius:999px;'
                            f'background:var(--accent-soft);color:var(--accent-2);'
                            f'border:1px solid var(--border);">{t.strip()}</span>'
                            for t in tags_str.split(",") if t.strip()
                        )
                        badges_html = f'<div style="margin:6px 0;">{badges_html}</div>'

                    row_cols = st.columns([8, 2])
                    with row_cols[0]:
                        st.markdown(
                            (f'<div style="margin-bottom:6px;">{meta_html}</div>' if meta_html else "")
                            + badges_html
                            + f'<div style="white-space:pre-wrap;font-size:15px;line-height:1.85;'
                            f'color:var(--text);opacity:0.92;margin-bottom:16px;">{body}</div>',
                            unsafe_allow_html=True,
                        )
                    with row_cols[1]:
                        if st.button("Delete", key=f"del_j_{idx}", use_container_width=True):
                            save_journal_df(journal_df.drop(idx).reset_index(drop=True))
                            st.rerun()
