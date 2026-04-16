import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime

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

entry = st.text_area("Entry", value="", height=320, key="journal_entry",
                     placeholder="Write freely. No judgement. Just presence.")

if st.button("Save Entry", use_container_width=True, key="save_journal"):
    trimmed = entry.strip()
    if trimmed:
        now_time = datetime.now().strftime("%H:%M")
        new_row = pd.DataFrame([{"date": today_str, "time": now_time, "entry": trimmed}])
        updated = pd.concat([journal_df, new_row], ignore_index=True)
        with st.spinner("Saving..."):
            save_journal_df(updated)
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

if journal_df.empty:
    st.markdown('<div class="list-row" style="justify-content:center;opacity:0.7;">No entries yet.</div>', unsafe_allow_html=True)
else:
    all_entries = journal_df.copy()
    all_entries["date_parsed"] = pd.to_datetime(all_entries["date"], errors="coerce")
    all_entries = all_entries.dropna(subset=["date_parsed"]).sort_values("date_parsed", ascending=False)

    if not show_all:
        from datetime import timedelta
        cutoff = pd.Timestamp(today - timedelta(days=30))
        all_entries = all_entries[all_entries["date_parsed"] >= cutoff]

    # Group by date (string key to avoid type mismatch)
    all_entries["_date_key"] = all_entries["date_parsed"].dt.date.astype(str)
    grouped = all_entries.groupby("_date_key")
    for day_str in sorted(grouped.groups.keys(), reverse=True):
        day_entries = grouped.get_group(day_str)
        label = day_entries.iloc[0]["date_parsed"].strftime("%A, %d %B %Y")
        count = len(day_entries)
        with st.expander(f"{label}  ({count} {'entry' if count == 1 else 'entries'})"):
            for idx, r in day_entries.iterrows():
                time_str = clean_text(r.get("time", ""))
                body = clean_text(r["entry"])
                time_label = f'<span style="color:var(--accent);font-weight:600;">{time_str}</span> — ' if time_str else ''
                row_cols = st.columns([8, 2])
                with row_cols[0]:
                    st.markdown(
                        f'<div style="white-space:pre-wrap;font-size:15px;line-height:1.85;color:var(--text);opacity:0.92;margin-bottom:16px;">'
                        f'{time_label}{body}</div>',
                        unsafe_allow_html=True,
                    )
                with row_cols[1]:
                    if st.button("Delete", key=f"del_j_{idx}", use_container_width=True):
                        save_journal_df(journal_df.drop(idx).reset_index(drop=True))
                        st.rerun()
