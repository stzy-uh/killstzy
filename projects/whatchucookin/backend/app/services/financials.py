# backend/app/services/financials.py

import time
import yfinance as yf
from typing import Any, Dict, Optional

def _humanize_number(n: Optional[float]) -> Optional[str]:
    if n is None:
        return None
    m = float(n)
    for unit in ("", "K", "M", "B", "T"):
        if abs(m) < 1_000.0:
            return f"{m:,.2f}{unit}"
        m /= 1_000.0
    return f"{m:.2f}P"

def get_financials_data(company: str) -> Dict[str, Any]:
    """
    Returns FinancialsResponse-compatible dict with:
      - ticker, price, change%, market_cap
      - pe, p/s, p/b
      - op_margin_pct, net_margin_pct
      - rev_ttm (humanized), rev_growth_yoy, gross_margin_pct
    """
    time.sleep(0.1)  # prevent burst
    tk = yf.Ticker(company)
    info: Dict[str, Any] = tk.info or {}

    # Basic quote data
    price = info.get("regularMarketPrice")
    change_pct = info.get("regularMarketChangePercent")
    ticker = info.get("symbol", company).upper()

    # Ratios & margins
    market_cap = _humanize_number(info.get("marketCap"))
    pe       = info.get("trailingPE")
    p_s      = info.get("priceToSalesTrailing12Months")
    p_b      = info.get("priceToBook")
    opm      = info.get("operatingMargins")
    npm      = info.get("profitMargins")

    # Revenue TTM & growth
    rev_ttm_raw = info.get("totalRevenue")
    rev_ttm     = _humanize_number(rev_ttm_raw)
    # YoY growth from last year to this
    rev_growth  = None
    try:
        hist_rev = tk.financials.loc["Total Revenue"]
        if len(hist_rev) >= 2 and hist_rev.iloc[1] != 0:
            rev_growth = (hist_rev.iloc[0] - hist_rev.iloc[1]) / hist_rev.iloc[1] * 100
    except Exception:
        pass

    # Gross margin
    gross_margin = None
    try:
        hist_gross = tk.financials.loc["Gross Profit"]
        if rev_ttm_raw and rev_ttm_raw != 0:
            gross_margin = hist_gross.iloc[0] / rev_ttm_raw * 100
    except Exception:
        pass

    return {
        "company": company,
        "ticker": ticker,
        "price": price,
        "change_percent": change_pct,
        "market_cap": market_cap,
        "pe": pe,
        "ps": p_s,
        "pb": p_b,
        "op_margin_pct": (opm * 100) if opm is not None else None,
        "net_margin_pct": (npm * 100) if npm is not None else None,
        "rev_ttm": rev_ttm,
        "rev_growth_yoy": rev_growth,
        "gross_margin_pct": gross_margin,
        "error": None,
    }
