import re

def normalize_ticker(name: str) -> str:
    """
    Very naive normalization:
    - If input looks like a ticker (1–5 letters, maybe a dot), return upper.
    - Otherwise attempt some simple map (add more as needed).
    """
    s = name.strip()
    if re.fullmatch(r"[A-Za-z\.]{1,6}", s):
        return s.upper()

    mapping = {
        "apple": "AAPL",
        "microsoft": "MSFT",
        "google": "GOOGL",
        "alphabet": "GOOGL",
        "amazon": "AMZN",
        "meta": "META",
        "facebook": "META",
        "tesla": "TSLA",
        "nvidia": "NVDA",
        "netflix": "NFLX",
        "puma": "PUM.DE",
    }
    return mapping.get(s.lower(), s.upper())
