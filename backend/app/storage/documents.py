# Use: Abstractions for managing raw file paths and metadata.

from datetime import UTC, datetime
from typing import Any

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
