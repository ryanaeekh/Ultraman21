import os
from datetime import datetime

import requests
import streamlit as st
from dotenv import load_dotenv
from theme import inject_theme, nav_menu, page_header

load_dotenv()

st.set_page_config(page_title="News", page_icon="📰", layout="wide", initial_sidebar_state="collapsed")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

# =========================================================
# STYLING
# =========================================================
inject_theme()
nav_menu("News")


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
st.markdown(page_header("News", "Breaking news and topics that matter — auto-refreshes every 30 minutes."), unsafe_allow_html=True)

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
