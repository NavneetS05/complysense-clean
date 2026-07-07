# Use: Manages conversation history persistence in ai_conversations (PostgreSQL).
# Updated: removed app.database import; uses decoupled utils/database.py session factory.

import json
from typing import Any, Dict, List

from sqlalchemy import text

from ai_service.utils.logger import StructuredLogger

logger = StructuredLogger("ai_service.rag.generation.conversation")


class ConversationManager:
    """
    Reads and writes conversation turns to the ai_conversations PostgreSQL table.

    If the database is not configured (DATABASE_URL missing) every method silently
    returns an empty result — the rest of the agent flow continues unaffected.
    """

    async def get_history(
        self,
        conversation_id: str,
        user_id: str,
        institution_id: str,
        limit: int = 6,
    ) -> List[Dict[str, str]]:
        """
        Returns the last `limit` messages for a conversation.
        Enforces strict user + institution isolation.

        Raises:
            ValueError: if the conversation belongs to a different user/institution.
        """
        if not conversation_id:
            return []

        session = await self._get_session()
        if session is None:
            return []

        async with session as db:
            query = text(
                """
                SELECT messages, institution_id, user_id
                FROM ai_conversations
                WHERE conversation_id = :conv_id
                """
            )
            res = await db.execute(query, {"conv_id": conversation_id})
            row = res.mappings().first()

        if not row:
            return []

        row_inst_id = str(row["institution_id"]) if row["institution_id"] else ""
        row_user_id = str(row["user_id"]) if row["user_id"] else ""

        if row_inst_id != str(institution_id) or row_user_id != str(user_id):
            raise ValueError("Unauthorized access to this conversation history.")

        messages = row["messages"]
        if isinstance(messages, str):
            messages = json.loads(messages)

        return messages[-limit:]

    async def save_turn(
        self,
        conversation_id: str,
        user_id: str,
        institution_id: str,
        agent_type: str,
        user_query: str,
        assistant_response: str,
    ) -> None:
        """
        Appends a user+assistant turn to the conversation row.
        Creates the conversation row if it does not yet exist.
        Enforces strict user + institution isolation on existing rows.

        Raises:
            ValueError: if the conversation belongs to a different user/institution.
        """
        if not conversation_id:
            return

        session = await self._get_session()
        if session is None:
            return

        new_msgs: List[Dict[str, str]] = [
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": assistant_response},
        ]

        async with session as db:
            select_q = text(
                """
                SELECT messages, institution_id, user_id
                FROM ai_conversations
                WHERE conversation_id = :conv_id
                """
            )
            res = await db.execute(select_q, {"conv_id": conversation_id})
            row = res.mappings().first()

            if row:
                row_inst_id = str(row["institution_id"]) if row["institution_id"] else ""
                row_user_id = str(row["user_id"]) if row["user_id"] else ""
                if row_inst_id != str(institution_id) or row_user_id != str(user_id):
                    raise ValueError("Unauthorized access to save to this conversation.")

                existing = row["messages"]
                if isinstance(existing, str):
                    existing = json.loads(existing)
                updated = existing + new_msgs

                await db.execute(
                    text(
                        """
                        UPDATE ai_conversations
                        SET messages = :messages, updated_at = now()
                        WHERE conversation_id = :conv_id
                        """
                    ),
                    {"conv_id": conversation_id, "messages": json.dumps(updated)},
                )
            else:
                await db.execute(
                    text(
                        """
                        INSERT INTO ai_conversations (
                            conversation_id, institution_id, user_id,
                            agent_type, messages, created_at, updated_at
                        ) VALUES (
                            :conv_id, :inst_id, :user_id,
                            :agent_type, :messages, now(), now()
                        )
                        """
                    ),
                    {
                        "conv_id": conversation_id,
                        "inst_id": institution_id,
                        "user_id": user_id,
                        "agent_type": agent_type,
                        "messages": json.dumps(new_msgs),
                    },
                )

            await db.commit()
            logger.info(
                "conversation.turn_saved",
                conversation_id=conversation_id,
                agent_type=agent_type,
            )

    # ── Private ────────────────────────────────────────────────────────────────

    @staticmethod
    async def _get_session():
        """
        Returns a context-manager-capable async session, or None if the DB
        is not configured (graceful degradation).
        """
        from ai_service.utils.database import get_async_session_factory

        factory = get_async_session_factory()
        if factory is None:
            logger.warning(
                "conversation.db_unavailable",
                detail="Conversation history will not be persisted.",
            )
            return None
        return factory()
