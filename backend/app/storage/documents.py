# Use: Abstractions for managing raw file paths and metadata.

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import get_settings


class DocumentStore:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.settings = get_settings()
        self.collection = database[self.settings.mongodb_documents_collection]

    async def save_metadata(
        self,
        *,
        institution_id: str,
        source_type: str,
        metadata: dict[str, Any],
        source_id: str | None = None,
        extracted_text: str | None = None,
    ) -> str:
        now = datetime.now(UTC)
        result = await self.collection.insert_one(
            {
                "institution_id": institution_id,
                "source_type": source_type,
                "source_id": source_id,
                "metadata": metadata,
                "extracted_text": extracted_text,
                "created_at": now,
                "updated_at": now,
            }
        )
        return str(result.inserted_id)

    async def get(self, document_id: str) -> dict[str, Any] | None:
        row = await self.collection.find_one({"_id": ObjectId(document_id)})
        if row:
            row["_id"] = str(row["_id"])
        return row

    async def update_metadata(
        self,
        document_id: str,
        *,
        metadata: dict[str, Any] | None = None,
        extracted_text: str | None = None,
    ) -> bool:
        updates: dict[str, Any] = {"updated_at": datetime.now(UTC)}
        if metadata is not None:
            updates["metadata"] = metadata
        if extracted_text is not None:
            updates["extracted_text"] = extracted_text
        result = await self.collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": updates},
        )
        return result.modified_count > 0

    async def delete(self, document_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0
