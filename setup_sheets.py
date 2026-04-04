"""Run this once to add headers to all Google Sheets tabs.
Run from your Ultraman21 main folder:
    python setup_sheets.py
"""

import json
import gspread
from google.oauth2.service_account import Credentials

# ── Paste your spreadsheet ID here ──────────────────────────────────
SPREADSHEET_ID = "1lkK3NuFa6-YiAsUl_KjZw0idaF6gOLQh0L-Jc10WGrk"

# ── Paste your service account JSON file path here ──────────────────
# e.g. "C:/Users/ryana/Downloads/authentic-realm-492315-p7-xxxx.json"
SERVICE_ACCOUNT_FILE = "YOUR_JSON_FILE_PATH_HERE"

# ── Sheet headers ────────────────────────────────────────────────────
SHEETS = {
    "planner": ["date", "priority_1", "priority_2", "priority_3", "focus_done", "run_done", "income_done", "reflection", "score"],
    "driving": ["date", "day_type", "start_time", "end_time", "hours_driven", "earnings", "hourly_rate", "target_status"],
    "finance": ["date", "category", "amount"],
    "monthly_expenses": ["name", "amount"],
    "exercise": ["date", "status", "type", "duration", "km", "pace", "notes"],
    "journal": ["date", "entry"],
    "settings": ["long_term_goals", "daily_income_target", "hourly_rate_target", "daily_budget", "monthly_budget", "checklist_items", "expense_categories"],
}

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def main():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    ss = client.open_by_key(SPREADSHEET_ID)

    existing = {ws.title: ws for ws in ss.worksheets()}

    for sheet_name, headers in SHEETS.items():
        if sheet_name in existing:
            ws = existing[sheet_name]
            print(f"✅ Found '{sheet_name}' — adding headers...")
        else:
            ws = ss.add_worksheet(title=sheet_name, rows=1000, cols=26)
            print(f"➕ Created '{sheet_name}' — adding headers...")

        ws.clear()
        ws.update([headers])
        print(f"   Headers set: {headers}")

    print("\n🎉 All sheets set up! Refresh your Streamlit app.")

if __name__ == "__main__":
    main()
