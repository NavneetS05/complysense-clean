import asyncio
from datetime import datetime, timedelta
from sqlalchemy import text

from app.database import AsyncSessionLocal
from app.repositories.users import UserRepository
from app.repositories.sessions import SessionRepository
from app.core.security import hash_password, create_access_token


async def main():
    async with AsyncSessionLocal() as session:
        # find role id for Compliance Officer
        result = await session.execute(
            text("select role_id from roles where role_name = :name limit 1"),
            {"name": "Compliance Officer"},
        )
        row = result.mappings().first()
        if not row:
            print("Role 'Compliance Officer' not found in roles table")
            return
        role_id = str(row["role_id"])

        # find an existing institution_id to associate the user with
        inst_result = await session.execute(text("select institution_id from institutions limit 1"))
        inst_row = inst_result.mappings().first()
        if not inst_row:
            print("No institution found — cannot create test user")
            return
        institution_id = str(inst_row['institution_id'])

        # create test user
        user_repo = UserRepository(session)
        user = await user_repo.create(
            institution_id=institution_id,
            role_id=role_id,
            full_name='Test Compliance AI',
            email='test.compliance+ai@example.com',
            password_hash=hash_password('Password123!'),
        )

        # create session
        expires = datetime.utcnow() + timedelta(days=1)
        session_repo = SessionRepository(session)
        session_id = await session_repo.create(
            user_id=user['user_id'],
            active_role_id=role_id,
            user_agent='ai-e2e-test',
            ip_address='127.0.0.1',
            expires_at=expires,
        )

        # Ensure token claims are JSON-serializable strings
        token = create_access_token(subject=str(user['user_id']), claims={'session_id': str(session_id)})
        await session.commit()

        print('CREATED_USER_ID', user['user_id'])
        print('CREATED_SESSION_ID', session_id)
        print('ACCESS_TOKEN', token)


if __name__ == '__main__':
    asyncio.run(main())
