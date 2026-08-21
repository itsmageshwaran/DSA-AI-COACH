"""Middleware that ensures every request has a unique X-Request-ID header."""

from __future__ import annotations

import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.core.logging.logger import request_id_ctx


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assign a UUID request identifier if client did not provide one."""

    header_name = "X-Request-ID"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request and attach X-Request-ID header."""
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        request.state.request_id = request_id

        token = request_id_ctx.set(request_id)
        try:
            response: Response = await call_next(request)
            response.headers[self.header_name] = request_id
            return response
        finally:
            request_id_ctx.reset(token)
