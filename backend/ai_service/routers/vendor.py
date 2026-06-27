# Use: Vendor analysis endpoints.

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/vendor", tags=["Vendor"])


class AnalyzeContractRequest(BaseModel):
    contract_text: str


@router.post("/analyze-contract")
async def analyze_contract(payload: AnalyzeContractRequest):
    return {"risks": [], "overall_risk": "Low"}
