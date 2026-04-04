"""Google Sheets backend for Ultraman21.
All data (planner, driving, finance, etc.) is stored in one Google Spreadsheet,
with each data type as a separate worksheet tab.
"""

import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource
def _get_client():
    """Return authorized gspread client. Cached for the app session."""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


@st.cache_resource
def _get_spreadsheet():
    """Return the main Ultraman21 spreadsheet. Cached for the app session."""
    return _get_client().open_by_key(st.secrets["spreadsheet_id"])


def _get_worksheet(sheet_name: str):
    """Return worksheet by name, creating it if it doesn't exist yet."""
    ss = _get_spreadsheet()
    try:
        return ss.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=sheet_name, rows=5000, cols=26)
        return ws


def load_sheet(sheet_name: str, columns: list) -> pd.DataFrame:
    """Load a worksheet and return a DataFrame with the expected columns."""
    try:
        ws = _get_worksheet(sheet_name)
        data = ws.get_all_records(default_blank="")
        if not data:
            return pd.DataFrame(columns=columns)
        df = pd.DataFrame(data)
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        return df[columns]
    except Exception as e:
        st.warning(f"⚠️ Could not load sheet '{sheet_name}': {e}")
        return pd.DataFrame(columns=columns)


def save_sheet(sheet_name: str, df: pd.DataFrame, columns: list) -> None:
    """Write a DataFrame to a worksheet, replacing all existing data."""
    try:
        ws = _get_worksheet(sheet_name)
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        out = df[columns].copy().fillna("").astype(str)
        ws.clear()
        if out.empty:
            ws.update([columns])
        else:
            ws.update([columns] + out.values.tolist())
    except Exception as e:
        st.error(f"❌ Failed to save '{sheet_name}' to Google Sheets: {e}")
