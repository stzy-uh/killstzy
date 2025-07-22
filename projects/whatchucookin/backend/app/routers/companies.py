from fastapi import APIRouter, HTTPException
from app.schemas import (
    CompanyRequest,
    IntelResponse,
    FinancialsResponse,
    ScorecardResponse,
    JobsResponse,
    NewsResponse,
    EventsResponse,
)
from app.services.intel import get_company_intel
from app.services.financials import get_financials_data
from app.services.scorecard.pipeline import get_scorecard
from app.services.jobs import get_jobs_data
from app.services.news import fetch_news_for_company
from app.services.events import fetch_events_for_company

router = APIRouter()

@router.post("/intel", response_model=IntelResponse)
def intel(req: CompanyRequest):
    try:
        return get_company_intel(req.company)
    except Exception as e:
        raise HTTPException(500, detail=f"intel_error: {e}")

@router.post("/financials", response_model=FinancialsResponse)
def financials(req: CompanyRequest):
    try:
        return get_financials_data(req.company)
    except Exception as e:
        raise HTTPException(500, detail=f"financials_error: {e}")

@router.post("/scorecard-real", response_model=ScorecardResponse)
def scorecard(req: CompanyRequest):
    try:
        return get_scorecard(req.company)
    except Exception as e:
        raise HTTPException(500, detail=f"scorecard_error: {e}")

@router.post("/jobs", response_model=JobsResponse)
def jobs(req: CompanyRequest):
    try:
        return get_jobs_data(req.company)
    except Exception as e:
        raise HTTPException(500, detail=f"jobs_error: {e}")

@router.post("/news", response_model=NewsResponse)
def news(req: CompanyRequest):
    try:
        items = fetch_news_for_company(req.company)
        return NewsResponse(company=req.company, news=items)
    except Exception as e:
        raise HTTPException(500, detail=f"news_error: {e}")

@router.post("/events", response_model=EventsResponse)
def events(req: CompanyRequest):
    try:
        items = fetch_events_for_company(req.company)
        return EventsResponse(company=req.company, events=items)
    except Exception as e:
        raise HTTPException(500, detail=f"events_error: {e}")
