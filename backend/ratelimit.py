
import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

WINDOW_SECONDS = 60
MAX_REQUESTS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/api/"):
            ip = request.client.host if request.client else "?"
            now = time.monotonic()
            window = self.hits[ip]
            while window and window[0] <= now - WINDOW_SECONDS:
                window.popleft()
            if len(window) >= MAX_REQUESTS:
                return JSONResponse({"detail": "Too many requests"}, status_code=429)
            window.append(now)
        return await call_next(request)
