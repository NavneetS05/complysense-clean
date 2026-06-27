# Use: Policy endpoints.

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/policy", tags=["Policy"])


class PolicyReviewRequest(BaseModel):
    policy_text: str
    framework_id: str


@router.post("/review")
async def review_policy(payload: PolicyReviewRequest):
    return {"conflicts": [], "verdict": "COMPLIANT"}
