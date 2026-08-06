import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as session:
        res = await session.execute(text("select created_at, created_at at time zone 'UTC' as created_at_utc from audit_logs order by created_at desc limit 5"))
        rows = res.mappings().all()
        for r in rows:
            print("DB ROW:", r['created_at'], "type:", type(r['created_at']), "tzinfo:", r['created_at'].tzinfo if hasattr(r['created_at'], 'tzinfo') else None)
            print("ISO:", r['created_at'].isoformat())

if __name__ == "__main__":
    asyncio.run(main())
