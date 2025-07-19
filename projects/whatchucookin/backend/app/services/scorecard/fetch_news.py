# app/services/scorecard/fetch_news.py
import requests, re
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime, timedelta

NEG_TERMS = ["lawsuit", "probe", "investigation", "antitrust", "fine", "shutdown", "hack", "breach", "recall", "fraud"]

def fetch_news_metrics(company: str) -> dict:
    q = company.replace(" ", "+")
    url = f"https://news.google.com/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code != 200:
        return {"headline_count_30d": 0, "domain_diversity": 0, "neg_hit_count": 0}
    soup = BeautifulSoup(resp.text, "html.parser")
    articles = soup.select("article")
    titles = []
    domains = []
    for a in articles:
        h = a.select_one("h3") or a.select_one("h4")
        if not h: continue
        title = h.get_text(" ", strip=True)
        titles.append(title.lower())
        source_span = a.select_one("div span")
        if source_span:
            domains.append(source_span.text.strip().lower())
    neg_hits = sum(any(term in t for term in NEG_TERMS) for t in titles)
    return {
        "headline_count_30d": len(titles),
        "domain_diversity": len(set(domains)),
        "neg_hit_count": neg_hits
    }
