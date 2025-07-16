from fastapi import APIRouter, HTTPException
from app.schemas import GossipRequest
from app.services.gossiper import get_gossip_data

router = APIRouter()

@router.post("/gossip")
async def gossip(request: GossipRequest):
    try:
        result = get_gossip_data(request.company)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

