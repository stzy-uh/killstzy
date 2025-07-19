# app/services/tickers.py

TICKER_MAP = {
    "nvidia": "NVDA", "nvda": "NVDA",
    "microsoft": "MSFT", "msft": "MSFT",
    "apple": "AAPL", "aapl": "AAPL",
    "google": "GOOGL", "alphabet": "GOOGL", "googl": "GOOGL",
    "meta": "META", "facebook": "META",
    "amazon": "AMZN", "amzn": "AMZN",
    "tesla": "TSLA", "tsla": "TSLA",
    "netflix": "NFLX",
    "nike": "NKE",
    "puma": "PUM.DE",
    "adidas": "ADS.DE"
    # add more as needed
}

def resolve_ticker(company: str) -> str | None:
    if not company:
        return None
    return TICKER_MAP.get(company.lower().strip())
