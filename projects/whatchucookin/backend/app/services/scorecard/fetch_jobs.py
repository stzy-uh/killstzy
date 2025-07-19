# app/services/scorecard/fetch_jobs.py
import re, requests

ROLE_TERMS = ["engineer", "data", "product", "designer", "manager", "scientist"]

def fetch_job_count(careers_url: str) -> int:
    if not careers_url:
        return 0
    try:
        html = requests.get(careers_url, timeout=10).text.lower()
        # crude: count terms occurrences (de-duplicated lines)
        lines = set(l.strip() for l in html.splitlines() if any(t in l for t in ROLE_TERMS))
        return min(len(lines), 200)  # cap so insane pages don't blow up
    except:
        return 0
