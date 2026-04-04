from pathlib import Path
import pandas as pd
import calendar
from datetime import datetime

# =========================================================
# BASE PATHS
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
# EXPECTED COLUMNS  (must match what each page actually writes)
# =========================================================
PLANNER_COLUMNS = [
    "date",
    "priority_1",
    "priority_2",
    "priority_3",
    "focus_done",
    "run_done",
    "income_done",
    "reflection",
    "score",
]

DRIVING_COLUMNS = [
    "date",
    "day_type",
    "start_time",
    "end_time",
    "hours_driven",
    "earnings",
    "hourly_rate",
    "target_status",
]

FINANCE_COLUMNS = [
    "date",
    "category",
    "amount",
]

MONTHLY_EXPENSES_COLUMNS = [
    "name",
    "amount",
]

EXERCISE_COLUMNS = [
    "date",
    "status",
    "type",
    "duration",
    "km",
    "pace",
    "notes",
]

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


# =========================================================
# FILE / CSV HELPERS
# =========================================================
def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def ensure_csv(file_path: Path, columns: list[str]) -> None:
    ensure_data_dir()
    if not file_path.exists():
        pd.DataFrame(columns=columns).to_csv(file_path, index=False)


def load_csv(file_path: Path, columns: list[str]) -> pd.DataFrame:
    ensure_csv(file_path, columns)
    try:
        df = pd.read_csv(file_path)
    except Exception:
        df = pd.DataFrame(columns=columns)

    for col in columns:
        if col not in df.columns:
            df[col] = ""

    return df[columns]


def save_csv(df: pd.DataFrame, file_path: Path, columns: list[str]) -> None:
    ensure_csv(file_path, columns)
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    df[columns].to_csv(file_path, index=False)


def coerce_numeric(df: pd.DataFrame, columns: list[str], fill: float = 0.0) -> pd.DataFrame:
    """Convert columns to numeric, filling NaN with *fill*."""
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(fill)
    return df


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
