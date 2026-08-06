# Use: Repository handling SQL operations for creating and inserting system audit logs.

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class AuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def write(
        self,
        *,
        institution_id: str | None,
        user_id: str | None,
        active_role_id: str | None,
        action_type: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        action_details: dict[str, Any] | None = None,
        ip_address: str | None = None,
        mac_address: str | None = None,
    ) -> None:
        """Insert a row into audit_logs."""
        details = action_details or {}
        if mac_address and "mac_address" not in details:
            details["mac_address"] = mac_address

        details_json = json.dumps(details)
        await self.session.execute(
            text(
                """
                insert into audit_logs (
                    institution_id, user_id, active_role_id,
                    action_type, entity_type, entity_id,
                    action_details, ip_address, mac_address
                )
                values (
                    :institution_id, :user_id, :active_role_id,
                    :action_type, :entity_type, :entity_id,
                    cast(:action_details as jsonb), :ip_address, :mac_address
                )
                """
            ),
            {
                "institution_id": institution_id,
                "user_id": user_id,
                "active_role_id": active_role_id,
                "action_type": action_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "action_details": details_json,
                "ip_address": ip_address,
                "mac_address": mac_address,
            },
        )

    async def get_recent_for_institution(
        self,
        institution_id: str,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Return recent audit log entries for a given institution (descending)."""
        result = await self.session.execute(
            text(
                """
                select al.audit_log_id, al.user_id, u.full_name as user_name,
                       al.active_role_id, r.role_name,
                       al.action_type, al.entity_type, al.entity_id,
                       al.action_details, al.ip_address, al.mac_address, al.created_at
                  from audit_logs al
                  left join users u on u.user_id = al.user_id
                  left join roles r on r.role_id = al.active_role_id
                 where al.institution_id = :institution_id
                 order by al.created_at desc
                 limit :limit offset :offset
                """
            ),
            {"institution_id": institution_id, "limit": limit, "offset": offset},
        )
        return [dict(row) for row in result.mappings().all()]

    async def get_all_institutions(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        action_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Super-admin: return audit logs across all institutions with optional action_type filter."""
        base = """
            select al.audit_log_id, al.institution_id, i.institution_name,
                   al.user_id, u.full_name as user_name,
                   al.action_type, al.entity_type, al.entity_id,
                   al.action_details, al.ip_address, al.mac_address, al.created_at
              from audit_logs al
              left join institutions i on i.institution_id = al.institution_id
              left join users u on u.user_id = al.user_id
        """
        where = "where al.action_type = :action_type" if action_type else ""
        query = f"{base} {where} order by al.created_at desc limit :limit offset :offset"
        result = await self.session.execute(
            text(query),
            {"action_type": action_type, "limit": limit, "offset": offset},
        )
        return [dict(row) for row in result.mappings().all()]
