from fastapi import APIRouter, HTTPException
from app.schemas import RoastRequest, RoastResponse
from app.services.roaster import generate_roast

router = APIRouter()

@router.post("/", response_model=RoastResponse)
def roast(req: RoastRequest):
    try:
        return generate_roast(req.company)
    except Exception as e:
        raise HTTPException(500, detail=f"roast_error: {e}")
