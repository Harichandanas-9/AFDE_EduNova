"""Simple in-memory rate limiter middleware (per IP)."""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter. Suitable for a single instance."""

    def __init__(self, app):
        super().__init__(app)
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)
        self._limit = settings.RATE_LIMIT_REQUESTS
        self._window = settings.RATE_LIMIT_WINDOW_SECONDS

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health / docs
        if request.url.path in ("/api/v1/health", "/", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        bucket = self._hits[client_ip]

        # Drop entries outside the window
        while bucket and now - bucket[0] > self._window:
            bucket.popleft()

        if len(bucket) >= self._limit:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please retry shortly.",
                    "limit": self._limit,
                    "window_seconds": self._window,
                },
            )

        bucket.append(now)
        return await call_next(request)
