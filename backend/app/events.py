# Use: Handles FastAPI application lifecycle events (startup and shutdown handlers).

from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from app.core.logging import logger


@dataclass(frozen=True)
class DomainEvent:
    event_type: str
    payload: dict[str, object]
    institution_id: str | None = None
    actor_user_id: str | None = None
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers[event.event_type]:
            try:
                await handler(event)
            except Exception as exc:
                logger.error(
                    "event_bus.handler_failed",
                    event_type=event.event_type,
                    event_id=event.event_id,
                    handler=getattr(handler, "__name__", str(handler)),
                    error=str(exc),
                )


event_bus = EventBus()
