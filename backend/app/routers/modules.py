# Use: Router managing active system modules.

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.schemas.auth import UserContext

router = APIRouter(prefix="/modules", tags=["modules"])

BOUNDED_CONTEXTS = [
    "platform_foundation",
    "identity_and_access",
    "departments",
    "control_operations",
    "assessments_and_gaps",
    "mitigation_tasks",
    "evidence",
    "incidents",
    "vendors",
    "policies",
    "audit_workspace",
    "calendar",
    "notifications",
    "audit_logging",
    "ai_conversations",
]


@router.get("")
async def module_boundaries(_: Annotated[UserContext, Depends(get_current_user)]) -> dict[str, object]:
    return {"bounded_contexts": BOUNDED_CONTEXTS}
