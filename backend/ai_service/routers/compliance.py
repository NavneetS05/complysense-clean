# Use: Compliance endpoints.

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/compliance", tags=["Compliance"])


class ComplianceGapAnalysisRequest(BaseModel):
    framework_id: str


@router.post("/gap-analysis")
async def gap_analysis_endpoint(payload: ComplianceGapAnalysisRequest):
    return {"gaps": []}
