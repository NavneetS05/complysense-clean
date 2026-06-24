# Use: Router managing IT security incident command center, timelines, and reporting.

from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("/")
async def get_incidents_root() -> dict[str, Any]:
    return {
        "message": "Incidents API root",
        "available": ["list", "create", "detail"],
    }
