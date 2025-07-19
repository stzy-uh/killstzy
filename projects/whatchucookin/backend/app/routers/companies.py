# app/routers/companies.py
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.intel import get_company_news
from app.services.scorecard.pipeline import get_scorecard_stub  # or your real function
from app.services.financials import fetch_financials

router = APIRouter()

class CompanyRequest(BaseModel):
    company: str

@router.post("/intel")
def intel(req: CompanyRequest):
    return get_company_news(req.company)

@router.post("/scorecard")
def scorecard(req: CompanyRequest):
    return get_scorecard_stub(req.company)

@router.post("/financials")
def financials(req: CompanyRequest):
    return fetch_financials(req.company)
