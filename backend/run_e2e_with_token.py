import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal
from app.core.security import create_access_token
import httpx


async def main():
    email = 'test.compliance+ai@example.com'
    async with AsyncSessionLocal() as session:
        # find user
        result = await session.execute(text("select user_id from users where email = :email limit 1"), {"email": email})
        row = result.mappings().first()
        if not row:
            print('Test user not found')
            return
        user_id = str(row['user_id'])

        # find active session
        result = await session.execute(text("select session_id from user_sessions where user_id = :user_id and (expires_at is null or expires_at > current_timestamp) limit 1"), {"user_id": user_id})
        srow = result.mappings().first()
        if not srow:
            print('Active session for test user not found')
            return
        session_id = str(srow['session_id'])

        token = create_access_token(subject=user_id, claims={'session_id': session_id})

    # Call AI service endpoint with Authorization header
    url = 'http://127.0.0.1:8001/compliance/chat'
    headers = {'Authorization': f'Bearer {token}'}
    payload = {'query': 'When was the last assessment date for the organization?'}

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers, timeout=60.0)
        try:
            print('status', resp.status_code)
            print(resp.json())
        except Exception:
            print('raw', resp.text)


if __name__ == '__main__':
    asyncio.run(main())
