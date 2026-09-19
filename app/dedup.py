import logging
import redis

from app.config import settings

logger = logging.getLogger("dedup")

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def is_duplicate(tx_hash: str) -> bool:
    """
    Checks whether this transaction has already been flagged as a whale
    alert. Uses Redis SETNX (set-if-not-exists) so the check and the
    mark happen atomically, avoiding a race where two workers both
    think a tx hasn't been seen yet.
    """
    key = f"whale_seen:{tx_hash}"
    was_set = redis_client.set(key, "1", nx=True, ex=settings.redis_dedup_ttl_seconds)
    return not was_set  # if it was NOT set, it means the key already existed


def dedup_health_check() -> bool:
    """Returns True if Redis is reachable."""
    try:
        redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False
