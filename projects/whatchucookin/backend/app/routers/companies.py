# app/routers/companies.py
from fastapi import APIRouter
from app.schemas import CompanyRequest
from app.services.intel import get_company_news

router = APIRouter()

@router.post("/intel")
async def company_intel(request: CompanyRequest):
    return get_company_news(request.company)
