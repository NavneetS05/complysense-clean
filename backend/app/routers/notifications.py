# Use: Router retrieving user alerts and notifications.

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.repositories.notification import NotificationRepository
from app.schemas.auth import UserContext

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", summary="List notifications for the current user")
async def list_notifications(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_NOTIFICATIONS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: int = 10,
    unread: bool = False,
) -> dict[str, Any]:
    repo = NotificationRepository(session)
    notifications = await repo.list_for_user(
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
        limit=limit,
        unread_only=unread,
    )
    unread_count = await repo.unread_count(
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
    )
    return {"notifications": notifications, "unread_count": unread_count}


@router.patch("/read-all", summary="Mark all notifications as read for current user")
async def mark_all_read(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_NOTIFICATIONS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, str]:
    repo = NotificationRepository(session)
    await repo.mark_all_read(
        institution_id=str(user_ctx.institution_id),
        user_id=str(user_ctx.user_id),
    )
    await session.commit()
    return {"message": "ok"}
