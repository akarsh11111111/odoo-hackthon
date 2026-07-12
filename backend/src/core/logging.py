"""Structured logging configuration for TransitOps."""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone

from src.core.config import get_settings

request_id_context: ContextVar[str] = ContextVar("request_id", default="-")
user_context: ContextVar[str] = ContextVar("user_id", default="-")
role_context: ContextVar[str] = ContextVar("role_name", default="-")
token_context: ContextVar[str] = ContextVar("token_type", default="-")


class RequestIdFilter(logging.Filter):
    """Attach correlation context to each log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get()
        record.user_id = user_context.get()
        record.role_name = role_context.get()
        record.token_type = token_context.get()
        return True


class JsonFormatter(logging.Formatter):
    """Format log records as JSON for centralized logging."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
            "user_id": getattr(record, "user_id", "-"),
            "role_name": getattr(record, "role_name", "-"),
            "token_type": getattr(record, "token_type", "-"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)


def configure_logging() -> None:
    """Configure application logging once at startup."""

    settings = get_settings()
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(settings.log_level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIdFilter())
    root_logger.addHandler(handler)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(logger_name).handlers.clear()
        logging.getLogger(logger_name).propagate = True
