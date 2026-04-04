import streamlit as st
import pandas as pd
from datetime import date
from theme import inject_theme, nav_menu, page_header
from utils import load_journal, save_journal_df, JOURNAL_COLUMNS

st.set_page_config(page_title="Journal", page_icon="📓", layout="wide", initial_sidebar_state="collapsed")

inject_theme()
nav_menu("Journal")
st.markdown('<style>.block-container{max-width:900px !important;}</style>', unsafe_allow_html=True)
st.markdown(page_header("Journal", "Daily reflections"), unsafe_allow_html=True)


@st.cache_data(ttl=15)
def _load_journal():
    df = load_journal()
    if "entry" in df.columns:
        df["entry"] = df["entry"].fillna("")
    return df


def _invalidate():
    _load_journal.clear()


def save_journal(df):
    save_journal_df(df)
    _invalidate()


today_str = date.today().strftime("%Y-%m-%d")
df = _load_journal()

# --- Today's entry ---
existing = df[df["date"] == today_str]
prefill = existing.iloc[0]["entry"] if len(existing) > 0 else ""

with st.form("journal_form", clear_on_submit=False):
    entry = st.text_area("Today's entry", value=prefill, height=300, placeholder="Write freely...")
    submitted = st.form_submit_button("Save")

if submitted:
    df = _load_journal()
    if len(df[df["date"] == today_str]) > 0:
        df.loc[df["date"] == today_str, "entry"] = entry
    else:
        new_row = pd.DataFrame([{"date": today_str, "entry": entry}])
        df = pd.concat([df, new_row], ignore_index=True)
    save_journal(df)
    st.success("Entry saved.")
    st.rerun()

# --- Past entries ---
past = df[df["date"] != today_str].copy()
if len(past) > 0:
    st.markdown('<div class="section-title">Past Entries</div>', unsafe_allow_html=True)
    past = past.sort_values("date", ascending=False)
    for _, row in past.iterrows():
        st.markdown(
            f'<div class="j-card">'
            f'<div class="j-date">{row["date"]}</div>'
            f'<div class="j-text">{row["entry"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
