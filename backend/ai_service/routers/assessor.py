# Use: Assessor endpoints.

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/assessor", tags=["Assessor"])


class AssessorChatRequest(BaseModel):
    query: str
    conversation_id: str


@router.post("/chat")
async def chat_endpoint(payload: AssessorChatRequest):
    return {"response": "Assessor Agent response placeholder"}
