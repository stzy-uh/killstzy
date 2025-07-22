from fastapi import APIRouter, HTTPException
from app.schemas import GossipRequest, GossipResponse
from app.services.gossiper import generate_gossip

router = APIRouter()

@router.post("/", response_model=GossipResponse)
def gossip(req: GossipRequest):
    try:
        return generate_gossip(req.company)
    except Exception as e:
        raise HTTPException(500, detail=f"gossip_error: {e}")
