# Use: Handles interactions with the MongoDB Atlas control library documents.

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import get_settings


class ControlLibraryStore:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.settings = get_settings()
        self.collection = database[self.settings.mongodb_control_library_collection]

    async def save_control(self, control: dict[str, Any]) -> str:
        now = datetime.now(UTC)
        document = {**control, "created_at": now, "updated_at": now}
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def find_by_control_id(self, control_id: str) -> dict[str, Any] | None:
        document = await self.collection.find_one({"control_id": control_id})
        if document is None:
            return None
        document["_id"] = str(document["_id"])
        return document

    async def get(self, document_id: str) -> dict[str, Any] | None:
        document = await self.collection.find_one({"_id": ObjectId(document_id)})
        if document is None:
            return None
        document["_id"] = str(document["_id"])
        return document

    async def list_all(self, limit: int = 500) -> list[dict[str, Any]]:
        """Return up to `limit` controls. No router calls this yet (Phase 3 candidate)."""
        cursor = self.collection.find({}, limit=limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    async def list_by_framework(self, framework_name: str, limit: int = 500) -> list[dict[str, Any]]:
        """Return controls filtered by framework_name field."""
        cursor = self.collection.find({"framework_name": framework_name}, limit=limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    async def update_control(self, document_id: str, updates: dict[str, Any]) -> bool:
        if not updates:
            return False
        result = await self.collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {**updates, "updated_at": datetime.now(UTC)}},
        )
        return result.modified_count > 0

    async def delete(self, document_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0
