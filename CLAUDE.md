# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

This is a multi-page Streamlit app. The entry point is `planner21.py` (the planner/daily log page). The other pages live in `pages/` and are auto-loaded by Streamlit.

```bash
# Run from the Ultraman21 directory
python -m streamlit run planner21.py
```

All pages are accessible from the sidebar once the app is running.

## Architecture

**Two-tier structure:**
- `planner21.py` — standalone entry point; has its own inline data helpers (does not import `utils.py`)
- `pages/` — multi-page Streamlit files loaded automatically; `dashboard.py` and `excercise.py` also duplicate helpers locally rather than importing from `utils.py`
- `utils.py` — shared data layer with canonical column schemas, loaders, and cross-module calculations; currently only partially adopted by pages

**Data layer (`data/` folder — CSV files):**
| File | Purpose |
|---|---|
| `planner.csv` | Daily planner entries (priorities, score, reflections) |
| `driving.csv` | Driving income logs (written only by `driving.py`) |
| `finance.csv` | Daily variable expenses |
| `monthly_expenses.csv` | Recurring monthly fixed costs |
| `exercise.csv` | Exercise sessions |

**Cross-module data contract:**
- `driving.py` is the **sole writer** of `driving.csv`. All other pages (`finance.py`, `dashboard.py`) read it read-only.
- `finance.py` explicitly guards against overwriting `driving.csv`.
- Fixed monthly expenses are amortized as a daily share (`total / days_in_month`) when calculating daily/monthly net figures — this pattern appears in `utils.py`, `finance.py`, and `dashboard.py`.

**Scoring system (planner):**
- Priorities done (focus_done): 40 pts
- Run done: 20 pts
- Income target done: 40 pts
- Total: 100 pts

**Known issue:** `planner21.py` sidebar nav only exposes `["Today", "Settings"]` but the file contains dead `History` and `Insights` page handlers (lines 521–678) that are unreachable.

## Styling Conventions

All pages use inline `st.markdown(..., unsafe_allow_html=True)` with CSS custom properties. The shared design tokens are:
- `--accent: #a08060` (warm brown)
- `--pos: #6a9e7a` (green for positive values)
- `--neg: #b87070` (red for negative values)
- `--border`, `--shadow`, `--radius-lg/md` for consistent card styling

Each page defines its own `<style>` block — there is no shared CSS file.
