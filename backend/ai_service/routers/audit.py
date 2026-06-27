# Use: Audit endpoints.

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/audit", tags=["Audit"])


class AuditObservationRequest(BaseModel):
    evidence_id: str
    control_id: str


@router.post("/draft-observation")
async def draft_observation_endpoint(payload: AuditObservationRequest):
    return {"draft": "Audit observation draft placeholder"}
