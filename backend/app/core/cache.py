from typing import Optional, Any, Union
import hashlib
import json
import logging
from app.core.redis_client import RedisCache

logger = logging.getLogger(__name__)


class CacheManager:
    """High-level cache manager with different caching strategies"""

    @staticmethod
    def get_embedding_cache(text: str) -> Optional[list[float]]:
        """Get cached embedding for text"""
        key = f"embed:{hashlib.md5(text.encode()).hexdigest()}"
        cached = RedisCache.get(key)
        if cached:
            try:
                return json.loads(cached)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in embedding cache for key: {key}")
        return None

    @staticmethod
    def set_embedding_cache(text: str, embedding: list[float]) -> bool:
        """Cache embedding for text"""
        key = f"embed:{hashlib.md5(text.encode()).hexdigest()}"
        return RedisCache.set_json(key, embedding, ex=RedisCache.EMBEDDING_TTL)

    @staticmethod
    def get_rag_cache(query: str, workspace_id: int) -> Optional[dict]:
        """Get cached RAG response"""
        key = f"rag:{hashlib.md5(f'{query}:{workspace_id}'.encode()).hexdigest()}"
        return RedisCache.get_json(key)

    @staticmethod
    def set_rag_cache(query: str, workspace_id: int, response: dict) -> bool:
        """Cache RAG response"""
        key = f"rag:{hashlib.md5(f'{query}:{workspace_id}'.encode()).hexdigest()}"
        return RedisCache.set_json(key, response, ex=RedisCache.RAG_RESPONSE_TTL)

    @staticmethod
    def invalidate_workspace_cache(workspace_id: int) -> int:
        """Invalidate all cache entries for a workspace"""
        patterns = [
            f"rag:*{workspace_id}*",
            f"embed:*",  # Embeddings are shared across workspaces
        ]

        total_cleared = 0
        for pattern in patterns:
            total_cleared += RedisCache.clear_pattern(pattern)

        return total_cleared

    @staticmethod
    def get_cache_hit_rate() -> dict:
        """Get cache hit rate statistics"""
        stats = RedisCache.get_cache_stats()
        hits = stats.get("keyspace_hits", 0)
        misses = stats.get("keyspace_misses", 0)
        total = hits + misses

        hit_rate = (hits / total * 100) if total > 0 else 0

        return {
            "hit_rate": round(hit_rate, 2),
            "hits": hits,
            "misses": misses,
            "total_requests": total
        }

    @staticmethod
    def cache_user_session(user_id: int, session_data: dict) -> bool:
        """Cache user session data"""
        key = f"session:{user_id}"
        return RedisCache.set_json(key, session_data, ex=3600)  # 1 hour

    @staticmethod
    def get_user_session(user_id: int) -> Optional[dict]:
        """Get cached user session"""
        key = f"session:{user_id}"
        return RedisCache.get_json(key)

    @staticmethod
    def cache_api_rate_limit(identifier: str, count: int, window: int = 60) -> bool:
        """Cache API rate limit counter"""
        key = f"rate_limit:{identifier}"
        return RedisCache.set(key, str(count), ex=window)

    @staticmethod
    def get_api_rate_limit(identifier: str) -> Optional[int]:
        """Get API rate limit counter"""
        key = f"rate_limit:{identifier}"
        value = RedisCache.get(key)
        return int(value) if value else None


# Backward compatibility functions
def get_cache(key: str) -> Optional[Any]:
    """Get value from cache (backward compatibility)"""
    return RedisCache.get_json(key)


def set_cache(key: str, value: Any, ttl: int = 300) -> bool:
    """Set value in cache (backward compatibility)"""
    return RedisCache.set_json(key, value, ex=ttl)


def delete_cache(key: str) -> bool:
    """Delete cache entry"""
    return RedisCache.delete(key)


def clear_cache_pattern(pattern: str) -> int:
    """Clear cache entries matching pattern"""
    return RedisCache.clear_pattern(pattern)
