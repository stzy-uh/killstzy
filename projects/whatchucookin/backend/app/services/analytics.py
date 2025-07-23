import yfinance as yf
from app.schemas import DataAnalysisResponse, DataPoint

def get_data_analysis(company: str) -> DataAnalysisResponse:
    """
    Fetch ~1 year of daily closing prices and quarterly revenue.
    """
    ticker = yf.Ticker(company)

    # --- Price history (1 year daily) ---
    hist = ticker.history(period="1y", interval="1d")
    price_series = [
        DataPoint(timestamp=dt.isoformat(), value=float(close))
        for dt, close in zip(hist.index.to_pydatetime(), hist["Close"])
    ]

    # --- Quarterly revenue history ---
    rev_df = ticker.quarterly_financials.T  # rows are quarters
    revenue_series = []
    for idx, row in rev_df.iterrows():
        if "Total Revenue" in row:
            revenue_series.append(
                DataPoint(
                    timestamp=idx.to_pydatetime().date().isoformat(),
                    value=float(row["Total Revenue"])
                )
            )

    return DataAnalysisResponse(
        company=company,
        price_history=price_series,
        revenue_history=revenue_series,
    )
