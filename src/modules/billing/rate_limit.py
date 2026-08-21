"""Rate limiting dependency using Redis."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException, Request, status

from src.infrastructure.redis.connection import get_redis_client
from src.domain.auth.models import User
from src.modules.auth.dependencies import get_current_user

# Fallback for when Redis is unavailable, or for unauthenticated users.
# A proper rate limiter should use IP, but we'll use a fast token bucket in Redis.


def rate_limit(requests: int, window: int) -> Callable[..., Any]:
    """Factory for rate limiting dependency.

    Args:
        requests: Maximum number of requests allowed in the window.
        window: Time window in seconds.

    """

    async def _rate_limit_dependency(
        request: Request,
        user: User | None = Depends(get_current_user),
    ) -> None:
        redis = get_redis_client()
        if not redis:
            # Fail open if Redis is down
            return

        # Use user ID if authenticated, else IP address
        client_identifier = user.id if user else request.client.host if request.client else "unknown_ip"

        # Simple fixed window rate limiting
        current_window = int(time.time() // window)
        key = f"rate_limit:{request.url.path}:{client_identifier}:{current_window}"

        # Atomic INCR and EXPIRE
        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        results = await pipe.execute()

        current_requests = results[0]

        if current_requests > requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(requests),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(window - int(time.time() % window)),
                },
            )

        # Optional: Add successful headers to response (though FastAPI dependencies
        # normally don't modify the response directly, this would be done via middleware if strictly needed)

    return _rate_limit_dependency
