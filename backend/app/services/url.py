import secrets
from urllib.parse import urlparse
from uuid import UUID

import redis.asyncio as aioredis

from app.core.config import settings
from app.models.url import URL
from app.repositories.url import URLRepository

# All valid characters for generating a short code (base62)
BASE62_CHARACTERS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

# The Redis key format for a cached short code
# Example: "url:abc123" -> "https://google.com"
CACHE_KEY_PREFIX = "url:"
CACHE_COUNTER_PREFIX = "clicks:"

class URLService:
    def __init__(self, repository: URLRepository, redis: aioredis.Redis):
        self.repository = repository
        self.redis = redis

    def validate_url(self, url: str) -> None:
        if not url:
            raise ValueError("URL cannot be empty")
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("URL must contain a scheme and a domain")
            if parsed.scheme not in ("http", "https"):
                raise ValueError("URL scheme must be http or https")
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"Invalid URL format: {str(e)}")

    def generate_short_code(self, length: int = 6) -> str:
        return "".join(secrets.choice(BASE62_CHARACTERS) for _ in range(length))

    async def create_url(self, original_url: str) -> URL:
        self.validate_url(original_url)

        # Try up to 5 times to find a unique short code
        short_code = None
        for _ in range(5):
            candidate = self.generate_short_code()
            existing = await self.repository.get_by_short_code(candidate)
            if not existing:
                short_code = candidate
                break
        if not short_code:
            raise RuntimeError("Failed to generate a unique short code after several attempts")
        return await self.repository.create(original_url=original_url, short_code=short_code)

    async def redirect_lookup(self, short_code: str) -> str | None:
        """
        HOT LINK CACHING — Cache-aside pattern:
        1. Check Redis first (very fast, in-memory lookup)
        2. Cache HIT  → use the cached original_url, still update click_count in DB
        3. Cache MISS → go to DB, cache the result for next time, update click_count
        """
        cache_key = CACHE_KEY_PREFIX + short_code
        counter_key = CACHE_COUNTER_PREFIX + short_code
        # Step 1: Check Redis cache
        cached_original_url = await self.redis.get(cache_key)

        if cached_original_url:
            # --- Cache HIT ---
            # We already know where to redirect without touching the DB.
            # We still need to hit the DB just for the click_count increment,
            # but the expensive "find this URL" lookup is skipped on hot links.
            await self.redis.incr(counter_key)
            return cached_original_url

        # --- Cache MISS ---
        # Step 2: Not in cache, go to the database
        url = await self.repository.get_by_short_code(short_code)
        if url is None:
            return None  # Short code doesn't exist at all

        # Step 3: Store the original URL in Redis so the next request is fast
        await self.redis.set(
            cache_key,
            url.original_url,
            ex=settings.CACHE_TTL_SECONDS,  # Auto-expires after N seconds (default 5 min)
        )
        await self.redis.incr(counter_key)


        return url.original_url


    async def get_all_urls_with_live_counts(self, skip: int = 0, limit: int = 100) -> list[dict]:
        """
        Returns all URLs with click counts read live from Redis.
        Uses a single MGET to fetch all counters in one round-trip.
        Falls back to the DB value (0) for any URL not yet in Redis.
        """
        urls = await self.repository.get_all(skip=skip, limit=limit)
        if not urls:
            return []

        # One network call to Redis instead of N individual GETs
        counter_keys = [CACHE_COUNTER_PREFIX + url.short_code for url in urls]
        redis_counts = await self.redis.mget(*counter_keys)

        result = []
        for url, redis_count in zip(urls, redis_counts):
            result.append({
                "id": url.id,
                "original_url": url.original_url,
                "short_code": url.short_code,
                "created_at": url.created_at,
                # Redis count wins; fall back to DB value if key doesn't exist yet
                "click_count": int(redis_count) if redis_count is not None else url.click_count,
            })
        return result

    async def delete_url(self, short_code: str) -> bool:
        deleted = await self.repository.delete(short_code)
        if deleted:
            # Remove from cache too, so stale data doesn't linger
            await self.redis.delete(CACHE_KEY_PREFIX + short_code)
            await self.redis.delete(CACHE_COUNTER_PREFIX + short_code)
        return deleted

    async def delete_url_by_id(self, id: UUID) -> bool:
        # First fetch the URL so we know its short_code (needed to clear cache)
        url = await self.repository.db.get(URL, id)
        if url is None:
            return False

        short_code = url.short_code
        deleted = await self.repository.delete_by_id(id)

        if deleted:
            # Remove from cache so stale data doesn't linger
            await self.redis.delete(CACHE_KEY_PREFIX + short_code)
            await self.redis.delete(CACHE_COUNTER_PREFIX + short_code)

        return deleted
