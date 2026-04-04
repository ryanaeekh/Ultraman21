"""AI Coach — personal productivity assistant powered by Claude."""

import os
from datetime import date, timedelta

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from theme import inject_theme, nav_menu, page_header, ACCENT
from utils import clean_text as _clean_text

load_dotenv()

# ── Data paths ────────────────────────────────────────────
DATA_FOLDER = "data"
PLANNER_FILE = os.path.join(DATA_FOLDER, "planner.csv")
SETTINGS_FILE = os.path.join(DATA_FOLDER, "settings.csv")

# ── Local data helpers ────────────────────────────────────

def _load_planner():
    if not os.path.exists(PLANNER_FILE):
        return pd.DataFrame()
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


def _load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return pd.DataFrame()
    return pd.read_csv(SETTINGS_FILE)


# ── Build data context for AI ─────────────────────────────

def _build_data_context():
    lines = []
    week_ago = str(date.today() - timedelta(days=6))

    # Planner data
    pdf = _load_planner()
    if not pdf.empty:
        recent = pdf[pdf["date"] >= week_ago].sort_values("date")
        total_days = len(pdf)
        if not recent.empty:
            weekly_avg = int(recent["score"].mean())
        else:
            weekly_avg = 0
        lines.append(
            f"=== PLANNER (last 7 days) ===\n"
            f"Total days logged: {total_days}, Weekly avg: {weekly_avg}/100"
        )
        for _, r in recent.iterrows():
            lines.append(
                f"  {r['date']}: score={r['score']}, focus={r['focus_done']}, "
                f"run={r['run_done']}, income={r['income_done']}, "
                f"reflection={_clean_text(r['reflection'])[:100]}"
            )

    # Finance data
    fin_path = os.path.join(DATA_FOLDER, "finance.csv")
    if os.path.exists(fin_path):
        fdf = pd.read_csv(fin_path)
        if not fdf.empty and "date" in fdf.columns:
            fdf["date"] = fdf["date"].astype(str)
            week_fin = fdf[fdf["date"] >= week_ago]
            total_spent = (
                round(week_fin["amount"].astype(float).sum(), 2)
                if not week_fin.empty and "amount" in fdf.columns
                else 0
            )
            lines.append(f"\n=== EXPENSES (last 7 days) ===\nTotal variable spending: ${total_spent}")
            if not week_fin.empty and "category" in fdf.columns:
                by_cat = week_fin.groupby("category")["amount"].sum().sort_values(ascending=False)
                for cat, amt in by_cat.items():
                    lines.append(f"  {cat}: ${amt:.2f}")

    # Driving data
    drv_path = os.path.join(DATA_FOLDER, "driving.csv")
    if os.path.exists(drv_path):
        ddf = pd.read_csv(drv_path)
        if not ddf.empty and "date" in ddf.columns and "earnings" in ddf.columns:
            ddf["date"] = ddf["date"].astype(str)
            week_drv = ddf[ddf["date"] >= week_ago]
            total_earned = round(week_drv["earnings"].astype(float).sum(), 2) if not week_drv.empty else 0
            lines.append(f"\n=== DRIVING INCOME (last 7 days) ===\nTotal earned: ${total_earned}")

    # Exercise data
    ex_path = os.path.join(DATA_FOLDER, "exercise.csv")
    if os.path.exists(ex_path):
        edf = pd.read_csv(ex_path)
        if not edf.empty and "date" in edf.columns:
            edf["date"] = edf["date"].astype(str)
            week_ex = edf[edf["date"] >= week_ago]
            if not week_ex.empty:
                done_count = len(
                    week_ex[week_ex["status"].astype(str).str.lower().isin(["done", "completed", "yes"])]
                )
                lines.append(f"\n=== EXERCISE (last 7 days) ===\n{done_count} completed sessions")

    # Goals
    sdf = _load_settings()
    if not sdf.empty:
        saved_goals = _clean_text(sdf.loc[0, "long_term_goals"]) if "long_term_goals" in sdf.columns else ""
        if saved_goals:
            lines.append(f"\n=== LONG TERM GOALS ===\n{saved_goals}")

        # Targets
        try:
            lines.append(
                f"\n=== TARGETS ===\n"
                f"Daily income target: ${float(sdf.loc[0, 'daily_income_target']):.0f}, "
                f"Daily budget: ${float(sdf.loc[0, 'daily_budget']):.0f}, "
                f"Monthly budget: ${float(sdf.loc[0, 'monthly_budget']):.0f}"
            )
        except Exception:
            pass

    return "\n".join(lines) if lines else "No data available yet."


# ── System prompt ─────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are Ryan's personal AI productivity coach inside his Planner21 app. "
    "You have access to his real data (planner scores, expenses, driving income, exercise, goals). "
    "Be direct, actionable, and motivating. Keep responses concise (2-4 paragraphs max). "
    "When giving advice, reference his actual numbers. "
    "Speak like a trusted mentor — firm but supportive."
)


