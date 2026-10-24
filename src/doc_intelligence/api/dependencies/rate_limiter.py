from fastapi import Request, HTTPException
import time
from collections import deque

class RateLimiter:
    def __init__(self, requests_per_unit: int, unit_seconds: int):
        self.requests_per_unit = requests_per_unit
        self.unit_seconds = unit_seconds
        self.requests = {}  # client_ip -> deque of timestamps

    def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = deque()
            
        # Remove old requests
        while self.requests[client_ip] and self.requests[client_ip][0] < now - self.unit_seconds:
            self.requests[client_ip].popleft()
            
        if len(self.requests[client_ip]) >= self.requests_per_unit:
            raise HTTPException(status_code=429, detail="Too many requests")
            
        self.requests[client_ip].append(now)
