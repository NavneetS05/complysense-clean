# Use: Daily digest endpoints.

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/digest", tags=["Digest"])


class GenerateDigestRequest(BaseModel):
    user_id: str
    role: str


@router.post("/generate")
async def generate_digest(payload: GenerateDigestRequest):
    return {"digest": "Daily morning digest summary placeholder"}
