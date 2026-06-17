# Use: AI endpoints for Read-Only Assessor RAG chat interface.

from fastapi import APIRouter

router = APIRouter(prefix="/assessor", tags=["ai-assessor"])
