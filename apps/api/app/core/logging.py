"""JSON request logging with redaction (specification §6.1 "Request ID", FR-125, NFR-013; IMP-201).

``configure_logging`` puts one stdout handler on the root logger. Its ``RedactionFilter`` runs on
every record that reaches the handler, from any logger. It removes:

- Authorization values;
- values of keys whose name contains key, secret, token or password;
- e-mail addresses;
- any field named prompt, system_text, user_text or notes.

``JsonFormatter`` then writes one JSON object per line. The fields are timestamp, level, logger,
message and request_id, plus user_hash, method, route, status and latency_ms when the record
carries them (the access line of ``app.core.request_id``). Prompt bodies are never logged at any
level (FR-125 AC2).
"""

import json
import logging
import re
import sys
from datetime import UTC, datetime
from typing import Any, Final, TextIO

from app.core.request_id import current_request_id

REDACTED: Final = "[redacted]"
# Optional fields copied from the record when present (the access line sets them).
ACCESS_FIELDS: Final = ("user_hash", "method", "route", "status", "latency_ms")
DROPPED_FIELDS: Final = frozenset({"prompt", "system_text", "user_text", "notes"})

_SENSITIVE_KEY = re.compile(r"key|secret|token|password|authorization", re.IGNORECASE)
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# "Authorization: Bearer x", "api_key=x", '"token": "x"' in free text. "GEMINI_API_KEY: missing"
# (a start-up message that names a variable, FR-124) is kept: a colon needs a quoted value.
_SECRET_IN_TEXT = re.compile(
    r"""(?ix)
    (\b(?:authorization|bearer)\b\s*[:=]?\s*(?:bearer\s+)?)[^\s,;"']+
    | ([\w-]*(?:key|secret|token|password)[\w-]*(?:\s*=\s*["']?|["']?\s*:\s*["']))[^\s,;"'&]+
    """
)
# The attributes every LogRecord has; anything else on a record came from ``extra``.
_RECORD_ATTRIBUTES: Final = frozenset(vars(logging.makeLogRecord({}))) | {"message", "asctime"}
_HANDLER_NAME: Final = "app-json"


def redact_text(value: str) -> str:
    value = _SECRET_IN_TEXT.sub(lambda m: (m.group(1) or m.group(2)) + REDACTED, value)
    return _EMAIL.sub(REDACTED, value)


class RedactionFilter(logging.Filter):
    """Redacts the message, the exception text and every ``extra`` field in place."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_text(record.getMessage())
        record.args = None
        if record.exc_info:
            record.exc_text = logging.Formatter().formatException(record.exc_info)
            record.exc_info = None
        if record.exc_text:
            record.exc_text = redact_text(record.exc_text)
        for name in [n for n in vars(record) if n not in _RECORD_ATTRIBUTES]:
            if name in DROPPED_FIELDS:
                delattr(record, name)
            elif _SENSITIVE_KEY.search(name):
                setattr(record, name, REDACTED)
            elif isinstance(value := getattr(record, name), str):
                setattr(record, name, redact_text(value))
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        line: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None) or current_request_id(),
        }
        line.update({f: getattr(record, f) for f in ACCESS_FIELDS if hasattr(record, f)})
        if record.exc_text:
            line["exception"] = record.exc_text
        return json.dumps(line, default=str)


def configure_logging(level: str, stream: TextIO | None = None) -> logging.Handler:
    """Install (or replace) the JSON handler on the root logger at LOG_LEVEL.

    Uvicorn's own loggers are routed through it as well. Its access log is switched off, because it
    would print the raw path and query string; ``app.core.request_id`` writes the access line.
    """
    root = logging.getLogger()
    for old in [h for h in root.handlers if h.get_name() == _HANDLER_NAME]:
        root.removeHandler(old)
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.set_name(_HANDLER_NAME)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RedactionFilter())
    root.addHandler(handler)
    root.setLevel(level)
    for name in ("uvicorn", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True
    logging.getLogger("uvicorn.access").disabled = True
    return handler
