import streamlit as st
from datetime import datetime

import requests
from theme import inject_theme, nav_menu, page_header

st.set_page_config(page_title="News", page_icon="📰", layout="wide", initial_sidebar_state="collapsed")

# Get API key from Streamlit secrets instead of .env file
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "")

inject_theme()
nav_menu("News")


@st.cache_data(ttl=1800)
def fetch_news(query, page_size=8, category=None, country=None):
    if not NEWS_API_KEY:
        return []
    try:
        if category and country:
            url = "https://newsapi.org/v2/top-headlines"
            params = {"category": category, "country": country, "pageSize": page_size, "apiKey": NEWS_API_KEY}
        else:
            url = "https://newsapi.org/v2/everything"
            params = {"q": query, "sortBy": "publishedAt", "pageSize": page_size, "language": "en", "apiKey": NEWS_API_KEY}
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        return data.get("articles", []) if data.get("status") == "ok" else []
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


st.markdown(page_header("News", "Breaking news and topics that matter — auto-refreshes every 30 minutes."), unsafe_allow_html=True)

if not NEWS_API_KEY:
    st.warning("⚠️ No News API key found. Add it to your Streamlit secrets:")
    st.code('[secrets]\nNEWS_API_KEY = "your_key_here"')
    st.info("Get a free key at https://newsapi.org/register (100 requests/day)")
else:
    col_refresh = st.columns([4, 1])
    with col_refresh[1]:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown('<div class="section-label">🌍 Breaking World News</div>', unsafe_allow_html=True)
    render_articles(fetch_news(query=None, page_size=6, category="general", country="us"), "No breaking news available.")

    st.markdown('<div class="section-label">🚀 Elon Musk</div>', unsafe_allow_html=True)
    render_articles(fetch_news("Elon Musk", page_size=5), "No Elon Musk news found.")

    st.markdown('<div class="section-label">🇺🇸 Trump / US Politics</div>', unsafe_allow_html=True)
    render_articles(fetch_news("Trump OR US politics", page_size=5), "No political news found.")

    st.markdown('<div class="section-label">🤖 AI & Technology</div>', unsafe_allow_html=True)
    render_articles(fetch_news("artificial intelligence OR AI technology", page_size=5), "No AI news found.")
