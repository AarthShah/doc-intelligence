from fastapi import Request, HTTPException
from starlette.responses import JSONResponse
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import time

class RateLimiter:
    def __init__(self, limit: int, period: int):
        self.limit = limit
        self.period = period
        self.user_requests = {}  # In-memory store for user requests: {user_identifier: [(timestamp, count)]}

    async def __call__(self, request: Request):
        # Simple user identification based on IP address. In a real app, consider more robust methods.
        user_identifier = request.client.host
        current_time = time.time()

        if user_identifier not in self.user_requests:
            self.user_requests[user_identifier] = []

        # Clean up old timestamps
        self.user_requests[user_identifier] = [
            (ts, count) for ts, count in self.user_requests[user_identifier] if ts > current_time - self.period
        ]

        # Check current request count within the period
        current_count = sum(count for ts, count in self.user_requests[user_identifier])

        if current_count >= self.limit:
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please try again in {self.period - (current_time - self.user_requests[user_identifier][-1][0]) if self.user_requests[user_identifier] else self.period} seconds."
            )

        # Add the current request
        self.user_requests[user_identifier].append((current_time, 1))

        # Return a response object or None if no response is needed
        return JSONResponse(content={"message": "Request allowed."})
