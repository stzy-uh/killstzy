# app/services/financials.py
from __future__ import annotations
import math, time
from datetime import datetime, timezone
import yfinance as yf
from .tickers import resolve_ticker

# simple in-memory cache; upgrade to Redis later
_CACHE: dict[str, tuple[float, dict]] = {}
TTL_SEC = 60 * 15  # 15 min

def _cache_get(k: str):
    item = _CACHE.get(k)
    if not item:
        return None
    ts, data = item
    if time.time() - ts > TTL_SEC:
        _CACHE.pop(k, None)
        return None
    return data

def _cache_set(k: str, data: dict):
    _CACHE[k] = (time.time(), data)

def _norm(v):
    if v is None: return None
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)): return None
    try:
        return float(v)
    except Exception:
        return None

def fetch_financials(company: str) -> dict:
    ticker = resolve_ticker(company)
    base = {
        "company": company,
        "ticker": ticker,
        "price": None,
        "change_percent": None,
        "market_cap": None,
        "pe": None,
        "rev_growth_yoy": None,
        "gross_margin_pct": None,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    if not ticker:
        return base

    ck = f"fin:{ticker}"
    cached = _cache_get(ck)
    if cached:
        return cached

    try:
        t = yf.Ticker(ticker)
        fast = getattr(t, "fast_info", {}) or {}

        def fg(key):
            if isinstance(fast, dict):
                return fast.get(key)
            return getattr(fast, key, None)

        price = fg("last_price") or fg("last_price_regular") or fg("previous_close")
        prev_close = fg("previous_close") or price
        change_pct = ((price - prev_close) / prev_close) * 100 if price and prev_close else None
        market_cap = fg("market_cap")

        info = {}
        try:
            info = t.info or {}
        except Exception:
            info = {}

        pe = info.get("trailingPE") or info.get("forwardPE")

        rev_growth = info.get("revenueGrowth")  # often fraction
        if rev_growth is not None and abs(rev_growth) < 5:
            rev_growth *= 100

        gross_margin = info.get("grossMargins")
        if gross_margin is not None and gross_margin < 1:
            gross_margin *= 100

        base.update({
            "price": _norm(price),
            "change_percent": _norm(change_pct),
            "market_cap": market_cap,
            "pe": _norm(pe),
            "rev_growth_yoy": _norm(rev_growth),
            "gross_margin_pct": _norm(gross_margin),
        })

    except Exception as e:
        base["error"] = f"financial_fetch_error: {e}"

    _cache_set(ck, base)
    return base
