from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from typing import Dict
import time

class RateLimiter:
    """
    FastAPI dependency that enforces a request rate limit per client IP.

    Parameters
    ----------
    requests_per_unit: int
        Maximum number of requests allowed within the time window.
    unit_seconds: int
        Length of the time window in seconds.
    """

    def __init__(self, requests_per_unit: int, unit_seconds: int):
        if not isinstance(requests_per_unit, int) or requests_per_unit <= 0:
            raise ValueError("requests_per_unit must be a positive integer")
        if not isinstance(unit_seconds, int) or unit_seconds <= 0:
            raise ValueError("unit_seconds must be a positive integer")

        self.requests_per_unit = requests_per_unit
        self.unit_seconds = unit_seconds
        # Mapping of client IP -> {"count": int, "timestamp": float}
        self._request_counts: Dict[str, Dict[str, float]] = {}

    async def __call__(self, request: Request):
        """
        FastAPI calls this dependency for each request.

        Raises
        ------
        HTTPException
            If the client exceeds the allowed request rate.
        """
        client_host = request.client.host if request.client else "unknown"
        now = time.time()

        client_data = self._request_counts.setdefault(
            client_host, {"count": 0, "timestamp": now}
        )
        elapsed = now - client_data["timestamp"]

        # Reset count if the time window has passed
        if elapsed > self.unit_seconds:
            client_data["count"] = 0
            client_data["timestamp"] = now
            elapsed = 0

        if client_data["count"] >= self.requests_per_unit:
            retry_after = int(client_data["timestamp"] + self.unit_seconds - now)
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            )

        client_data["count"] += 1
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from typing import Dict
import time

class RateLimiter:
    """
    FastAPI dependency that enforces a request rate limit per client IP.

    Parameters
    ----------
    requests_per_unit: int
        Maximum number of requests allowed within the time window.
    unit_seconds: int
        Length of the time window in seconds.
    """

    def __init__(self, requests_per_unit: int, unit_seconds: int):
        if not isinstance(requests_per_unit, int) or requests_per_unit <= 0:
            raise ValueError("requests_per_unit must be a positive integer")
        if not isinstance(unit_seconds, int) or unit_seconds <= 0:
            raise ValueError("unit_seconds must be a positive integer")

        self.requests_per_unit = requests_per_unit
        self.unit_seconds = unit_seconds
        # Mapping of client IP -> {"count": int, "timestamp": float}
        self._request_counts: Dict[str, Dict[str, float]] = {}

    async def __call__(self, request: Request):
        """
        FastAPI calls this dependency for each request.

        Raises
        ------
        HTTPException
            If the client exceeds the allowed request rate.
        """
        client_host = request.client.host if request.client else "unknown"
        now = time.time()

        client_data = self._request_counts.setdefault(
            client_host, {"count": 0, "timestamp": now}
        )
        elapsed = now - client_data["timestamp"]

        # Reset count if the time window has passed
        if elapsed > self.unit_seconds:
            client_data["count"] = 0
            client_data["timestamp"] = now
            elapsed = 0

        if client_data["count"] >= self.requests_per_unit:
            retry_after = int(client_data["timestamp"] + self.unit_seconds - now)
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            )

        client_data["count"] += 1
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from typing import Dict
import time

class RateLimiter:
    """
    Manages API rate limiting to prevent abuse and ensure fair usage.

    This class tracks incoming requests per client (identified by IP address)
    and enforces limits based on a configurable number of requests within a
    specific time unit.

    Attributes:
        requests_per_unit (int): The maximum number of requests allowed within the unit period.
        unit_seconds (int): The duration of the time unit in seconds.
        _request_counts (Dict[str, Dict[str, float]]): A dictionary storing request counts and timestamps
                                                      for each IP address.
    """
    def __init__(self, requests_per_unit: int, unit_seconds: int):
        if not isinstance(requests_per_unit, int) or requests_per_unit <= 0:
            raise ValueError("requests_per_unit must be a positive integer")
        if not isinstance(unit_seconds, int) or unit_seconds <= 0:
            raise ValueError("unit_seconds must be a positive integer")

        self.requests_per_unit = requests_per_unit
        self.unit_seconds = unit_seconds
        self._request_counts: Dict[str, Dict] = {}

    def __call__(self, request: Request):
        client_host = request.client.host if request.client else "unknown"
        current_time = time.time()

        if client_host not in self._request_counts:
            self._request_counts[client_host] = {"count": 0, "timestamp": current_time}

        client_data = self._request_counts[client_host]
        time_diff = current_time - client_data["timestamp"]

        if time_diff > self.unit_seconds:
            client_data["count"] = 0
            client_data["timestamp"] = current_time
            time_diff = 0

        if client_data["count"] >= self.requests_per_unit:
            reset_time = client_data["timestamp"] + self.unit_seconds - current_time
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please try again in {int(reset_time)} seconds.",
            )

        client_data["count"] += 1
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from typing import Dict
import time

