# Use: Repository retrieving user permissions based on active roles from PostgreSQL.

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class RbacRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def permissions_for_role(self, role_id: str) -> list[str]:
        result = await self.session.execute(
            text(
                """
                select p.permission_key
                  from role_permissions rp
                  join permissions p on p.permission_id = rp.permission_id
                 where rp.role_id = :role_id
                 order by p.permission_key
                """
            ),
            {"role_id": role_id},
        )
        return [str(row[0]) for row in result.all()]
