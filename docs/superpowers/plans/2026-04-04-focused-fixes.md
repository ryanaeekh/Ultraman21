# Focused Fixes & Utils Consolidation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix bugs, enhance utils.py with 5 specific improvements, and consolidate duplicated helpers across all pages.

**Architecture:** utils.py becomes the single source for shared helpers (backup_csv, safe_float, safe_bool, clean_text, coerce_numeric). Pages import from utils.py instead of redefining locally. No loader refactoring — each page keeps its own cached loaders.

**Tech Stack:** Python, Pandas, Streamlit

---

### Task 1: Enhance utils.py — add coerce_numeric, type hints, fix get_monthly_recurring_expenses

**Files:**
- Modify: `utils.py:1-215`

- [ ] **Step 1: Add `coerce_numeric` helper after the FILE/CSV HELPERS section (after line 99)**

Add this function between the `save_csv` function and the `SPECIFIC LOADERS` section:

```python
def coerce_numeric(df: pd.DataFrame, columns: list[str], fill: float = 0.0) -> pd.DataFrame:
    """Convert columns to numeric, filling NaN with *fill*."""
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(fill)
    return df
```

- [ ] **Step 2: Refactor all loaders to use `coerce_numeric`**

Replace the repeated `pd.to_numeric(...).fillna(...)` calls in every loader:

```python
def load_planner() -> pd.DataFrame:
    df = load_csv(PLANNER_FILE, PLANNER_COLUMNS)
    df = coerce_numeric(df, ["score"])
    for col in ["focus_done", "run_done", "income_done"]:
        df[col] = df[col].apply(lambda v: str(v).strip().lower() == "true")
    return df


def load_driving() -> pd.DataFrame:
    df = load_csv(DRIVING_FILE, DRIVING_COLUMNS)
    df = coerce_numeric(df, ["earnings", "hours_driven", "hourly_rate"])
    return df


def load_finance() -> pd.DataFrame:
    df = load_csv(FINANCE_FILE, FINANCE_COLUMNS)
    df = coerce_numeric(df, ["amount"])
    return df


def load_monthly_expenses() -> pd.DataFrame:
    df = load_csv(MONTHLY_EXPENSES_FILE, MONTHLY_EXPENSES_COLUMNS)
    df = coerce_numeric(df, ["amount"])
    return df


def load_exercise() -> pd.DataFrame:
    df = load_csv(EXERCISE_FILE, EXERCISE_COLUMNS)
    df = coerce_numeric(df, ["duration", "km"])
    return df
```

- [ ] **Step 3: Fix `get_monthly_recurring_expenses` — remove unused year/month params**

The function accepts `year` and `month` but never uses them. Since the monthly_expenses.csv stores flat recurring costs (not per-month), the params are misleading. Remove them and update callers.

Change:
```python
def get_monthly_recurring_expenses() -> float:
    return float(load_monthly_expenses()["amount"].sum())


def get_monthly_recurring_daily_share(year: int, month: int) -> float:
    total = get_monthly_recurring_expenses()
    days  = month_days(year, month)
    return float(total / days) if days > 0 else 0.0


def get_total_month_expense_with_recurring(year: int, month: int) -> float:
    return float(get_monthly_daily_expenses(year, month) + get_monthly_recurring_expenses())
```

- [ ] **Step 4: Add optional DataFrame params to `get_day_total_expense`**

```python
def get_day_total_expense(
    selected_date,
    finance_df: pd.DataFrame | None = None,
    monthly_df: pd.DataFrame | None = None,
) -> float:
    if isinstance(selected_date, str):
        selected_date = pd.to_datetime(selected_date, errors="coerce")
        if pd.isna(selected_date):
            return 0.0
        selected_date = selected_date.date()

    if finance_df is None:
        finance_df = load_finance()
    if monthly_df is None:
        monthly_df = load_monthly_expenses()

    daily_expense   = float(filter_by_exact_date(finance_df, selected_date)["amount"].sum())
    recurring_total = float(monthly_df["amount"].sum())
    daily_share     = recurring_total / month_days(selected_date.year, selected_date.month)
    return float(daily_expense + daily_share)
```

- [ ] **Step 5: Add type hints to all functions missing them**

Update these function signatures:
```python
def ensure_data_dir() -> None:
def ensure_csv(file_path: Path, columns: list[str]) -> None:
def load_csv(file_path: Path, columns: list[str]) -> pd.DataFrame:
def save_csv(df: pd.DataFrame, file_path: Path, columns: list[str]) -> None:
def normalize_date_column(df: pd.DataFrame, col: str = "date") -> pd.DataFrame:
def month_days(year: int, month: int) -> int:
def filter_by_month(df: pd.DataFrame, year: int, month: int, date_col: str = "date") -> pd.DataFrame:
def filter_by_exact_date(df: pd.DataFrame, selected_date, date_col: str = "date") -> pd.DataFrame:
def get_monthly_driving_income(year: int, month: int) -> float:
def get_monthly_daily_expenses(year: int, month: int) -> float:
def get_monthly_recurring_expenses() -> float:
def get_monthly_recurring_daily_share(year: int, month: int) -> float:
def get_total_month_expense_with_recurring(year: int, month: int) -> float:
def get_monthly_score_average(year: int, month: int) -> float:
```

