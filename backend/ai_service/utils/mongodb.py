# Use: Decoupled MongoDB Motor async client for the AI service.
# Connects to Atlas using MONGODB_URI from .env — does NOT import from app.*

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ai_service.config import get_ai_settings
from ai_service.utils.logger import StructuredLogger

logger = StructuredLogger("ai_service.utils.mongodb")

_mongo_client: Optional[AsyncIOMotorClient] = None


def get_mongo_client() -> Optional[AsyncIOMotorClient]:
    """
    Returns a lazy-initialized Motor async client.
    Returns None if MONGODB_URI is not configured (graceful degradation).
    The service will continue without user-document indexing.
    """
    global _mongo_client
    if _mongo_client is not None:
        return _mongo_client

    settings = get_ai_settings()
    if not settings.mongodb_uri:
        logger.warning(
            "mongodb.not_configured",
            detail="MONGODB_URI is missing. User-uploaded document indexing will be skipped.",
        )
        return None

    try:
        _mongo_client = AsyncIOMotorClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=8000,
        )
        logger.info("mongodb.connected", database=settings.mongodb_database)
        return _mongo_client
    except Exception as exc:
        logger.error("mongodb.connection_failed", error=str(exc))
        return None


def get_mongo_database() -> Optional[AsyncIOMotorDatabase]:
    """
    Returns the configured MongoDB database or None if unavailable.
    """
    client = get_mongo_client()
    if client is None:
        return None

    settings = get_ai_settings()
    return client[settings.mongodb_database]
