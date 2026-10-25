from fastapi import Request, HTTPException
import time
from collections import deque, defaultdict
from typing import Deque

class RateLimiter:
    def __init__(self, requests_per_unit: int, unit_seconds: int):
        self.requests_per_unit = requests_per_unit
        self.unit_seconds = unit_seconds
        # Store timestamps of requests per client IP
        self._request_log: defaultdict[str, Deque[float]] = defaultdict(deque)

    def is_allowed(self, client_ip: str) -> bool:
        """
        Return True if the client is under the rate limit, otherwise False.
        """
        now = time.time()
        timestamps = self._request_log[client_ip]

        # Remove timestamps older than the current window
        while timestamps and now - timestamps[0] > self.unit_seconds:
            timestamps.popleft()

        if len(timestamps) < self.requests_per_unit:
            timestamps.append(now)
            return True
        return False

    async def __call__(self, request: Request) -> None:
        """
        FastAPI dependency entry point – validates the request using ``is_allowed``.
        """
        client_ip = request.client.host if request.client else "unknown"
        if not self.is_allowed(client_ip):
            raise HTTPException(status_code=429, detail="Too Many Requests")
