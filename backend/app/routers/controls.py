# Use: Router managing control assignments and their operational status.

from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/controls", tags=["controls"])


@router.get("/")
async def get_controls_root() -> dict[str, Any]:
    return {
        "message": "Controls API root",
        "available": ["list", "detail", "update"],
    }
