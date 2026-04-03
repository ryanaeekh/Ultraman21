import streamlit as st
import pandas as pd
import os
from datetime import date
from theme import inject_theme, page_header

st.set_page_config(page_title="Journal", page_icon="📓", layout="wide")

inject_theme()
st.markdown('<style>.block-container{max-width:900px !important;}</style>', unsafe_allow_html=True)
st.markdown(page_header("Journal", "Daily reflections"), unsafe_allow_html=True)

# --- Data ---
DATA_FOLDER = "data"
JOURNAL_FILE = os.path.join(DATA_FOLDER, "journal.csv")
os.makedirs(DATA_FOLDER, exist_ok=True)

BACKUP_FOLDER = os.path.join(DATA_FOLDER, "backups")
os.makedirs(BACKUP_FOLDER, exist_ok=True)

def backup_csv(filepath):
    """Create a timestamped backup before writing."""
    if os.path.exists(filepath):
        from datetime import datetime as dt_cls
        import shutil, glob
        basename = os.path.basename(filepath).replace(".csv", "")
        stamp = dt_cls.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(filepath, os.path.join(BACKUP_FOLDER, f"{basename}_{stamp}.csv"))
        for old in sorted(glob.glob(os.path.join(BACKUP_FOLDER, f"{basename}_*.csv")))[:-20]:
            os.remove(old)

def load_journal():
    if os.path.exists(JOURNAL_FILE):
        df = pd.read_csv(JOURNAL_FILE, dtype=str)
        df["entry"] = df["entry"].fillna("")
        return df
    return pd.DataFrame(columns=["date", "entry"])

def save_journal(df):
    backup_csv(JOURNAL_FILE)
    df.to_csv(JOURNAL_FILE, index=False)

today_str = date.today().strftime("%Y-%m-%d")
df = load_journal()

# --- Today's entry ---
existing = df[df["date"] == today_str]
prefill = existing.iloc[0]["entry"] if len(existing) > 0 else ""

with st.form("journal_form", clear_on_submit=False):
    entry = st.text_area("Today's entry", value=prefill, height=300,
                         placeholder="Write freely...")
    submitted = st.form_submit_button("Save")

if submitted:
    if len(existing) > 0:
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