class RateLimiter:
    """
    Manages API rate limiting to prevent abuse and ensure fair usage.

    This class tracks incoming requests per client (identified by IP address)
    and enforces limits based on a configurable number of requests within a
    specific time unit.

    Attributes:
        requests_per_unit (int): The maximum number of requests allowed within the unit period.
        unit_seconds (int): The duration of the time unit in seconds.
        _request_counts (Dict[str, Dict[str, float]]): A dictionary storing request counts and timestamps
                                                      for each IP address.
    """
    def __init__(self, requests_per_unit: int, unit_seconds: int):
        if not isinstance(requests_per_unit, int) or requests_per_unit <= 0:
            raise ValueError("requests_per_unit must be a positive integer")
        if not isinstance(unit_seconds, int) or unit_seconds <= 0:
            raise ValueError("unit_seconds must be a positive integer")

        self.requests_per_unit = requests_per_unit
        self.unit_seconds = unit_seconds
        self._request_counts: Dict[str, Dict] = {}

    def __call__(self, request: Request):
        client_host = request.client.host if request.client else "unknown"
        current_time = time.time()

        if client_host not in self._request_counts:
            self._request_counts[client_host] = {"count": 0, "timestamp": current_time}

        client_data = self._request_counts[client_host]
        time_diff = current_time - client_data["timestamp"]

        if time_diff > self.unit_seconds:
            client_data["count"] = 0
            client_data["timestamp"] = current_time
            time_diff = 0

        if client_data["count"] >= self.requests_per_unit:
            reset_time = client_data["timestamp"] + self.unit_seconds - current_time
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please try again in {int(reset_time)} seconds.",
            )

        client_data["count"] += 1
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from typing import Dict
import time

class RateLimiter:
    """
    Manages API rate limiting to prevent abuse and ensure fair usage.

    This class tracks incoming requests per client (identified by IP address)
    and enforces limits based on a configurable number of requests within a
    specific time unit.

    Attributes:
        requests_per_unit (int): The maximum number of requests allowed within the unit period.
        unit_seconds (int): The duration of the time unit in seconds.
        _request_counts (Dict[str, Dict[str, float]]): A dictionary storing request counts and timestamps
                                                      for each IP address.
    """
    def __init__(self, requests_per_unit: int, unit_seconds: int):
        if not isinstance(requests_per_unit, int) or requests_per_unit <= 0:
            raise ValueError("requests_per_unit must be a positive integer")
        if not isinstance(unit_seconds, int) or unit_seconds <= 0:
            raise ValueError("unit_seconds must be a positive integer")

        self.requests_per_unit = requests_per_unit
        self.unit_seconds = unit_seconds
        self._request_counts: Dict[str, Dict] = {}

    def __call__(self, request: Request):
        client_host = request.client.host if request.client else "unknown"
        current_time = time.time()

        if client_host not in self._request_counts:
            self._request_counts[client_host] = {"count": 0, "timestamp": current_time}

        client_data = self._request_counts[client_host]
        time_diff = current_time - client_data["timestamp"]

        if time_diff > self.unit_seconds:
            client_data["count"] = 0
            client_data["timestamp"] = current_time
            time_diff = 0

        if client_data["count"] >= self.requests_per_unit:
            reset_time = client_data["timestamp"] + self.unit_seconds - current_time
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please try again in {int(reset_time)} seconds.",
            )

        client_data["count"] += 1
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from typing import Dict
import time

