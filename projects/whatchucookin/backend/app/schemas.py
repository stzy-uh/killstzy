# backend/app/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

# ---------------- Shared Request ----------------

class CompanyRequest(BaseModel):
    company: str = Field(..., min_length=1, description="Plain company name or ticker string")
    # Pydantic v2 config to allow aliases if you ever use them
    model_config = ConfigDict(populate_by_name=True)


# ---------------- Intel ----------------

class IntelResponse(BaseModel):
    company: str
    headlines: List[str] = []
    what_they_cookin: str


# ---------------- Financials ----------------

class FinancialsResponse(BaseModel):
    company: str
    ticker: Optional[str] = Field(None, description="Stock symbol / ticker")
    price: Optional[float] = None
    change_percent: Optional[float] = Field(None, description="Intraday % change")
    market_cap: Optional[str] = None
    pe: Optional[float] = Field(None, description="Trailing P/E ratio")
    p_s: Optional[float] = Field(None, alias="ps", description="Price-to-sales")
    p_b: Optional[float] = Field(None, alias="pb", description="Price-to-book")
    op_margin_pct: Optional[float] = Field(None, description="Operating margin %")
    net_margin_pct: Optional[float] = Field(None, description="Net margin %")
    rev_ttm: Optional[str] = Field(None, description="Revenue (TTM)")
    rev_growth_yoy: Optional[float] = None
    gross_margin_pct: Optional[float] = None
    error: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


# ---------------- Scorecard ----------------

class ScorecardScores(BaseModel):
    innovation: Optional[float] = None
    product_momentum: Optional[float] = None
    brand_clout: Optional[float] = None
    financial_quality: Optional[float] = None
    market_momentum: Optional[float] = None
    talent_demand: Optional[float] = None
    ethics_risk: Optional[float] = None

class ScorecardResponse(BaseModel):
    company: str
    composite: Optional[float]
    scores: ScorecardScores
    explanation: str
    updated_at: str


# ---------------- Jobs + Filters ----------------

class JobsFilterRequest(CompanyRequest):
    location: Optional[str] = Field(None, description="e.g. San Francisco, Remote, London")
    keywords: Optional[List[str]] = Field(None, description="List of keywords to match")
    remote: Optional[bool] = Field(None, description="Only remote roles?")

class JobsResponse(BaseModel):
    company: str
    job_count: int
    sample_keywords: List[str] = []
    locations: List[str] = []
    remote_only: bool = False
    listings: Optional[List[dict]] = None  # optional detailed job objects


# ---------------- News ----------------

class NewsItem(BaseModel):
    title: str
    url: str
    source: Optional[str] = None
    published_at: Optional[str] = None

class NewsResponse(BaseModel):
    company: str
    news: List[NewsItem]


# ---------------- Events ----------------

class EventItem(BaseModel):
    name: str
    date: str   # ISO date string, e.g. "2025-08-15"
    location: Optional[str] = None
    url: Optional[str] = None

class EventsResponse(BaseModel):
    company: str
    events: List[EventItem]
