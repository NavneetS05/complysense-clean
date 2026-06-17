# Use: AI endpoints for generating personalized morning compliance digests.

from fastapi import APIRouter

router = APIRouter(prefix="/digest", tags=["ai-digest"])
