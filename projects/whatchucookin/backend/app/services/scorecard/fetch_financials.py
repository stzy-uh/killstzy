# app/services/scorecard/fetch_financials.py
import yfinance as yf
import math

def fetch_financial_metrics(ticker: str) -> dict:
    try:
        tk = yf.Ticker(ticker)
        info = tk.info  # may be slow; consider selective attributes
        hist = tk.history(period="2mo", interval="1d")
        price_return_30d = 0.0
        if len(hist) > 22:
            recent_close = hist["Close"].iloc[-1]
            past_close = hist["Close"].iloc[-22]
            price_return_30d = ((recent_close - past_close) / past_close) * 100
        # Financial statements
        fin = tk.financials  # DataFrame (columns = periods)
        rev_growth_yoy = None
        if fin is not None and "Total Revenue" in fin.index and fin.shape[1] >= 2:
            rev_latest = fin.loc["Total Revenue"].iloc[0]
            rev_prev = fin.loc["Total Revenue"].iloc[1]
            if rev_prev:
                rev_growth_yoy = (rev_latest - rev_prev) / rev_prev * 100
        gross_margin = info.get("grossMargins")
        pe = info.get("trailingPE")
        return {
            "price_return_30d": price_return_30d,
            "rev_growth_yoy": rev_growth_yoy if rev_growth_yoy is not None else 0.0,
            "gross_margin_pct": (gross_margin * 100) if gross_margin else None,
            "pe": pe if pe and not math.isinf(pe) else None
        }
    except Exception:
        return {
            "price_return_30d": 0.0,
            "rev_growth_yoy": 0.0,
            "gross_margin_pct": None,
            "pe": None
        }
