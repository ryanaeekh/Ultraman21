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


# =========================================================
# FILE / CSV HELPERS
# =========================================================
def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def ensure_csv(file_path: Path, columns: list):
    ensure_data_dir()
    if not file_path.exists():
        pd.DataFrame(columns=columns).to_csv(file_path, index=False)


def load_csv(file_path: Path, columns: list) -> pd.DataFrame:
    ensure_csv(file_path, columns)
    try:
        df = pd.read_csv(file_path)
    except Exception:
        df = pd.DataFrame(columns=columns)

    for col in columns:
        if col not in df.columns:
            df[col] = ""

    return df[columns]


def save_csv(df: pd.DataFrame, file_path: Path, columns: list):
    ensure_csv(file_path, columns)
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    df[columns].to_csv(file_path, index=False)


# =========================================================
# SPECIFIC LOADERS
# =========================================================
def load_planner() -> pd.DataFrame:
    df = load_csv(PLANNER_FILE, PLANNER_COLUMNS)
    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)
    for col in ["focus_done", "run_done", "income_done"]:
        df[col] = df[col].apply(lambda v: str(v).strip().lower() == "true")
    return df


def load_driving() -> pd.DataFrame:
    df = load_csv(DRIVING_FILE, DRIVING_COLUMNS)
    df["earnings"]     = pd.to_numeric(df["earnings"],     errors="coerce").fillna(0.0)
    df["hours_driven"] = pd.to_numeric(df["hours_driven"], errors="coerce").fillna(0.0)
    df["hourly_rate"]  = pd.to_numeric(df["hourly_rate"],  errors="coerce").fillna(0.0)
    return df


def load_finance() -> pd.DataFrame:
    df = load_csv(FINANCE_FILE, FINANCE_COLUMNS)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    return df


def load_monthly_expenses() -> pd.DataFrame:
    df = load_csv(MONTHLY_EXPENSES_FILE, MONTHLY_EXPENSES_COLUMNS)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    return df


def load_exercise() -> pd.DataFrame:
    df = load_csv(EXERCISE_FILE, EXERCISE_COLUMNS)
    df["duration"] = pd.to_numeric(df["duration"], errors="coerce").fillna(0.0)
    df["km"]       = pd.to_numeric(df["km"],       errors="coerce").fillna(0.0)
    return df


# =========================================================
# DATE HELPERS
# =========================================================
def normalize_date_column(df: pd.DataFrame, col="date") -> pd.DataFrame:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    return df


def month_days(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def filter_by_month(df: pd.DataFrame, year: int, month: int, date_col="date") -> pd.DataFrame:
    if df.empty or date_col not in df.columns:
        return df.iloc[0:0]
    temp = normalize_date_column(df.copy(), date_col).dropna(subset=[date_col])
    return temp[temp[date_col].apply(lambda d: d.year == year and d.month == month)]


def filter_by_exact_date(df: pd.DataFrame, selected_date, date_col="date") -> pd.DataFrame:
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


def get_monthly_recurring_expenses(year: int, month: int) -> float:
    return float(load_monthly_expenses()["amount"].sum())


def get_monthly_recurring_daily_share(year: int, month: int) -> float:
    total = get_monthly_recurring_expenses(year, month)
    days  = month_days(year, month)
    return float(total / days) if days > 0 else 0.0


def get_total_month_expense_with_recurring(year: int, month: int) -> float:
    return float(get_monthly_daily_expenses(year, month) + get_monthly_recurring_expenses(year, month))


def get_day_total_expense(selected_date) -> float:
    if isinstance(selected_date, str):
        selected_date = pd.to_datetime(selected_date, errors="coerce")
        if pd.isna(selected_date):
            return 0.0
        selected_date = selected_date.date()

    daily_expense   = float(filter_by_exact_date(load_finance(), selected_date)["amount"].sum())
    recurring_total = float(load_monthly_expenses()["amount"].sum())
    daily_share     = recurring_total / month_days(selected_date.year, selected_date.month)
    return float(daily_expense + daily_share)


def get_monthly_score_average(year: int, month: int) -> float:
    df = filter_by_month(load_planner(), year, month)
    return float(df["score"].mean()) if not df.empty else 0.0
