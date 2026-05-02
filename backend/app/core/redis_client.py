import redis
import json
import logging
from typing import Optional, Any, Union
from app.config import settings

logger = logging.getLogger(__name__)

# Redis connection with connection pooling and error handling
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=6379,
    password=settings.REDIS_PASSWORD,
    ssl=True,
    decode_responses=True,  # Automatically decode responses
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30
)


class RedisCache:
    """Redis cache manager with proper error handling and TTL management"""

    # Cache TTL constants (in seconds)
    EMBEDDING_TTL = 86400      # 24 hours
    RAG_RESPONSE_TTL = 300     # 5 minutes
    REFRESH_TOKEN_TTL = 604800  # 7 days

    @staticmethod
    def get(key: str) -> Optional[str]:
        """Get value from Redis"""
        try:
            return redis_client.get(key)
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {str(e)}")
            return None

    @staticmethod
    def set(key: str, value: Union[str, dict, list], ex: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiry"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return redis_client.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {str(e)}")
            return False

    @staticmethod
    def delete(key: str) -> bool:
        """Delete key from Redis"""
        try:
            return redis_client.delete(key) > 0
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {str(e)}")
            return False

    @staticmethod
    def exists(key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            return redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {str(e)}")
            return False

    @staticmethod
    def keys(pattern: str) -> list:
        """Get keys matching pattern"""
        try:
            return redis_client.keys(pattern)
        except Exception as e:
            logger.error(f"Redis keys error for pattern {pattern}: {str(e)}")
            return []

    @staticmethod
    def clear_pattern(pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            keys = redis_client.keys(pattern)
            if keys:
                return redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis clear pattern error for {pattern}: {str(e)}")
            return 0

    @staticmethod
    def get_json(key: str) -> Optional[Any]:
        """Get JSON value from Redis"""
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get_json error for key {key}: {str(e)}")
            return None

    @staticmethod
    def set_json(key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set JSON value in Redis"""
        try:
            return redis_client.set(key, json.dumps(value), ex=ex)
        except Exception as e:
            logger.error(f"Redis set_json error for key {key}: {str(e)}")
            return False

    @staticmethod
    def ping() -> bool:
        """Check Redis connection"""
        try:
            return redis_client.ping()
        except Exception as e:
            logger.error(f"Redis ping error: {str(e)}")
            return False

    @staticmethod
    def get_cache_stats() -> dict:
        """Get Redis cache statistics"""
        try:
            info = redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            logger.error(f"Redis stats error: {str(e)}")
            return {}


def test_redis_connection() -> bool:
    """Test Redis connection and configuration"""
    try:
        # Test basic connectivity
        if not RedisCache.ping():
            logger.error("Redis ping failed")
            return False

        # Test set/get operations
        test_key = "test:connection"
        test_value = "test_value"

        if not RedisCache.set(test_key, test_value, ex=10):
            logger.error("Redis set test failed")
            return False

        retrieved = RedisCache.get(test_key)
        if retrieved != test_value:
            logger.error("Redis get test failed")
            return False

        # Clean up
        RedisCache.delete(test_key)

        logger.info("Redis connection test successful")
        return True

    except Exception as e:
        logger.error(f"Redis connection test failed: {str(e)}")
        return False
