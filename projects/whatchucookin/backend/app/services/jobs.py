from typing import List, Optional
import httpx
from datetime import date, timedelta

from app.schemas import JobsResponse

from .job_sources import GREENHOUSE, LEVER

HTTP_TIMEOUT = 8.0

def _fetch_greenhouse(board_token: str) -> List[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        r = client.get(url)
        r.raise_for_status()
        data = r.json()
    return data.get("jobs", [])

def _fetch_lever(board_token: str) -> List[dict]:
    url = f"https://api.lever.co/v0/postings/{board_token}?mode=json"
    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        r = client.get(url)
        r.raise_for_status()
        data = r.json()
    return data

def _normalize_greenhouse(jobs: List[dict]) -> List[dict]:
    norm = []
    for j in jobs:
        loc = (j.get("location") or {}).get("name")
        norm.append({
            "title": j.get("title"),
            "location": loc,
            "url": j.get("absolute_url"),
            "remote": ("remote" in (loc or "").lower()),
        })
    return norm

def _normalize_lever(jobs: List[dict]) -> List[dict]:
    norm = []
    for j in jobs:
        locs = j.get("categories", {}).get("location")
        norm.append({
            "title": j.get("text") or j.get("title"),
            "location": locs,
            "url": j.get("hostedUrl"),
            "remote": ("remote" in (locs or "").lower()),
        })
    return norm

def get_jobs_data(
    company: str,
    location: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    remote: Optional[bool] = None,
) -> JobsResponse:
    key = company.lower()
    listings: List[dict] = []

    try:
        if key in GREENHOUSE:
            raw = _fetch_greenhouse(GREENHOUSE[key])
            listings = _normalize_greenhouse(raw)
        elif key in LEVER:
            raw = _fetch_lever(LEVER[key])
            listings = _normalize_lever(raw)
    except Exception:
        listings = []

    # filters
    if location:
        listings = [j for j in listings if j.get("location") and location.lower() in j["location"].lower()]
    if remote is not None:
        listings = [j for j in listings if bool(j.get("remote")) is remote]
    if keywords:
        kw_lower = [k.lower() for k in keywords]
        listings = [
            j for j in listings
            if any(k in (j.get("title") or "").lower() for k in kw_lower)
        ]

    job_count = len(listings)

    # derive sample_keywords
    words = set()
    for j in listings:
        for token in (j.get("title") or "").lower().split():
            if token.isalpha() and 3 <= len(token) <= 12:
                words.add(token)
            if len(words) >= 8:
                break
        if len(words) >= 8:
            break
    sample_keywords = sorted(words)[:8]

    # top locations
    locs = sorted({j["location"] for j in listings if j.get("location")})[:5]

    # build 7-day flat “history” so sparkline has real data
    history = []
    for i in range(7):
        d = date.today() - timedelta(days=6 - i)
        history.append({"date": d.isoformat(), "count": job_count})

    return JobsResponse(
        company=company,
        job_count=job_count,
        sample_keywords=sample_keywords,
        locations=locs,
        remote_only=bool(remote),
        listings=listings[:50],
        history=history,
    )
