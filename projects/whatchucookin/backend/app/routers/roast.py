from fastapi import APIRouter
from app.schemas import CompanyRequest
from app.services.roaster import roast_company

router = APIRouter()

@router.post("/roast")
async def roast(request: CompanyRequest):
    return {"roast": roast_company(request.company)}
