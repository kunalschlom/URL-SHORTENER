import pytest
from typing import AsyncGenerator
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from app.core.database import Base, get_async_db
from app.core.redis import get_redis
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        class_=AsyncSession
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def mock_redis():
    """
    A lightweight fake Redis client for unit/API tests.
    Uses an in-memory dict to simulate get/set/delete/incr so tests
    don't need a real Redis server running.
    """
    store: dict = {}

    redis = AsyncMock()

    async def _get(key):
        return store.get(key)

    async def _set(key, value, ex=None):
        store[key] = value

    async def _delete(*keys):
        for k in keys:
            store.pop(k, None)

    async def _incr(key):
        store[key] = store.get(key, 0) + 1
        return store[key]

    async def _mget(*keys):
        return [store.get(k) for k in keys]

    redis.get = AsyncMock(side_effect=_get)
    redis.set = AsyncMock(side_effect=_set)
    redis.delete = AsyncMock(side_effect=_delete)
    redis.incr = AsyncMock(side_effect=_incr)
    redis.mget = AsyncMock(side_effect=_mget)

    return redis


@pytest.fixture
async def client(db_session: AsyncSession, mock_redis) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_async_db():
        yield db_session

    def override_get_redis():
        return mock_redis

    app.dependency_overrides[get_async_db] = override_get_async_db
    app.dependency_overrides[get_redis] = override_get_redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
