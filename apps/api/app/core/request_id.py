"""Request ID middleware (specification §6.1, FR-125).

A client-supplied UUID in X-Request-ID is kept, otherwise one is generated. The ID is stored in a
context variable and in the request state (where the error handlers read it) and echoed in the
X-Request-ID header of every response.

The middleware also times the request and writes one access line per request to the
``app.access`` logger (FR-125 AC1). The fields are method, route template, status, latency_ms and
user_hash; the line never holds the raw path, query string, headers or body. user_hash is set
when ``request.state.user_id`` holds the caller's ID. The JSON format and redaction are in
``app.core.logging``.
"""

import hashlib
import logging
import time
import uuid
from contextvars import ContextVar

from fastapi.routing import iter_route_contexts
from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER = "X-Request-ID"

access_logger = logging.getLogger("app.access")

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def parse_request_id(value: str | None) -> str | None:
    """The canonical lower-case form of a client UUID, or None when it is not a UUID."""
    if not value:
        return None
    try:
        return str(uuid.UUID(value))
    except ValueError:
        return None


def new_request_id() -> str:
    return str(uuid.uuid4())


def current_request_id() -> str | None:
    return request_id_var.get()


def user_hash(user_id: object) -> str:
    """The first 12 hex characters of the SHA-256 of the user ID; the ID itself is never logged."""
    return hashlib.sha256(str(user_id).encode()).hexdigest()[:12]


class RequestIdMiddleware:
    """Pure ASGI middleware, so it also covers responses produced by inner exception handlers."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        # Route object -> full path template. A route inside an included router knows only its
        # own path ("/trips/{trip_id}"); FastAPI's route contexts carry the prefix.
        self._templates: dict[int, str] | None = None

    def _route_template(self, scope: Scope) -> str | None:
        route = scope.get("route")
        if route is None:
            return None  # no route matched: the raw path is never logged
        if self._templates is None and "app" in scope:
            routes = getattr(scope["app"], "routes", [])
            self._templates = {
                id(c.original_route): c.path for c in iter_route_contexts(routes) if c.path
            }
        return (self._templates or {}).get(id(route), getattr(route, "path", None))

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = parse_request_id(Headers(scope=scope).get(REQUEST_ID_HEADER))
        request_id = request_id or new_request_id()
        state = scope.setdefault("state", {})
        state["request_id"] = request_id
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        status = 500  # when no response starts, the server answers 500

        async def send_with_request_id(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                MutableHeaders(scope=message)[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            user_id = state.get("user_id")
            access_logger.info(
                "request",
                extra={
                    "request_id": request_id,
                    "method": scope["method"],
                    "route": self._route_template(scope),
                    "status": status,
                    "latency_ms": round((time.perf_counter() - started) * 1000, 1),
                    "user_hash": user_hash(user_id) if user_id else None,
                },
            )
            request_id_var.reset(token)
