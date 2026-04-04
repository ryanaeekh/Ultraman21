"""History page — browse and manage past daily planner entries."""

import pandas as pd
import streamlit as st

from theme import inject_theme, nav_menu, page_header, status_badge, progress_bar, ACCENT, POS, NEG
from utils import load_planner, save_planner_df, clean_text

st.set_page_config(page_title="History", page_icon="📅", layout="wide", initial_sidebar_state="collapsed")

PLANNER_COLS = [
    "date", "priority_1", "priority_2", "priority_3",
    "focus_done", "run_done", "income_done", "reflection", "score",
]


@st.cache_data(ttl=15)
def _load_planner():
    df = load_planner()
    if "date" in df.columns:
        df["date"] = df["date"].astype(str)
    return df


def _invalidate():
    _load_planner.clear()


def save_planner(df: pd.DataFrame):
    save_planner_df(df)
    _invalidate()


def get_execution_label(score):
    if score == 100:    return "Fully Completed"
    elif score >= 70:   return "Strong Progress"
    elif score >= 40:   return "In Progress"
    else:               return "Not Started"


inject_theme()
nav_menu("History")

st.markdown(page_header("History", "Your daily scores"), unsafe_allow_html=True)

planner_df = _load_planner()

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
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'  <span style="font-family:var(--font-display);font-size:16px;font-weight:600;">{row["date"]}</span>'
                f'  <span style="font-size:22px;font-weight:700;color:{bar_color}">{score}<span style="font-size:13px;opacity:.5">/100</span></span>'
                f'</div>'
                f'{progress_bar(score, bar_color)}'
                f'<div style="margin:8px 0 14px;">{status_badge(label, label_color)}</div>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">'
                f'  <div>'
                f'    <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.08em;color:var(--text2);margin-bottom:8px;">Priorities</div>'
                f'    <div style="font-size:13px;color:var(--text);margin-bottom:4px;">1 &middot; {p1 or "&mdash;"}</div>'
                f'    <div style="font-size:13px;color:var(--text);margin-bottom:4px;">2 &middot; {p2 or "&mdash;"}</div>'
                f'    <div style="font-size:13px;color:var(--text);">3 &middot; {p3 or "&mdash;"}</div>'
                f'  </div>'
                f'  <div>'
                f'    <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.08em;color:var(--text2);margin-bottom:8px;">Execution</div>'
                f'    <div class="exec-pills">'
                f'      <span class="exec-pill {f_cls}">Focus</span>'
                f'      <span class="exec-pill {r_cls}">Run</span>'
                f'      <span class="exec-pill {i_cls}">Income</span>'
                f'    </div>'
                f'  </div>'
                f'</div>'
                f'{reflection_html}'
                f'</div>'
            )

            st.markdown(card_html, unsafe_allow_html=True)

            if st.button("Delete", key=f"del_{row['date']}"):
                updated = planner_df[planner_df["date"] != row["date"]]
                save_planner(updated.reset_index(drop=True))
                st.rerun()
