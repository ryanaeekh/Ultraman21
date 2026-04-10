"""Utility functions for Ultraman21.
Data is stored in Google Sheets (via gsheets.py) instead of local CSV files.
All other logic (helpers, loaders, calculations) remains the same.
"""

from pathlib import Path
import pandas as pd
import calendar
from datetime import datetime

from gsheets import load_sheet, save_sheet


# =========================================================
# FILE PATH CONSTANTS  (kept for compatibility — stems used as sheet names)
# =========================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

PLANNER_FILE          = DATA_DIR / "planner.csv"
DRIVING_FILE          = DATA_DIR / "driving.csv"
FINANCE_FILE          = DATA_DIR / "finance.csv"
MONTHLY_EXPENSES_FILE = DATA_DIR / "monthly_expenses.csv"
EXERCISE_FILE         = DATA_DIR / "exercise.csv"
JOURNAL_FILE          = DATA_DIR / "journal.csv"
SETTINGS_FILE         = DATA_DIR / "settings.csv"


# =========================================================
# EXPECTED COLUMNS
# =========================================================
PLANNER_COLUMNS = [
    "date", "priority_1", "priority_2", "priority_3",
    "focus_done", "run_done", "income_done", "reflection", "score",
]

DRIVING_COLUMNS = [
    "date", "day_type", "start_time", "end_time",
    "hours_driven", "earnings", "hourly_rate", "target_status",
]

FINANCE_COLUMNS = ["date", "category", "amount"]

MONTHLY_EXPENSES_COLUMNS = ["name", "amount"]

EXERCISE_COLUMNS = ["date", "status", "type", "duration", "km", "pace", "notes"]

JOURNAL_COLUMNS = ["date", "entry"]

SETTINGS_COLUMNS = [
    "long_term_goals", "daily_income_target", "hourly_rate_target",
    "daily_budget", "monthly_budget", "checklist_items", "expense_categories",
]


# =========================================================
# SHEET NAME HELPER
# =========================================================
def _sheet_name(file_path) -> str:
    """Convert any file path (str or Path) to a Google Sheets worksheet name."""
    return Path(file_path).stem


# =========================================================
# CORE CSV-COMPATIBLE API  (now backed by Google Sheets)
# =========================================================
def ensure_data_dir() -> None:
    """No-op — Google Sheets needs no local directory."""
    pass


def ensure_csv(file_path, columns: list) -> None:
    """No-op — Google Sheets creates worksheets on demand."""
    pass


def load_csv(file_path, columns: list) -> pd.DataFrame:
    """Load data from the Google Sheet worksheet matching file_path's stem."""
    return load_sheet(_sheet_name(file_path), columns)


def save_csv(df: pd.DataFrame, file_path, columns: list) -> None:
    """Save data to the Google Sheet worksheet matching file_path's stem."""
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    save_sheet(_sheet_name(file_path), df[columns], columns)


def backup_csv(filepath) -> None:
    """No-op — Google Sheets has built-in version history."""
    pass


def coerce_numeric(df: pd.DataFrame, columns: list, fill: float = 0.0) -> pd.DataFrame:
    """Convert columns to numeric, filling NaN with *fill*."""
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(fill)
    return df


# =========================================================
# COMMON HELPERS
# =========================================================
def safe_float(value) -> float:
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def safe_bool(value) -> bool:
    return str(value).strip().lower() == "true"


def clean_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


# =========================================================
# SPECIFIC LOADERS
# =========================================================
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


def load_journal() -> pd.DataFrame:
    return load_csv(JOURNAL_FILE, JOURNAL_COLUMNS)


def load_settings() -> pd.DataFrame:
    return load_csv(SETTINGS_FILE, SETTINGS_COLUMNS)


# =========================================================
# SPECIFIC SAVERS  (convenience wrappers)
# =========================================================
def save_planner_df(df: pd.DataFrame) -> None:
    save_csv(df, PLANNER_FILE, PLANNER_COLUMNS)


def save_driving_df(df: pd.DataFrame) -> None:
    save_csv(df, DRIVING_FILE, DRIVING_COLUMNS)


def save_finance_df(df: pd.DataFrame) -> None:
    save_csv(df, FINANCE_FILE, FINANCE_COLUMNS)


def save_monthly_expenses_df(df: pd.DataFrame) -> None:
    save_csv(df, MONTHLY_EXPENSES_FILE, MONTHLY_EXPENSES_COLUMNS)


def save_exercise_df(df: pd.DataFrame) -> None:
    save_csv(df, EXERCISE_FILE, EXERCISE_COLUMNS)


def save_journal_df(df: pd.DataFrame) -> None:
    save_csv(df, JOURNAL_FILE, JOURNAL_COLUMNS)


def save_settings_df(df: pd.DataFrame) -> None:
    save_csv(df, SETTINGS_FILE, SETTINGS_COLUMNS)


# =========================================================
# DATE HELPERS
# =========================================================
def normalize_date_column(df: pd.DataFrame, col: str = "date") -> pd.DataFrame:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    return df


def month_days(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def filter_by_month(df: pd.DataFrame, year: int, month: int, date_col: str = "date") -> pd.DataFrame:
    if df.empty or date_col not in df.columns:
        return df.iloc[0:0]
    temp = normalize_date_column(df.copy(), date_col).dropna(subset=[date_col])
    return temp[temp[date_col].apply(lambda d: d.year == year and d.month == month)]


def filter_by_exact_date(df: pd.DataFrame, selected_date, date_col: str = "date") -> pd.DataFrame:
    if df.empty or date_col not in df.columns:
        return df.iloc[0:0]
    temp = normalize_date_column(df.copy(), date_col).dropna(subset=[date_col])
    if isinstance(selected_date, str):
        selected_date = pd.to_datetime(selected_date, errors="coerce")
        if pd.isna(selected_date):
            return temp.iloc[0:0]
        selected_date = selected_date.date()
    return temp[temp[date_col] == selected_date]


# =========================================================
# SHARED CALCULATIONS
# =========================================================
def get_monthly_driving_income(year: int, month: int) -> float:
    df = filter_by_month(load_driving(), year, month)
    return float(df["earnings"].sum())


def get_monthly_daily_expenses(year: int, month: int) -> float:
    df = filter_by_month(load_finance(), year, month)
    return float(df["amount"].sum())


def get_monthly_recurring_expenses() -> float:
    return float(load_monthly_expenses()["amount"].sum())


def get_monthly_recurring_daily_share(year: int, month: int) -> float:
    total = get_monthly_recurring_expenses()
    days  = month_days(year, month)
    return float(total / days) if days > 0 else 0.0


def get_total_month_expense_with_recurring(year: int, month: int) -> float:
    return float(get_monthly_daily_expenses(year, month) + get_monthly_recurring_expenses())


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


def get_monthly_score_average(year: int, month: int) -> float:
    df = filter_by_month(load_planner(), year, month)
    return float(df["score"].mean()) if not df.empty else 0.0