class RateLimiter:
    """
    Manages API rate limiting to prevent abuse and ensure fair usage.

    This class tracks incoming requests per client (identified by IP address)
    and enforces limits based on a configurable number of requests within a
    specific time unit.

    Attributes:
        requests_per_unit (int): The maximum number of requests allowed within the unit period.
        unit_seconds (int): The duration of the time unit in seconds.
        _request_counts (Dict[str, Dict[str, float]]): A dictionary storing request counts and timestamps
                                                      for each IP address.
    """
    def __init__(self, requests_per_unit: int, unit_seconds: int):
        if not isinstance(requests_per_unit, int) or requests_per_unit <= 0:
            raise ValueError("requests_per_unit must be a positive integer")
        if not isinstance(unit_seconds, int) or unit_seconds <= 0:
            raise ValueError("unit_seconds must be a positive integer")

        self.requests_per_unit = requests_per_unit
        self.unit_seconds = unit_seconds
        self._request_counts: Dict[str, Dict] = {}

    def __call__(self, request: Request):
        client_host = request.client.host if request.client else "unknown"
        current_time = time.time()

        if client_host not in self._request_counts:
            self._request_counts[client_host] = {"count": 0, "timestamp": current_time}

        client_data = self._request_counts[client_host]
        time_diff = current_time - client_data["timestamp"]

        if time_diff > self.unit_seconds:
            client_data["count"] = 0
            client_data["timestamp"] = current_time
            time_diff = 0

        if client_data["count"] >= self.requests_per_unit:
            reset_time = client_data["timestamp"] + self.unit_seconds - current_time
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please try again in {int(reset_time)} seconds.",
            )

        client_data["count"] += 1
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from typing import Dict
import time

class RateLimiter:
    """
    Manages API rate limiting to prevent abuse and ensure fair usage.

    This class tracks incoming requests per client (identified by IP address)
    and enforces limits based on a configurable number of requests within a
    specific time unit.

    Attributes:
        requests_per_unit (int): The maximum number of requests allowed within the unit period.
        unit_seconds (int): The duration of the time unit in seconds.
        _request_counts (Dict[str, Dict[str, float]]): A dictionary storing request counts and timestamps
                                                      for each IP address.
    """
    def __init__(self, requests_per_unit: int, unit_seconds: int):
        if not isinstance(requests_per_unit, int) or requests_per_unit <= 0:
            raise ValueError("requests_per_unit must be a positive integer")
        if not isinstance(unit_seconds, int) or unit_seconds <= 0:
            raise ValueError("unit_seconds must be a positive integer")

        self.requests_per_unit = requests_per_unit
        self.unit_seconds = unit_seconds
        self._request_counts: Dict[str, Dict] = {}

    def __call__(self, request: Request):
        client_host = request.client.host if request.client else "unknown"
        current_time = time.time()

        if client_host not in self._request_counts:
            self._request_counts[client_host] = {"count": 0, "timestamp": current_time}

        client_data = self._request_counts[client_host]
        time_diff = current_time - client_data["timestamp"]

        if time_diff > self.unit_seconds:
            client_data["count"] = 0
            client_data["timestamp"] = current_time
            time_diff = 0

        if client_data["count"] >= self.requests_per_unit:
            reset_time = client_data["timestamp"] + self.unit_seconds - current_time
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please try again in {int(reset_time)} seconds.",
            )

        client_data["count"] += 1
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from typing import Dict
import time

class RateLimiter:
    """
    Manages API rate limiting to prevent abuse and ensure fair usage.

    This class tracks incoming requests per client (identified by IP address)
    and enforces limits based on a configurable number of requests within a
    specific time unit.

    Attributes:
        requests_per_unit (int): The maximum number of requests allowed within the unit period.
        unit_seconds (int): The duration of the time unit in seconds.
        _request_counts (Dict[str, Dict[str, float]]): A dictionary storing request counts and timestamps
                                                      for each IP address.
    """
    def __init__(self, requests_per_unit: int, unit_seconds: int):
        if not isinstance(requests_per_unit, int) or requests_per_unit <= 0:
            raise ValueError("requests_per_unit must be a positive integer")
        if not isinstance(unit_seconds, int) or unit_seconds <= 0:
            raise ValueError("unit_seconds must be a positive integer")

        self.requests_per_unit = requests_per_unit
        self.unit_seconds = unit_seconds
        self._request_counts: Dict[str, Dict] = {}

    def __call__(self, request: Request):
        client_host = request.client.host if request.client else "unknown"
        current_time = time.time()

        if client_host not in self._request_counts:
            self._request_counts[client_host] = {"count": 0, "timestamp": current_time}

        client_data = self._request_counts[client_host]
        time_diff = current_time - client_data["timestamp"]

        if time_diff > self.unit_seconds:
            client_data["count"] = 0
            client_data["timestamp"] = current_time
            time_diff = 0

        if client_data["count"] >= self.requests_per_unit:
            reset_time = client_data["timestamp"] + self.unit_seconds - current_time
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please try again in {int(reset_time)} seconds.",
            )

        client_data["count"] += 1
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from typing import Dict
import time

