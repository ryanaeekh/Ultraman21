"""History page — browse and manage past daily planner entries."""

import os

import pandas as pd
import streamlit as st

from theme import inject_theme, nav_menu, page_header, status_badge, progress_bar, ACCENT, POS, NEG
from utils import backup_csv, clean_text

# ─── Constants ───────────────────────────────────────────────────────
DATA_FOLDER = "data"
PLANNER_FILE = os.path.join(DATA_FOLDER, "planner.csv")
BACKUP_FOLDER = os.path.join(DATA_FOLDER, "backups")

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

PLANNER_COLS = [
    "date", "priority_1", "priority_2", "priority_3",
    "focus_done", "run_done", "income_done", "reflection", "score",
]

# ─── File bootstrap ──────────────────────────────────────────────────
if not os.path.exists(PLANNER_FILE):
    pd.DataFrame(columns=PLANNER_COLS).to_csv(PLANNER_FILE, index=False)


def _ensure_columns(path, required_cols, default_row=None):
    df = pd.read_csv(path)
    if list(df.columns) != required_cols:
        df = pd.DataFrame([default_row] if default_row else [], columns=required_cols)
        df.to_csv(path, index=False)
    return df


_ensure_columns(PLANNER_FILE, PLANNER_COLS)


# ─── Data helpers ────────────────────────────────────────────────────
@st.cache_data
def load_planner():
    df = pd.read_csv(PLANNER_FILE)
    if "date" in df.columns:
        df["date"] = df["date"].astype(str)
    for col in ["focus_done", "run_done", "income_done"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda v: str(v).strip().lower() == "true")
    for col in ["score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    return df


def save_planner(df: pd.DataFrame):
    backup_csv(PLANNER_FILE)
    df.to_csv(PLANNER_FILE, index=False)
    invalidate_cache()


def invalidate_cache():
    load_planner.clear()


def get_execution_label(score):
    if score == 100:
        return "Fully Completed"
    elif score >= 70:
        return "Strong Progress"
    elif score >= 40:
        return "In Progress"
    else:
        return "Not Started"


# ─── Page content ────────────────────────────────────────────────────
inject_theme()
nav_menu("History")

st.markdown(page_header("History", "Your daily scores"), unsafe_allow_html=True)

planner_df = load_planner()

if planner_df.empty:
    st.info("No history yet. Start logging your days.")
else:
    hist = planner_df.sort_values("date", ascending=False).reset_index(drop=True)

    show_only_completed = st.checkbox("Show only days with score > 0", value=False)
    if show_only_completed:
        hist = hist[hist["score"] > 0]

    if hist.empty:
        st.info("No matching records.")
    else:
        for _, row in hist.iterrows():
            score = int(row["score"])
            label = get_execution_label(score)
            reflection = clean_text(row["reflection"])
            p1 = clean_text(row["priority_1"])
            p2 = clean_text(row["priority_2"])
            p3 = clean_text(row["priority_3"])

            bar_color = POS if score >= 70 else ACCENT
            label_color = POS if score >= 70 else (NEG if score < 40 else ACCENT)

            f_cls = "done" if row["focus_done"] else "pending"
            r_cls = "done" if row["run_done"] else "pending"
            i_cls = "done" if row["income_done"] else "pending"

            reflection_html = ""
            if reflection:
                reflection_html = (
                    f'<div style="margin-top:12px;padding-top:12px;'
                    f'border-top:1px solid var(--border);'
                    f'font-size:13px;color:var(--text2);font-style:italic;">'
                    f'{reflection}</div>'
                )

            card_html = (
                f'<div class="hist-card">'
                # Header row: date + score
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'  <span style="font-family:var(--font-display);font-size:16px;font-weight:600;">{row["date"]}</span>'
                f'  <span style="font-size:22px;font-weight:700;color:{bar_color}">{score}<span style="font-size:13px;opacity:.5">/100</span></span>'
                f'</div>'
                # Progress bar
                f'{progress_bar(score, bar_color)}'
                # Status badge
                f'<div style="margin:8px 0 14px;">{status_badge(label, label_color)}</div>'
                # Two-column grid: priorities + execution
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">'
                # Priorities column
                f'  <div>'
                f'    <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.08em;color:var(--text2);margin-bottom:8px;">Priorities</div>'
                f'    <div style="font-size:13px;color:var(--text);margin-bottom:4px;">1 &middot; {p1 or "&mdash;"}</div>'
                f'    <div style="font-size:13px;color:var(--text);margin-bottom:4px;">2 &middot; {p2 or "&mdash;"}</div>'
                f'    <div style="font-size:13px;color:var(--text);">3 &middot; {p3 or "&mdash;"}</div>'
                f'  </div>'
                # Execution column
                f'  <div>'
                f'    <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.08em;color:var(--text2);margin-bottom:8px;">Execution</div>'
                f'    <div class="exec-pills">'
                f'      <span class="exec-pill {f_cls}">Focus</span>'
                f'      <span class="exec-pill {r_cls}">Run</span>'
                f'      <span class="exec-pill {i_cls}">Income</span>'
                f'    </div>'
                f'  </div>'
                f'</div>'
                # Reflection
                f'{reflection_html}'
                f'</div>'
            )

            st.markdown(card_html, unsafe_allow_html=True)

            if st.button("Delete", key=f"del_{row['date']}"):
                updated = planner_df[planner_df["date"] != row["date"]]
                save_planner(updated.reset_index(drop=True))
                st.rerun()
