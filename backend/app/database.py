# Use: Database configuration for SQLAlchemy async engine and session management.

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.sql import text

from app.config import get_settings

settings = get_settings()

engine: AsyncEngine = create_async_engine(
    str(settings.database_url),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def initialize_database_schema() -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text(
                """
                create table if not exists notifications (
                    notification_id text primary key,
                    institution_id text not null,
                    user_id text not null,
                    title text not null,
                    message text,
                    notification_type text,
                    related_entity_type text,
                    related_entity_id text,
                    is_read boolean not null default false,
                    created_at timestamptz not null default now()
                )
                """
            )
        )
        await connection.execute(
            text("alter table audit_logs add column if not exists mac_address text")
        )


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


async def check_postgres() -> dict[str, int | bool]:
    async with engine.connect() as connection:
        await connection.execute(text("select 1"))
    return {"ok": True}
