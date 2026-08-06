import asyncio
from datetime import datetime, timedelta
from sqlalchemy import text

from app.database import AsyncSessionLocal
from app.repositories.sessions import SessionRepository
from app.repositories.users import UserRepository
from app.core.security import create_access_token


async def main():
    async with AsyncSessionLocal() as session:
        # find user by email
        email = 'test.compliance+ai@example.com'
        result = await session.execute(text('select user_id from users where email = :email limit 1'), {'email': email})
        row = result.mappings().first()
        if not row:
            print('User not found')
            return
        user_id = str(row['user_id'])

        # find compliance officer role id
        # we reuse the user's role
        role_res = await session.execute(text('select role_id from users where user_id = :uid limit 1'), {'uid': user_id})
        role_row = role_res.mappings().first()
        if not role_row:
            print('Role not found')
            return
        role_id = str(role_row['role_id'])

        # create session
        expires = datetime.utcnow() + timedelta(days=1)
        session_repo = SessionRepository(session)
        session_id = await session_repo.create(
            user_id=user_id,
            active_role_id=role_id,
            user_agent='ai-e2e-test',
            ip_address='127.0.0.1',
            expires_at=expires,
        )

        token = create_access_token(subject=user_id, claims={'session_id': str(session_id)})
        await session.commit()

        print('CREATED_SESSION_ID', session_id)
        print('ACCESS_TOKEN', token)


if __name__ == '__main__':
    asyncio.run(main())