# ── Page ──────────────────────────────────────────────────

inject_theme()
nav_menu("AI Coach")

st.markdown(
    page_header("AI Coach", "Your personal productivity assistant — powered by Claude"),
    unsafe_allow_html=True,
)

api_key = os.getenv("ANTHROPIC_API_KEY", "")

if not api_key:
    st.markdown(
        '<div class="card" style="border-left:3px solid #ffb400">'
        '<div style="color:#ffb400;font-weight:600;margin-bottom:8px">API Key Required</div>'
        '<div style="color:var(--text2);font-size:14px">'
        "No Anthropic API key found. Add your key to the <code>.env</code> file in the project root:"
        "</div></div>",
        unsafe_allow_html=True,
    )
    st.code("ANTHROPIC_API_KEY=sk-ant-...")
    st.info("Get your key at https://console.anthropic.com/")
    st.stop()

# Conditional import — only needed when API key is present
try:
    import anthropic
except ImportError:
    st.error("The `anthropic` package is not installed. Run `pip install anthropic` to enable the AI Coach.")
    st.stop()

# ── Smart Features ────────────────────────────────────────

st.markdown(
    '<div class="section-title">Smart Features</div>',
    unsafe_allow_html=True,
)

data_ctx = _build_data_context()

sf1, sf2 = st.columns(2, gap="medium")

with sf1:
    if st.button("Spending Advice", use_container_width=True):
        with st.spinner("Analyzing your spending..."):
            client = anthropic.Anthropic(api_key=api_key)
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                system="You are a concise financial advisor. Analyze the user's spending data and give 3 specific, actionable tips. Reference actual numbers.",
                messages=[{"role": "user", "content": f"Here is my financial data:\n\n{data_ctx}\n\nGive me spending advice based on this data."}],
            )
            st.markdown(resp.content[0].text)

    if st.button("Reflection Prompt", use_container_width=True):
        with st.spinner("Generating reflection prompt..."):
            client = anthropic.Anthropic(api_key=api_key)
            # Build today context
            pdf = _load_planner()
            today_str = str(date.today())
            today_row = pdf[pdf["date"] == today_str].iloc[0] if not pdf.empty and today_str in pdf["date"].values else None
            if today_row is not None:
                today_score = int(today_row["score"])
                refl = _clean_text(today_row["reflection"])
                today_info = f"Today's score: {today_score}/100. " + (f"Reflection so far: {refl}" if refl else "No reflection written yet.")
            else:
                today_info = "No entry logged for today yet."
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                system="You are a reflective journaling coach. Generate ONE thoughtful reflection question tailored to the user's day. Make it specific to their score and situation, not generic.",
                messages=[{"role": "user", "content": f"{today_info}\n\nRecent context:\n{data_ctx}\n\nGive me a personalized reflection prompt for tonight."}],
            )
            st.markdown(resp.content[0].text)

with sf2:
    if st.button("Weekly Summary", use_container_width=True):
        with st.spinner("Analyzing your week..."):
            client = anthropic.Anthropic(api_key=api_key)
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=600,
                system="You are a weekly review coach. Analyze the user's week across all dimensions (execution, money, exercise, habits) and give a structured summary with 1 win, 1 concern, and 1 action for next week. Use actual numbers.",
                messages=[{"role": "user", "content": f"Here is my data for the past week:\n\n{data_ctx}\n\nGive me my weekly summary."}],
            )
            st.markdown(resp.content[0].text)

    if st.button("Goal Coaching", use_container_width=True):
        with st.spinner("Coaching on your goals..."):
            client = anthropic.Anthropic(api_key=api_key)
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                system="You are a goal-setting coach. Based on the user's actual performance data and current goals, suggest realistic adjustments or new micro-goals. Be specific — reference their numbers.",
                messages=[{"role": "user", "content": f"Here is my data and goals:\n\n{data_ctx}\n\nCoach me on my goals — what should I adjust or focus on?"}],
            )
            st.markdown(resp.content[0].text)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Chat Interface ────────────────────────────────────────

st.markdown(
    '<div class="section-title">Chat with AI Coach</div>',
    unsafe_allow_html=True,
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask your AI coach anything..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            client = anthropic.Anthropic(api_key=api_key)

            # Build messages with data context in first user message
            api_messages = []
            for i, msg in enumerate(st.session_state.chat_history):
                content = msg["content"]
                if i == 0 and msg["role"] == "user":
                    content = f"[MY PLANNER DATA]\n{data_ctx}\n\n[MY QUESTION]\n{content}"
                api_messages.append({"role": msg["role"], "content": content})

            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                system=SYSTEM_PROMPT,
                messages=api_messages,
            )
            reply = resp.content[0].text
            st.markdown(reply)

    st.session_state.chat_history.append({"role": "assistant", "content": reply})

if st.session_state.chat_history and st.button("Clear chat"):
    st.session_state.chat_history = []
    st.rerun()
