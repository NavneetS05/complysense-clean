# Use: AI endpoints for policy conflict checking and summaries.

from fastapi import APIRouter

router = APIRouter(prefix="/policy", tags=["ai-policy"])
