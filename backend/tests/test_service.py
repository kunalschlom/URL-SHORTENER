import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.url import URLService
from app.repositories.url import URLRepository
from app.models.url import URL


def make_service(repo=None, redis=None):
    """Helper to create a URLService with sensible mock defaults."""
    if repo is None:
        repo = MagicMock(spec=URLRepository)
    if redis is None:
        redis = AsyncMock()
    return URLService(repository=repo, redis=redis)


def test_validate_url_valid():
    service = make_service()
    service.validate_url("https://example.com")
    service.validate_url("http://example.com/path?query=1")


def test_validate_url_invalid():
    service = make_service()
    with pytest.raises(ValueError):
        service.validate_url("invalid-url")
    with pytest.raises(ValueError):
        service.validate_url("ftp://example.com")
    with pytest.raises(ValueError):
        service.validate_url("")


def test_generate_short_code_length():
    service = make_service()
    code = service.generate_short_code()
    assert len(code) == 6
    assert all(c in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" for c in code)


@pytest.mark.asyncio
async def test_create_url_success():
    repo = MagicMock(spec=URLRepository)
    repo.get_by_short_code = AsyncMock(return_value=None)
    repo.create = AsyncMock(return_value=URL(original_url="https://google.com", short_code="abcde1"))
    service = make_service(repo=repo)
    url = await service.create_url("https://google.com")

    assert url is not None
    repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_url_collision_retry():
    repo = MagicMock(spec=URLRepository)
    repo.get_by_short_code = AsyncMock(
        side_effect=[URL(original_url="https://other.com", short_code="coll1"), None]
    )
    repo.create = AsyncMock(return_value=URL(original_url="https://google.com", short_code="abcde2"))

    service = make_service(repo=repo)
    url = await service.create_url("https://google.com")

    assert url is not None
    assert repo.get_by_short_code.call_count == 2
    repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_url_max_collisions():
    repo = MagicMock(spec=URLRepository)
    repo.get_by_short_code = AsyncMock(
        return_value=URL(original_url="https://other.com", short_code="coll")
    )

    service = make_service(repo=repo)
    with pytest.raises(RuntimeError):
        await service.create_url("https://google.com")


@pytest.mark.asyncio
async def test_redirect_lookup_cache_miss():
    """On a cache MISS the service should hit the DB, cache the result, and return the URL string."""
    db_url = URL(original_url="https://google.com", short_code="google", click_count=0)
    repo = MagicMock(spec=URLRepository)
    repo.get_by_short_code = AsyncMock(return_value=db_url)

    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)  # cache MISS

    service = make_service(repo=repo, redis=redis)
    result = await service.redirect_lookup("google")

    assert result == "https://google.com"
    redis.set.assert_called_once()   # URL should have been cached
    redis.incr.assert_called_once()  # Click counter should have been incremented


@pytest.mark.asyncio
async def test_redirect_lookup_cache_hit():
    """On a cache HIT the service should return immediately without touching the DB."""
    repo = MagicMock(spec=URLRepository)

    redis = AsyncMock()
    redis.get = AsyncMock(return_value="https://google.com")  # cache HIT

    service = make_service(repo=repo, redis=redis)
    result = await service.redirect_lookup("google")

    assert result == "https://google.com"
    repo.get_by_short_code.assert_not_called()  # DB should NOT be hit
    redis.incr.assert_called_once()             # Click counter should still be incremented


@pytest.mark.asyncio
async def test_redirect_lookup_not_found():
    """When the short code doesn't exist in cache or DB, return None."""
    repo = MagicMock(spec=URLRepository)
    repo.get_by_short_code = AsyncMock(return_value=None)

    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)  # cache MISS

    service = make_service(repo=repo, redis=redis)
    result = await service.redirect_lookup("noexist")

    assert result is None
    redis.set.assert_not_called()   # Nothing to cache
    redis.incr.assert_not_called()  # No click to count


@pytest.mark.asyncio
async def test_get_all_urls_with_live_counts():
    """
    Redis counter should override the stale DB click_count.
    URLs with no Redis counter should fall back to the DB value.
    """
    url_a = URL(original_url="https://google.com", short_code="goog", click_count=0)
    url_b = URL(original_url="https://github.com", short_code="gh", click_count=3)

    repo = MagicMock(spec=URLRepository)
    repo.get_all = AsyncMock(return_value=[url_a, url_b])

    redis = AsyncMock()
    # url_a has 42 clicks in Redis; url_b has no Redis key (None) → should fall back to DB value 3
    redis.mget = AsyncMock(return_value=["42", None])

    service = make_service(repo=repo, redis=redis)
    result = await service.get_all_urls_with_live_counts()

    assert len(result) == 2
    assert result[0]["short_code"] == "goog"
    assert result[0]["click_count"] == 42     # from Redis
    assert result[1]["short_code"] == "gh"
    assert result[1]["click_count"] == 3      # fallback to DB value
    redis.mget.assert_called_once()           # single batch call, not N individual GETs
