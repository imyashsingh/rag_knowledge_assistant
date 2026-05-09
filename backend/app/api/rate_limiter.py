"""
Rate limiting middleware for RAG Knowledge Assistant backend
"""

import time
from typing import Dict, Optional, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.redis_client import RedisCache, redis_client
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-based rate limiting middleware"""

    def __init__(
        self,
        app,
        default_limit: int = 100,
        default_window: int = 60,
        redis_cache: Optional[RedisCache] = None
    ):
        super().__init__(app)
        self.default_limit = default_limit
        self.default_window = default_window
        self.redis_cache = redis_cache or RedisCache()

        # Rate limit configurations for different endpoints
        self.endpoint_configs = {
            # Authentication endpoints - stricter limits
            # 5 requests per 5 minutes
            "/api/v1/auth/register": {"limit": 5, "window": 300},
            # 10 requests per 5 minutes
            "/api/v1/auth/login": {"limit": 10, "window": 300},
            # 20 requests per 5 minutes
            "/api/v1/auth/refresh": {"limit": 20, "window": 300},

            # Document endpoints - moderate limits
            # 10 uploads per minute
            "/api/v1/documents/upload": {"limit": 10, "window": 60},
            # 100 requests per minute
            "/api/v1/documents/": {"limit": 100, "window": 60},

            # Chat endpoints - higher limits for good UX
            # 30 queries per minute
            "/api/v1/chat/query": {"limit": 30, "window": 60},
            # 50 requests per minute
            "/api/v1/chat/stats": {"limit": 50, "window": 60},

            # Health endpoints - very high limits
            # 1000 requests per minute
            "/api/v1/health/": {"limit": 1000, "window": 60},
        }

    async def dispatch(self, request: Request, call_next):
        """Process request through rate limiting"""

        # Get client identifier (IP address or user ID)
        client_id = self._get_client_id(request)

        # Get rate limit config for this endpoint
        path = request.url.path
        config = self._get_rate_limit_config(path)

        # Check rate limit
        is_allowed, remaining, reset_time = await self._check_rate_limit(
            client_id, path, config["limit"], config["window"]
        )

        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for {client_id} on {path}",
                extra={
                    "client_id": client_id,
                    "path": path,
                    "limit": config["limit"],
                    "window": config["window"]
                }
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "X-RateLimit-Limit": str(config["limit"]),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(config["window"])
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(config["limit"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        return response

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get user ID from JWT token if available
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from app.core.security import verify_access_token
                token = auth_header.split(" ")[1]
                payload = verify_access_token(token)
                user_id = payload.get("user_id")
                if user_id:
                    return f"user:{user_id}"
            except Exception:
                pass  # Fall back to IP-based limiting

        # Fall back to IP address
        client_ip = request.client.host
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Get the first IP in the list
            client_ip = forwarded_for.split(",")[0].strip()

        return f"ip:{client_ip}"

    def _get_rate_limit_config(self, path: str) -> Dict:
        """Get rate limit configuration for endpoint"""
        # Check exact match first
        if path in self.endpoint_configs:
            return self.endpoint_configs[path]

        # Check prefix matches
        for endpoint_path, config in self.endpoint_configs.items():
            if path.startswith(endpoint_path):
                return config

        # Default configuration
        return {"limit": self.default_limit, "window": self.default_window}

    async def _check_rate_limit(
        self,
        client_id: str,
        path: str,
        limit: int,
        window: int
    ) -> Tuple[bool, int, int]:
        """
        Check if request is allowed based on rate limit

        Returns:
            Tuple of (is_allowed, remaining_requests, reset_time)
        """
        current_time = int(time.time())
        window_start = current_time - window

        # Redis key for rate limiting
        key = f"rate_limit:{path}:{client_id}"

        try:
            # Get current request count and timestamps
            pipe = redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)  # Remove old entries
            pipe.zcard(key)  # Count current entries
            pipe.zrange(key, 0, 0)  # Get oldest timestamp
            results = pipe.execute()

            current_count = results[1]

            # Check if limit exceeded
            if current_count >= limit:
                # Get reset time (oldest request + window)
                oldest_timestamp = results[2]
                if oldest_timestamp:
                    reset_time = int(float(oldest_timestamp)) + window
                else:
                    reset_time = current_time + window

                return False, 0, reset_time

            # Add current request
            redis_client.zadd(
                key, {str(current_time): current_time})
            redis_client.expire(key, window)

            remaining = limit - (current_count + 1)
            reset_time = current_time + window

            return True, remaining, reset_time

        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # Fail open - allow request if Redis fails
            return True, limit, current_time + window


class RateLimiter:
    """Utility class for manual rate limiting"""

    def __init__(self, redis_cache: Optional[RedisCache] = None):
        self.redis_cache = redis_cache or RedisCache()

    def is_rate_limited(
        self,
        identifier: str,
        limit: int,
        window: int
    ) -> Tuple[bool, int, int]:
        """
        Check if identifier is rate limited

        Args:
            identifier: Unique identifier (user ID, IP, etc.)
            limit: Request limit
            window: Time window in seconds

        Returns:
            Tuple of (is_limited, remaining_requests, reset_time)
        """
        current_time = int(time.time())
        window_start = current_time - window

        key = f"rate_limit:custom:{identifier}"

        try:
            pipe = redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zrange(key, 0, 0)
            results = pipe.execute()

            current_count = results[1]

            if current_count >= limit:
                oldest_timestamp = results[2]
                if oldest_timestamp:
                    reset_time = int(float(oldest_timestamp)) + window
                else:
                    reset_time = current_time + window

                return True, 0, reset_time

            # Add current request
            redis_client.zadd(
                key, {str(current_time): current_time})
            redis_client.expire(key, window)

            remaining = limit - (current_count + 1)
            reset_time = current_time + window

            return False, remaining, reset_time

        except Exception as e:
            logger.error(f"Manual rate limiting error: {str(e)}")
            # Fail open
            return False, limit, current_time + window

    def clear_rate_limit(self, identifier: str) -> bool:
        """Clear rate limit for identifier"""
        try:
            key = f"rate_limit:custom:{identifier}"
            return self.redis_cache.delete(key)
        except Exception as e:
            logger.error(f"Error clearing rate limit: {str(e)}")
            return False

    def get_rate_limit_info(self, identifier: str) -> Dict:
        """Get rate limit information for identifier"""
        try:
            key = f"rate_limit:custom:{identifier}"
            pipe = redis_client.pipeline()
            pipe.zcard(key)
            pipe.ttl(key)
            results = pipe.execute()

            return {
                "current_requests": results[0],
                "ttl": results[1]
            }
        except Exception as e:
            logger.error(f"Error getting rate limit info: {str(e)}")
            return {"current_requests": 0, "ttl": 0}


# Global rate limiter instance
rate_limiter = RateLimiter()
