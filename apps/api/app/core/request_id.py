"""Request ID middleware (specification §6.1, FR-125).

A client-supplied UUID in X-Request-ID is kept, otherwise one is generated. The ID is stored in a
context variable and in the request state (where the error handlers read it) and echoed in the
X-Request-ID header of every response.
"""

import uuid
from contextvars import ContextVar

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER = "X-Request-ID"

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


class RequestIdMiddleware:
    """Pure ASGI middleware, so it also covers responses produced by inner exception handlers."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = parse_request_id(Headers(scope=scope).get(REQUEST_ID_HEADER))
        request_id = request_id or new_request_id()
        scope.setdefault("state", {})["request_id"] = request_id
        token = request_id_var.set(request_id)

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            request_id_var.reset(token)
