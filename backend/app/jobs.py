# Use: Defines periodic or asynchronous background task execution jobs.

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Job:
    name: str
    payload: dict[str, object]
    run_at: datetime | None = None


JobProcessor = Callable[[Job], Awaitable[None]]


class JobRegistry:
    def __init__(self) -> None:
        self._processors: dict[str, JobProcessor] = {}

    def register(self, name: str, processor: JobProcessor) -> None:
        self._processors[name] = processor

    async def enqueue(self, job: Job) -> None:
        processor = self._processors.get(job.name)
        if processor is None:
            raise ValueError(f"No job processor registered for {job.name}")
        await processor(job)


job_registry = JobRegistry()
