# Use: Centralized structured logging.

import logging
import structlog


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configures structlog with JSON rendering and stdlib integration.
    Call once at app startup in main.py lifespan.
    """
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )


class StructuredLogger:
    def __init__(self, name: str):
        self.logger = structlog.get_logger(name)

    def info(self, event: str, **kwargs: object) -> None:
        self.logger.info(event, **kwargs)

    def warning(self, event: str, **kwargs: object) -> None:
        self.logger.warning(event, **kwargs)

    def error(self, event: str, **kwargs: object) -> None:
        self.logger.error(event, **kwargs)

    def debug(self, event: str, **kwargs: object) -> None:
        self.logger.debug(event, **kwargs)
