# Use: Handles interactions with the MongoDB Atlas control library documents.

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import get_settings


class ControlLibraryStore:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.settings = get_settings()
        self.collection = database[self.settings.mongodb_control_library_collection]

    async def find_by_control_id(self, control_id: str) -> dict[str, Any] | None:
        document = await self.collection.find_one({"control_id": control_id})
        if document is None:
            return None
        document["_id"] = str(document["_id"])
        return document
