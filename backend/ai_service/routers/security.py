# Use: Security endpoints.

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/security", tags=["Security"])


class IncidentReportRequest(BaseModel):
    incident_details: str


@router.post("/draft-certin-report")
async def draft_certin_report(payload: IncidentReportRequest):
    return {"report_form": "CERT-In incident draft report layout placeholder"}
