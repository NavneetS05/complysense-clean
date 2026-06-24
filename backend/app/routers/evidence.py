# Use: Router for uploading and reviewing evidence files.

from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get("/")
async def get_evidence_root() -> dict[str, Any]:
    return {
        "message": "Evidence API root",
        "available": ["list", "upload", "review"],
    }
