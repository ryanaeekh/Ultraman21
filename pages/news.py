import os
from datetime import datetime

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="News", page_icon="📰", layout="wide")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

# =========================================================
# STYLING
# =========================================================
st.markdown("""
<style>
:root {
    --accent: #8a7055; --pos: #5a9a6a; --neg: #b87070;
    --border: 1px solid rgba(0,0,0,0.07); --shadow: 0 1px 3px rgba(0,0,0,0.04);
}
@media (prefers-color-scheme: dark) {
    :root { --accent: #b08a65; --border: 1px solid rgba(255,255,255,0.07); --shadow: 0 1px 3px rgba(0,0,0,0.12); --pos: #7ab88a; }
}
[data-theme="dark"] { --accent: #b08a65; --border: 1px solid rgba(255,255,255,0.07); --shadow: 0 1px 3px rgba(0,0,0,0.12); --pos: #7ab88a; }
.stDecoration { display: none !important; }
html, body, [class*="css"] { font-family: Georgia, 'Times New Roman', serif !important; }
.block-container { max-width: 1200px; padding-top: 4rem !important; padding-bottom: 4rem !important; }

.news-card {
    border: var(--border); border-radius: 18px;
    padding: 22px 28px; background: var(--secondary-background-color);
    box-shadow: var(--shadow); margin-bottom: 14px;
    transition: border-color 0.15s ease;
}
.news-card:hover { border-color: rgba(138,112,85,0.30); }
.news-source { font-size: 10px; opacity: 0.55; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 400; margin-bottom: 6px; }
.news-title { font-size: 1.1rem; font-weight: 500; line-height: 1.5; margin-bottom: 8px; }
.news-title a { color: inherit; text-decoration: none; }
.news-title a:hover { color: var(--accent); }
.news-desc { font-size: 0.92rem; opacity: 0.75; line-height: 1.7; margin-bottom: 8px; }
.news-meta { font-size: 12px; opacity: 0.45; }
.section-label {
    font-size: 10px; font-weight: 400; letter-spacing: 0.12em;
    text-transform: uppercase; opacity: 0.55; margin-bottom: 14px; margin-top: 24px;
}

div.stButton > button {
    border-radius: 12px !important; border: 1px solid rgba(0,0,0,0.14) !important;
    font-weight: 400 !important; font-family: Georgia, serif !important;
    background: var(--secondary-background-color) !important; color: inherit !important;
}
div.stButton > button:hover { border-color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
_dark = st.session_state["dark_mode"]
_bg = "#0e1117" if _dark else "#f5f0e8"
_sbg = "#161b22" if _dark else "#ede8de"
_color = "#fafafa" if _dark else "#3a3028"
st.markdown(f"""<style>
.stApp {{ background-color: {_bg} !important; color: {_color} !important; }}
section[data-testid="stSidebar"] > div:first-child {{ background-color: {_sbg} !important; }}
header[data-testid="stHeader"] {{ background-color: {_bg} !important; }}
</style>""", unsafe_allow_html=True)


# =========================================================
# NEWS FETCHER
# =========================================================
@st.cache_data(ttl=1800)
def fetch_news(query, page_size=8, category=None, country=None):
    """Fetch news from NewsAPI. Returns list of article dicts."""
    if not NEWS_API_KEY:
        return []
    try:
        if category and country:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "category": category,
                "country": country,
                "pageSize": page_size,
                "apiKey": NEWS_API_KEY,
            }
        else:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "sortBy": "publishedAt",
                "pageSize": page_size,
                "language": "en",
                "apiKey": NEWS_API_KEY,
            }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("status") == "ok":
            return data.get("articles", [])
        return []
    except Exception:
        return []


def render_articles(articles, empty_msg="No articles found."):
    if not articles:
        st.info(empty_msg)
        return
    for article in articles:
        title = article.get("title", "Untitled") or "Untitled"
        desc = article.get("description", "") or ""
        source = article.get("source", {}).get("name", "Unknown")
        url = article.get("url", "#")
        published = article.get("publishedAt", "")
        if published:
            try:
                dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                time_str = dt.strftime("%b %d, %Y %H:%M")
            except Exception:
                time_str = published[:10]
        else:
            time_str = ""

        # Truncate description
        if len(desc) > 200:
            desc = desc[:200].rsplit(" ", 1)[0] + "..."

        st.markdown(
            f'<div class="news-card">'
            f'<div class="news-source">{source}</div>'
            f'<div class="news-title"><a href="{url}" target="_blank">{title}</a></div>'
            f'<div class="news-desc">{desc}</div>'
            f'<div class="news-meta">{time_str}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# =========================================================
# PAGE
# =========================================================
st.title("📰 News")
st.markdown(
    '<div style="opacity:0.6;margin-bottom:1.4rem">Breaking news and topics that matter — auto-refreshes every 30 minutes.</div>',
    unsafe_allow_html=True,
)

if not NEWS_API_KEY:
    st.warning("⚠️ No News API key found. Add your key to the `.env` file in the project root:")
    st.code("NEWS_API_KEY=your_key_here")
    st.info("Get a free key at https://newsapi.org/register (100 requests/day)")
else:
    col_refresh = st.columns([4, 1])
    with col_refresh[1]:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ── Breaking World News ──
    st.markdown('<div class="section-label">🌍 Breaking World News</div>', unsafe_allow_html=True)
    breaking = fetch_news(query=None, page_size=6, category="general", country="us")
    render_articles(breaking, "No breaking news available.")

    # ── Elon Musk ──
    st.markdown('<div class="section-label">🚀 Elon Musk</div>', unsafe_allow_html=True)
    musk = fetch_news("Elon Musk", page_size=5)
    render_articles(musk, "No Elon Musk news found.")

    # ── Trump / US Politics ──
    st.markdown('<div class="section-label">🇺🇸 Trump / US Politics</div>', unsafe_allow_html=True)
    politics = fetch_news("Trump OR US politics", page_size=5)
    render_articles(politics, "No political news found.")

    # ── AI & Technology ──
    st.markdown('<div class="section-label">🤖 AI & Technology</div>', unsafe_allow_html=True)
    ai_news = fetch_news("artificial intelligence OR AI technology", page_size=5)
    render_articles(ai_news, "No AI news found.")
