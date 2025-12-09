import redis.asyncio as redis
from app.config import get_settings
from typing import Optional
import json


class CacheService:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.settings = get_settings()

    async def connect(self):
        """Initialize Redis connection"""
        self.redis = await redis.from_url(
            self.settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[dict]:
        """Get value from cache"""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: dict, ttl: Optional[int] = None):
        """Set value in cache with optional TTL"""
        if ttl is None:
            ttl = self.settings.cache_ttl

        await self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )

    async def delete(self, key: str):
        """Delete key from cache"""
        await self.redis.delete(key)

    async def get_stats(self) -> dict:
        """Get cache statistics"""
        info = await self.redis.info()
        dbsize = await self.redis.dbsize()

        return {
            "redis_keys": dbsize,
            "memory_used": info.get("used_memory_human", "N/A"),
            "connected_clients": info.get("connected_clients", 0)
        }

    async def health_check(self) -> bool:
        """Check if Redis is healthy"""
        try:
            await self.redis.ping()
            return True
        except Exception:
            return False

    async def clear_all(self):
        """Clear all keys (use with caution!)"""
        await self.redis.flushdb()


# Global cache instance
cache_service = CacheService()
