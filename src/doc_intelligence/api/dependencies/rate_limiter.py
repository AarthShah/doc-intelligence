from fastapi import Request, HTTPException
import time
from collections import deque

class RateLimiter:
    def __init__(self, requests_per_unit: int, unit_seconds: int):
        self.requests_per_unit = requests_per_unit
        self.unit_seconds = unit_seconds
        self.requests = {}  # client_ip -> deque of timestamps

    async def __call__(self, request: Request) -> None:
        """
        FastAPI dependency that enforces a request rate limit per client IP.

        Parameters
        ----------
        request: Request
            The incoming FastAPI request.

        Raises
        ------
        HTTPException
            If the client has exceeded the allowed number of requests within the time window.
        """
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        if client_ip not in self.requests:
            self.requests[client_ip] = deque()

        # Remove old requests that are outside the time window
        while self.requests[client_ip] and self.requests[client_ip][0] < now - self.unit_seconds:
            self.requests[client_ip].popleft()

        if len(self.requests[client_ip]) >= self.requests_per_unit:
            raise HTTPException(status_code=429, detail="Too many requests")

        self.requests[client_ip].append(now)
