# backend/app/services/events.py

import os
from datetime import date, timedelta
from typing import List

import httpx
from app.schemas import EventItem

# --- configure your Finnhub key ---
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
if not FINNHUB_API_KEY:
    raise RuntimeError("Please set the FINNHUB_API_KEY environment variable")

def fetch_events_for_company(company: str) -> List[EventItem]:
    """
    Fetch upcoming earnings dates for `company` (ticker) from Finnhub.
    Returns a list of EventItem(name, date, location, url).
    """
    # Build a 90-day window
    today = date.today()
    to_date = today + timedelta(days=90)

    url = "https://finnhub.io/api/v1/calendar/earnings"
    params = {
        "symbol": company.upper(),
        "from": today.isoformat(),
        "to": to_date.isoformat(),
        "token": FINNHUB_API_KEY,
    }

    resp = httpx.get(url, params=params, timeout=10.0)
    resp.raise_for_status()
    payload = resp.json()

    events: List[EventItem] = []
    # Finnhub returns {"earningsCalendar": [ { "date": "2025-08-01", "symbol": "AAPL", ... }, ... ]}
    for item in payload.get("earningsCalendar", []):
        ev_date = item.get("date")
        symbol = item.get("symbol", company.upper())
        events.append(
            EventItem(
                name=f"Earnings Call • {symbol}",
                date=ev_date,
                location=None,
                url=f"https://finnhub.io/calendar/earnings?symbol={symbol}"
            )
        )

    return events
