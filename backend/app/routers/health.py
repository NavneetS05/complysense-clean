# Use: Health check router confirming database and service availability.

import asyncio
from typing import Any
from fastapi import APIRouter

from app.database import check_postgres
from app.mongodb import check_mongodb
from app.supabase_client import check_supabase_sync

router = APIRouter(prefix="/health", tags=["health"])


async def check_supabase() -> dict[str, Any]:
    return await asyncio.to_thread(check_supabase_sync)


async def safe_check(name: str, check: object) -> dict[str, object]:
    try:
        result = await check()  # type: ignore[misc]
        return {"name": name, "status": "ok", "details": result}
    except Exception as exc:  # noqa: BLE001 - health reports dependency errors
        return {"name": name, "status": "error", "error": str(exc)}


@router.get("/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready() -> dict[str, object]:
    dependencies = [
        await safe_check("postgres", check_postgres),
        await safe_check("mongodb", check_mongodb),
        await safe_check("supabase", check_supabase),
    ]
    status = "ready" if all(item["status"] == "ok" for item in dependencies) else "degraded"
    return {"status": status, "dependencies": dependencies}
