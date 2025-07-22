import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List

from app.schemas import NewsItem

def fetch_news_for_company(company: str) -> List[NewsItem]:
    """
    Fetches the top ~5 news articles for a company via Google News RSS.
    """
    # Encode spaces, etc.
    query = requests.utils.quote(company)
    url = f"https://news.google.com/rss/search?q={query}"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)
    items: List[NewsItem] = []
    for element in root.findall("./channel/item")[:5]:
        title = element.findtext("title", default="")
        link  = element.findtext("link", default="")
        pub   = element.findtext("pubDate", default="")
        src_el = element.find("source")
        source = src_el.text if src_el is not None else None

        # Try to parse to ISO
        try:
            dt = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %Z")
            published_at = dt.isoformat()
        except Exception:
            published_at = pub

        items.append(
            NewsItem(
                title=title,
                url=link,
                source=source,
                published_at=published_at,
            )
        )
    return items
