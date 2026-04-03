import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="Journal", page_icon="📓", layout="wide")

st.markdown("""
<style>
:root {
    --accent: #8a7055;
    --pos: #5a9a6a; --neg: #b87070;
    --border: 1px solid rgba(0,0,0,0.07);
    --shadow: 0 1px 3px rgba(0,0,0,0.04);
    --radius: 18px;
}
@media (prefers-color-scheme: dark) {
    :root {
        --accent: #b08a65;
        --border: 1px solid rgba(255,255,255,0.07);
        --shadow: 0 1px 3px rgba(0,0,0,0.12);
        --pos: #7ab88a;
    }
}
[data-theme="dark"] {
    --accent: #b08a65;
    --border: 1px solid rgba(255,255,255,0.07);
    --shadow: 0 1px 3px rgba(0,0,0,0.12);
    --pos: #7ab88a;
}

.stDecoration { display: none !important; }
html, body, [class*="css"] { font-family: Georgia, 'Times New Roman', serif !important; }
.block-container {
    max-width: 900px;
    padding-top: 4rem !important;
    padding-bottom: 4rem !important;
}
div[data-testid="stForm"] {
    border: none !important; padding: 0 !important; background: transparent !important;
}
div.stButton > button {
    border-radius: 12px !important;
    border: 1px solid rgba(0,0,0,0.14) !important;
    font-weight: 400 !important;
    font-family: Georgia, serif !important;
    background: var(--secondary-background-color) !important;
    color: inherit !important;
}
div.stButton > button:hover {
    border-color: var(--accent) !important;
}

.j-card {
    border: var(--border);
    border-radius: 18px;
    padding: 24px 28px;
    background: var(--secondary-background-color);
    box-shadow: var(--shadow);
    margin-bottom: 14px;
}
.j-date {
    font-size: 10px;
    opacity: 0.55;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 400;
    margin-bottom: 8px;
}
.j-text {
    font-size: 15px;
    line-height: 1.85;
    white-space: pre-wrap;
}
</style>
""", unsafe_allow_html=True)

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
_dark = st.session_state["dark_mode"]
_bg    = "#0e1117" if _dark else "#f5f0e8"
_sbg   = "#161b22" if _dark else "#ede8de"
_color = "#fafafa" if _dark else "#3a3028"
st.markdown(f"""<style>
.stApp {{ background-color: {_bg} !important; color: {_color} !important; }}
section[data-testid="stSidebar"] > div:first-child {{ background-color: {_sbg} !important; }}
header[data-testid="stHeader"] {{ background-color: {_bg} !important; }}
</style>""", unsafe_allow_html=True)

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

# --- Title ---
st.title("📓 Journal")
st.caption("Thoughts, ideas, and anything that doesn't fit elsewhere.")
st.markdown("---")

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
    st.markdown("### Past Entries")
    past = past.sort_values("date", ascending=False)
    for _, row in past.iterrows():
        st.markdown(
            f'<div class="j-card">'
            f'<div class="j-date">{row["date"]}</div>'
            f'<div class="j-text">{row["entry"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
