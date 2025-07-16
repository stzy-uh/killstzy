# app/schemas.py

from pydantic import BaseModel

class CompanyRequest(BaseModel):
    company: str

class GossipRequest(BaseModel):
    company: str
