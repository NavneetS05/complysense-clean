# Use: AI endpoints for generating CERT-In incident report drafts.

from fastapi import APIRouter

router = APIRouter(prefix="/security", tags=["ai-security"])
