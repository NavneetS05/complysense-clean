# Use: MongoDB connection helper using Motor async client for MongoDB Atlas.

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

settings = get_settings()
mongo_client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=10000)


def get_mongo_database() -> AsyncIOMotorDatabase:
    return mongo_client[settings.mongodb_database]


async def check_mongodb() -> dict[str, bool]:
    await get_mongo_database().command("ping")
    return {"ok": True}
