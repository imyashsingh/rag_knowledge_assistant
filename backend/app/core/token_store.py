from typing import Optional
from app.core.redis_client import redis_client


def store_refresh_token(user_id: int, token: str) -> None:
    """Store refresh token in Redis with 7-day expiry"""
    redis_client.set(f"refresh_token:{user_id}",
                     token, ex=604800)  # 7 days in seconds


def get_refresh_token(user_id: int) -> Optional[str]:
    """Get refresh token from Redis"""
    token = redis_client.get(f"refresh_token:{user_id}")
    return token.decode() if token else None


def delete_refresh_token(user_id: int) -> bool:
    """Delete refresh token from Redis"""
    result = redis_client.delete(f"refresh_token:{user_id}")
    return result > 0


def validate_refresh_token(user_id: int, token: str) -> bool:
    """Validate refresh token against stored token"""
    stored_token = get_refresh_token(user_id)
    return stored_token == token