class RateLimiter:
    """
    Manages API rate limiting to prevent abuse and ensure fair usage.

    This class tracks incoming requests per client (identified by IP address)
    and enforces limits based on a configurable number of requests within a
    specific time unit.

    Attributes:
        requests_per_unit (int): The maximum number of requests allowed within the unit period.
        unit_seconds (int): The duration of the time unit in seconds.
        _request_counts (Dict[str, Dict[str, float]]): A dictionary storing request counts and timestamps
                                                      for each IP address.
    """
    def __init__(self, requests_per_unit: int, unit_seconds: int):
        if not isinstance(requests_per_unit, int) or requests_per_unit <= 0:
            raise ValueError("requests_per_unit must be a positive integer")
        if not isinstance(unit_seconds, int) or unit_seconds <= 0:
            raise ValueError("unit_seconds must be a positive integer")

        self.requests_per_unit = requests_per_unit
        self.unit_seconds = unit_seconds
        self._request_counts: Dict[str, Dict] = {}

    def __call__(self, request: Request):
        client_host = request.client.host if request.client else "unknown"
        current_time = time.time()

        if client_host not in self._request_counts:
            self._request_counts[client_host] = {"count": 0, "timestamp": current_time}

        client_data = self._request_counts[client_host]
        time_diff = current_time - client_data["timestamp"]

        if time_diff > self.unit_seconds:
            client_data["count"] = 0
            client_data["timestamp"] = current_time
            time_diff = 0

        if client_data["count"] >= self.requests_per_unit:
            reset_time = client_data["timestamp"] + self.unit_seconds - current_time
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please try again in {int(reset_time)} seconds.",
            )

        client_data["count"] += 1
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from typing import Dict
import time

class RateLimiter:
    """
    Manages API rate limiting to prevent abuse and ensure fair usage.

    This class tracks incoming requests per client (identified by IP address)
    and enforces limits based on a configurable number of requests within a
    specific time unit.

    Attributes:
        requests_per_unit (int): The maximum number of requests allowed within the unit period.
        unit_seconds (int): The duration of the time unit in seconds.
        _request_counts (Dict[str, Dict[str, float]]): A dictionary storing request counts and timestamps
                                                      for each IP address.
    """
    def __init__(self, requests_per_unit: int, unit_seconds: int):
        if not isinstance(requests_per_unit, int) or requests_per_unit <= 0:
            raise ValueError("requests_per_unit must be a positive integer")
        if not isinstance(unit_seconds, int) or unit_seconds <= 0:
            raise ValueError("unit_seconds must be a positive integer")

        self.requests_per_unit = requests_per_unit
        self.unit_seconds = unit_seconds
        self._request_counts: Dict[str, Dict] = {}

    def __call__(self, request: Request):
        client_host = request.client.host if request.client else "unknown"
        current_time = time.time()

        if client_host not in self._request_counts:
            self._request_counts[client_host] = {"count": 0, "timestamp": current_time}

        client_data = self._request_counts[client_host]
        time_diff = current_time - client_data["timestamp"]

        if time_diff > self.unit_seconds:
            client_data["count"] = 0
            client_data["timestamp"] = current_time
            time_diff = 0

        if client_data["count"] >= self.requests_per_unit:
            reset_time = client_data["timestamp"] + self.unit_seconds - current_time
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please try again in {int(reset_time)} seconds.",
            )

        client_data["count"] += 1
