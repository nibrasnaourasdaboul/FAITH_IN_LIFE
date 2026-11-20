import logging

from redis.asyncio import Redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)
_client: Redis | None = None


# يحاول الاتصال بذاكرة التخزين المؤقت ويتجاوزها إذا كانت متوقفة.
async def get_redis() -> Redis | None:
    global _client
    if _client is not None:
        return _client
    try:
        client = Redis.from_url(get_settings().redis_url, decode_responses=True)
        await client.ping()
        _client = client
        return client
    except Exception as exc:  # Redis is helpful, not mandatory for local auth.
        logger.warning("Redis unavailable, continuing with database-backed tokens: %s", exc)
        return None


# يغلق اتصال ذاكرة التخزين المؤقت عند إيقاف الخادم.
async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
