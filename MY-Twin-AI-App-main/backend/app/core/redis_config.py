"""Redis config v2.0 – اتصال قوي وجاهز للإنتاج"""
import os, logging
import redis
from redis import ConnectionPool

logger = logging.getLogger("redis_config")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

try:
    pool = ConnectionPool.from_url(
        REDIS_URL,
        max_connections=100,
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5,
        retry_on_timeout=True,
    )
    redis_client = redis.Redis(connection_pool=pool)
    redis_client.ping()
    REDIS_AVAILABLE = True
    logger.info("✅ Redis connected for production scaling")
except Exception as e:
    logger.warning(f"⚠️ Redis not available: {e}")
    REDIS_AVAILABLE = False
    redis_client = None

def get_redis():
    """استدعاء آمن لـ Redis"""
    return redis_client if REDIS_AVAILABLE else None