- [ ] **Step 6: Verify by importing utils in Python**

Run: `cd /c/Users/ryana/OneDrive/Desktop/Ultraman21 && python -c "import utils; print('OK:', dir(utils))"`
Expected: No errors, `coerce_numeric` appears in output.

---

### Task 2: Add shared helpers to utils.py (backup_csv, safe_float, safe_bool, clean_text)

**Files:**
- Modify: `utils.py`

- [ ] **Step 1: Add shared helpers to utils.py**

Add these after the `coerce_numeric` function, before the SPECIFIC LOADERS section:

```python
# =========================================================
# COMMON HELPERS  (used across pages)
# =========================================================
BACKUP_DIR = DATA_DIR / "backups"


def backup_csv(filepath: str | Path) -> None:
    """Create a timestamped backup before writing. Keeps last 20."""
    filepath = Path(filepath)
    if not filepath.exists():
        return
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    from datetime import datetime as dt_cls
    import shutil
    basename = filepath.stem
    stamp = dt_cls.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(filepath, BACKUP_DIR / f"{basename}_{stamp}.csv")
    backups = sorted(BACKUP_DIR.glob(f"{basename}_*.csv"))
    for old in backups[:-20]:
        old.unlink()


def safe_float(value) -> float:
    """Convert value to float, returning 0.0 on failure."""
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def safe_bool(value) -> bool:
    """Check if value represents a True boolean string."""
    return str(value).strip().lower() == "true"


def clean_text(value) -> str:
    """Strip whitespace and filter 'nan' strings to empty."""
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text
```

- [ ] **Step 2: Add JOURNAL schema to utils.py**

After EXERCISE_COLUMNS, add:

```python
JOURNAL_COLUMNS = [
    "date",
    "entry",
]

SETTINGS_COLUMNS = [
    "long_term_goals",
    "daily_income_target",
    "hourly_rate_target",
    "daily_budget",
    "monthly_budget",
    "checklist_items",
    "expense_categories",
]
```

And add file paths:

```python
JOURNAL_FILE          = DATA_DIR / "journal.csv"
SETTINGS_FILE         = DATA_DIR / "settings.csv"
```

- [ ] **Step 3: Verify**

Run: `cd /c/Users/ryana/OneDrive/Desktop/Ultraman21 && python -c "from utils import backup_csv, safe_float, safe_bool, clean_text, JOURNAL_COLUMNS, SETTINGS_COLUMNS; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add utils.py
git commit -m "feat: enhance utils.py with coerce_numeric, shared helpers, type hints, and bug fixes"
```

---

### Task 3: Initialize missing CSV files in planner21.py

**Files:**
- Modify: `planner21.py:17-56`

- [ ] **Step 1: Add exercise.csv and journal.csv initialization**

After the existing file setup section (around line 56), add:

```python
EXERCISE_FILE = os.path.join(DATA_FOLDER, "exercise.csv")
EXERCISE_COLS = ["date", "status", "type", "duration", "km", "pace", "notes"]
if not os.path.exists(EXERCISE_FILE):
    pd.DataFrame(columns=EXERCISE_COLS).to_csv(EXERCISE_FILE, index=False)

JOURNAL_FILE = os.path.join(DATA_FOLDER, "journal.csv")
JOURNAL_COLS = ["date", "entry"]
if not os.path.exists(JOURNAL_FILE):
    pd.DataFrame(columns=JOURNAL_COLS).to_csv(JOURNAL_FILE, index=False)
```

- [ ] **Step 2: Verify by deleting exercise.csv and running the app**

Run: `cd /c/Users/ryana/OneDrive/Desktop/Ultraman21 && python -c "import planner21" 2>&1 | head -5`
Expected: No FileNotFoundError.

- [ ] **Step 3: Commit**

```bash
git add planner21.py
git commit -m "fix: initialize exercise.csv and journal.csv on first run"
```

---

### Task 4: Update pages to import shared helpers from utils.py

**Files:**
- Modify: `pages/dashboard.py`
- Modify: `pages/finance.py`
- Modify: `pages/driving.py`
- Modify: `pages/excercise.py`
- Modify: `pages/weekly_review.py`
- Modify: `pages/history.py`
- Modify: `pages/journal.py`
- Modify: `pages/settings.py`
- Modify: `pages/insights.py`
- Modify: `pages/ai_coach.py`

For each page, the change is: replace the local `backup_csv`, `safe_float`, `safe_bool`, `clean_text` definitions with imports from utils. Keep each page's local loaders and caching intact.

- [ ] **Step 1: Update dashboard.py**

Replace lines 28-53 (safe_read_csv, safe_float, safe_bool, clean_text definitions) with:

```python
from utils import safe_float, safe_bool, clean_text, backup_csv
```

Keep `safe_read_csv` and `parse_date_column` as they are local to dashboard (dashboard adds its own caching and parse logic).

Actually — dashboard defines `safe_read_csv` which is not in utils.py. Keep that local. Only replace `safe_float`, `safe_bool`, `clean_text`.

