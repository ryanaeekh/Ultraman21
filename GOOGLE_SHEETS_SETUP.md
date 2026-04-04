# Google Sheets Setup Guide for Ultraman21

Follow these steps **once** to connect your app to Google Sheets.
After setup, all your data saves permanently and is accessible from any device.

---

## Step 1 — Create a Google Spreadsheet

1. Go to https://sheets.google.com
2. Click **+ New spreadsheet**
3. Name it: `Ultraman21`
4. Copy the spreadsheet ID from the URL:
   - URL looks like: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
   - Copy the long string between `/d/` and `/edit`
   - Save it — you'll need it in Step 4

---

## Step 2 — Create a Google Cloud Service Account

1. Go to https://console.cloud.google.com
2. Create a new project (or select an existing one)
3. In the search bar, search for **"Google Sheets API"** → Enable it
4. Also enable **"Google Drive API"**
5. Go to **APIs & Services → Credentials**
6. Click **"+ Create Credentials" → Service Account**
7. Give it any name (e.g. `ultraman21-bot`) → Click **Create**
8. Skip optional steps → Click **Done**
9. Click on your new service account → Go to **Keys** tab
10. Click **Add Key → Create new key → JSON** → Download the file

---

## Step 3 — Share Your Spreadsheet with the Service Account

1. Open the JSON key file you downloaded
2. Find the `client_email` field — it looks like:
   `ultraman21-bot@your-project.iam.gserviceaccount.com`
3. Open your `Ultraman21` Google Spreadsheet
4. Click **Share** (top right)
5. Paste the `client_email` address and give it **Editor** access
6. Click **Send**

---

## Step 4 — Add Secrets to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Open your Ultraman21 app → Click **"⋮" (three dots) → Settings**
3. Click **"Secrets"** tab
4. Paste the following, replacing with your actual values:

```toml
spreadsheet_id = "YOUR_SPREADSHEET_ID_FROM_STEP_1"

NEWS_API_KEY = "your_newsapi_key_here"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN RSA PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END RSA PRIVATE KEY-----\n"
client_email = "ultraman21-bot@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email"
```

> **Tip:** Copy the values from the JSON file you downloaded in Step 2.
> The `private_key` field must keep the `\n` characters intact.

---

## Step 5 — Replace Files in VS Code

Copy these updated files into your Ultraman21 project folder, replacing the originals:

- `gsheets.py` ← NEW file (add this)
- `utils.py`
- `planner21.py`
- `driving.py`
- `excercise.py`
- `finance.py`
- `journal.py`
- `settings.py`
- `dashboard.py`
- `history.py`
- `insights.py`
- `weekly_review.py`
- `news.py`
- `requirements.txt`

---

## Step 6 — Push to GitHub and Deploy

In your VS Code terminal:
```bash
git add .
git commit -m "feat: Google Sheets data backend"
git push
```

Streamlit Cloud will automatically redeploy. 

---

## How It Works After Setup

| Action | Where data goes |
|---|---|
| You save a planner entry | Google Sheets "planner" tab |
| You log a driving session | Google Sheets "driving" tab |
| You log an expense | Google Sheets "finance" tab |
| You write a journal entry | Google Sheets "journal" tab |

- Data is **permanent** — never lost when the app restarts
- You can **view and edit** your data directly in Google Sheets
- Works on **phone, tablet, and desktop** — any browser
- Google Sheets keeps **version history** — you can restore old data anytime

---

## Troubleshooting

**"Could not load sheet" warning:**
- Make sure you shared the spreadsheet with the service account email
- Double-check the `spreadsheet_id` in Secrets

**"Failed to save" error:**
- Check that Google Sheets API and Google Drive API are both enabled
- Make sure the service account has Editor access to the spreadsheet

**Data looks empty after deploying:**
- The first time you use the app, sheets will be created automatically
- Just start entering data normally
