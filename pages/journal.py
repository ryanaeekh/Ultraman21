import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date

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

st.markdown(page_header(pretty, "A quiet place to think"), unsafe_allow_html=True)

journal_df = load_journal()

existing = ""
if not journal_df.empty:
    _jdates = pd.to_datetime(journal_df["date"], errors="coerce")
    match = journal_df[_jdates.dt.date == today]
    if not match.empty:
        existing = clean_text(match.iloc[0]["entry"])

entry = st.text_area("Entry", value=existing, height=320, key="journal_entry",
                     placeholder="Write freely. No judgement. Just presence.")

if st.button("Save Entry", use_container_width=True, key="save_journal"):
    trimmed = entry.strip()
    updated = journal_df.copy()
    updated = updated[pd.to_datetime(updated["date"], errors="coerce").dt.date != today]
    if trimmed:
        new_row = pd.DataFrame([{"date": today_str, "entry": trimmed}])
        updated = pd.concat([updated, new_row], ignore_index=True)
    with st.spinner("Saving..."):
        save_journal_df(updated)
    st.success("Entry saved.")
    st.rerun()

# Past entries
st.markdown('<div class="section-title">\U0001f4da Past Entries</div>', unsafe_allow_html=True)

if journal_df.empty:
    st.markdown('<div class="list-row" style="justify-content:center;opacity:0.7;">No entries yet.</div>', unsafe_allow_html=True)
else:
    past = journal_df.copy()
    past["date_parsed"] = pd.to_datetime(past["date"], errors="coerce")
    past = past.dropna(subset=["date_parsed"]).sort_values("date_parsed", ascending=False)
    past = past[past["date_parsed"].dt.date != today]
    for _, r in past.iterrows():
        label = r["date_parsed"].strftime("%A, %d %B %Y")
        body = clean_text(r["entry"])
        preview = (body[:120] + "\u2026") if len(body) > 120 else body
        with st.expander(f"{label}  \u2014  {preview}"):
            st.markdown(
                f'<div style="white-space:pre-wrap;font-size:15px;line-height:1.85;color:var(--text);opacity:0.92;">{body}</div>',
                unsafe_allow_html=True,
            )
