# app/services/scorecard/pipeline.py
from __future__ import annotations
import datetime as dt
from typing import Any, Dict, Optional

# Import the scoring function
from .scoring import compute_scores

# ------------------------------------------------------------------
# 1. Fetch Layer (replace these stubs with real data collectors)
# ------------------------------------------------------------------

def fetch_financials(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Replace with yfinance or other source.
    Expected keys (optional):
      price, change_percent, market_cap, pe, rev_growth_yoy, gross_margin_pct
    """
    try:
        import yfinance as yf  # make sure numpy/pandas resolved
        t = yf.Ticker(ticker)
        info = t.fast_info if hasattr(t, "fast_info") else {}
        price = getattr(t, "history")(period="1d")["Close"].iloc[-1] if hasattr(t, "history") else None
        change_percent = info.get("regularMarketChangePercent")
        market_cap = info.get("marketCap")
        # Basic financial derivations (add real parsing later)
        pe = info.get("trailingPe") or info.get("peRatio")
        # Placeholders for revenue growth & gross margin if not easily fetched:
        rev_growth_yoy = None
        gross_margin_pct = None
        return {
            "price": price,
            "change_percent": change_percent,
            "market_cap": market_cap,
            "pe": pe,
            "rev_growth_yoy": rev_growth_yoy,
            "gross_margin_pct": gross_margin_pct
        }
    except Exception:
        return None


def fetch_news_metrics(company: str) -> Optional[Dict[str, Any]]:
    """
    Should return something like:
      { 'headline_count_30d': int, 'recent_headlines': [ {title, ts}, ... ] }
    """
    # TODO: integrate your actual scraping pipeline. Stub:
    return None


def fetch_jobs(company: str) -> Optional[Dict[str, Any]]:
    """
    Should return:
      { 'job_count': int, 'sample_keywords': ['ai','sales',...], ... }
    """
    # TODO: integrate careers page parser.
    return None


def fetch_github(company: str) -> Optional[Dict[str, Any]]:
    """
    Map company -> org(s). Collect commits/stars last 30d.
    Return:
      { 'commits_last30': int, 'stars_last30': int }
    """
    # TODO: implement GitHub API queries w/ caching.
    return None


def fetch_brand_sentiment(company: str) -> Optional[Dict[str, Any]]:
    """
    Optional: sentiment score, social mention volume, etc.
    """
    return None


# ------------------------------------------------------------------
# 2. Ticker / Company Mapping
# ------------------------------------------------------------------

COMPANY_MAP = {
    # Extend this map as needed
    "nvidia": {"ticker": "NVDA"},
    "nvda": {"ticker": "NVDA"},
    "microsoft": {"ticker": "MSFT"},
    "msft": {"ticker": "MSFT"},
    "apple": {"ticker": "AAPL"},
    "aapl": {"ticker": "AAPL"},
    "puma": {"ticker": "PUM.DE"},    # alt: "PUMSY" (ADR) if needed
    "pum": {"ticker": "PUM.DE"},
    "puma se": {"ticker": "PUM.DE"},
    "tesla": {"ticker": "TSLA"},
    "tsla": {"ticker": "TSLA"},
}

def resolve_ticker(company: str) -> Optional[str]:
    key = company.lower().strip()
    if key in COMPANY_MAP:
        return COMPANY_MAP[key]["ticker"]
    # naive fallback: assume user passed a ticker already
    if key.isalpha() and 1 < len(key) <= 6:
        return key.upper()
    return None


# ------------------------------------------------------------------
# 3. Explanation Builder (Optional AI Summary)
# ------------------------------------------------------------------

def build_explanation(company: str, subs: Dict[str, Optional[float]], composite: Optional[float], meta: Dict[str, Any]) -> str:
    """
    Lightweight text synthesis without calling an LLM yet.
    You can replace with an OpenAI call for richer narrative.
    """
    coverage = meta.get("coverage", 0)
    missing_keys = [k for k, m in meta.get("missing", {}).items() if m]
    pieces = []
    if composite is not None:
        pieces.append(f"Composite {composite:.1f} with {int(coverage*100)}% data coverage.")
    else:
        pieces.append("Composite unavailable (insufficient data).")

    def slot(label, key):
        v = subs.get(key)
        if v is not None:
            pieces.append(f"{label} {v:.0f}")
    slot("Innovation", "innovation")
    slot("Product momentum", "product_momentum")
    slot("Financial quality", "financial_quality")
    slot("Brand clout", "brand_clout")
    slot("Market momentum", "market_momentum")
    slot("Talent demand", "talent_demand")
    slot("Ethics/risk", "ethics_risk")

    if missing_keys:
        pieces.append(f"Missing: {', '.join(missing_keys)}")
    return f"{company.title()}: " + " | ".join(pieces)


# ------------------------------------------------------------------
# 4. Public Pipeline Function
# ------------------------------------------------------------------

def build_scorecard(company: str) -> Dict[str, Any]:
    """
    Orchestrates the entire scorecard build.
    """
    ticker = resolve_ticker(company) or company.upper()

    financials = fetch_financials(ticker)
    news = fetch_news_metrics(company)
    jobs = fetch_jobs(company)
    github = fetch_github(company)
    sentiment = fetch_brand_sentiment(company)

    raw = {
        "company": company,
        "ticker": ticker,
        "financials": financials,
        "news": news,
        "jobs": jobs,
        "github": github,
        "sentiment": sentiment
    }

    subs, composite, meta = compute_scores(raw)

    explanation = build_explanation(company, subs, composite, meta)

    return {
        "company": company.lower(),
        "ticker": ticker,
        "timestamp": dt.datetime.utcnow().isoformat() + "Z",
        "scores": subs,
        "composite": composite,
        "meta": meta,
        "explanation": explanation,
        "raw": {
            # Keep raw light; remove if sensitive
            "financials_present": financials is not None,
            "news_present": news is not None,
            "jobs_present": jobs is not None,
            "github_present": github is not None,
            "sentiment_present": sentiment is not None,
        }
    }


# ------------------------------------------------------------------
# 5. FastAPI Integration Helper
# ------------------------------------------------------------------

def get_scorecard_response(company: str) -> Dict[str, Any]:
    """
    Thin wrapper for routers to call.
    """
    return build_scorecard(company)
# app/services/scorecard/pipeline.py
from datetime import datetime

def get_scorecard_stub(company: str):
    score = hash(company.lower()) % 41 + 50  # pseudo-stable 50–90
    return {
        "company": company,
        "composite": score,
        "scores": {
            "innovation": score - 4,
            "product_momentum": score - 6,
            "brand_clout": score + 3,
            "financial_quality": score - 2,
            "market_momentum": score - 8,
            "talent_demand": score - 10,
            "ethics_risk": max(30, score - 12)
        },
        "explanation": f"{company} composite {score}: solid core metrics with room in momentum & talent acquisition.",
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