Replace lines 38-53:
```python
# Remove safe_float, safe_bool, clean_text definitions
# Add import at top (after theme import):
from utils import safe_float, safe_bool, clean_text
```

- [ ] **Step 2: Update weekly_review.py**

Replace lines 37-45 (safe_float, safe_bool definitions) with import:

```python
from utils import safe_float, safe_bool
```

- [ ] **Step 3: Update finance.py**

Replace lines 104-117 (clean_text, safe_float definitions) with:

```python
from utils import clean_text, safe_float, backup_csv as _backup_csv
```

Then replace `backup_csv` usage with `_backup_csv`, OR just keep importing as `backup_csv` since the local one is removed:

```python
from utils import clean_text, safe_float, backup_csv
```

Remove the local `backup_csv` definition (lines 27-36).

- [ ] **Step 4: Update driving.py**

Replace the local `backup_csv` (lines 22-31) with:

```python
from utils import backup_csv
```

- [ ] **Step 5: Update excercise.py**

Replace lines 48-80 (safe_read_csv, safe_float, safe_text definitions) with:

```python
from utils import safe_float, clean_text as safe_text, backup_csv
```

Keep `safe_read_csv` local (excercise.py uses it slightly differently). Actually, the `safe_read_csv` pattern is identical — but since we're doing focused fixes, keep it local and just replace the shared ones.

Remove local `backup_csv` (lines 24-32), `safe_float` (67-73), `safe_text` (76-80).

- [ ] **Step 6: Update history.py**

Replace local `backup_csv` (lines 40-49) and `clean_text` (76-80) with:

```python
from utils import backup_csv, clean_text
```

- [ ] **Step 7: Update journal.py**

Replace local `backup_csv` (lines 22-31) with:

```python
from utils import backup_csv
```

- [ ] **Step 8: Update settings.py**

Replace local `backup_csv` (lines 49-57) and `clean_text` (81-85) with:

```python
from utils import backup_csv, clean_text
```

Remove `import shutil` and `import glob` from top-level (they're now in utils.py's backup_csv).

- [ ] **Step 9: Update insights.py**

No shared helper duplication — insights.py only duplicates `load_planner` (keeping local) and streak functions (keeping local). No changes needed.

- [ ] **Step 10: Update ai_coach.py**

Replace local `_clean_text` (lines 42-46) with:

```python
from utils import clean_text as _clean_text
```

- [ ] **Step 11: Verify all pages import correctly**

Run:
```bash
cd /c/Users/ryana/OneDrive/Desktop/Ultraman21
python -c "
import importlib, sys
sys.path.insert(0, '.')
for mod in ['pages.dashboard', 'pages.finance', 'pages.driving', 'pages.excercise', 'pages.weekly_review', 'pages.history', 'pages.journal', 'pages.settings', 'pages.insights', 'pages.ai_coach']:
    try:
        importlib.import_module(mod)
        print(f'{mod}: OK')
    except Exception as e:
        print(f'{mod}: FAIL - {e}')
"
```

Expected: All OK (some may fail due to st.set_page_config being called twice, which is fine — the import itself should not error on missing functions).

- [ ] **Step 12: Commit**

```bash
git add pages/dashboard.py pages/finance.py pages/driving.py pages/excercise.py pages/weekly_review.py pages/history.py pages/journal.py pages/settings.py pages/ai_coach.py
git commit -m "refactor: consolidate shared helpers — pages now import from utils.py"
```

---

### Task 5: Fix session state cleanup in finance.py

**Files:**
- Modify: `pages/finance.py:478-483`

- [ ] **Step 1: Clear edit_daily_index after delete**

In finance.py, after the delete button handler (around line 480-483), add session state cleanup:

```python
with c2:
    if st.button("Delete", key=f"delete_daily_{original_index}"):
        finance_df = finance_df.drop(index=original_index).reset_index(drop=True)
        save_finance(finance_df)
        st.session_state.edit_daily_index = None  # <-- ADD THIS
        st.success("Daily expense deleted.")
        st.rerun()
```

Similarly for monthly delete (around line 598-601):

```python
with m2:
    if st.button("Delete", key=f"delete_monthly_{original_index}"):
        monthly_df = monthly_df.drop(index=original_index).reset_index(drop=True)
        save_monthly(monthly_df)
        st.session_state.edit_monthly_index = None  # <-- ADD THIS
        st.success("Monthly expense deleted.")
        st.rerun()
```

- [ ] **Step 2: Commit**

```bash
git add pages/finance.py
git commit -m "fix: clear edit session state after deleting expenses in finance page"
```

---

### Task 6: Smoke test the full app

- [ ] **Step 1: Run the app and verify all pages load**

```bash
cd /c/Users/ryana/OneDrive/Desktop/Ultraman21
python -m streamlit run planner21.py
```

Visit each page in the browser and confirm no errors:
- Mission 21 (home)
- Dashboard
- Finance
- Driving
- Exercise
- Journal
- Weekly Review
- History
- Settings
- Insights
- News
- AI Coach

- [ ] **Step 2: Final commit if any fixes needed**
