import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.url import URLRepository
from app.models.url import URL

@pytest.mark.asyncio
async def test_create_and_get_url(db_session: AsyncSession):
    repo = URLRepository(db_session)
    url = await repo.create(original_url="https://google.com", short_code="google")
    
    assert url.id is not None
    assert url.original_url == "https://google.com"
    assert url.short_code == "google"
    assert url.click_count == 0

    fetched = await repo.get_by_short_code("google")
    assert fetched is not None
    assert fetched.id == url.id

@pytest.mark.asyncio
async def test_get_all_urls(db_session: AsyncSession):
    repo = URLRepository(db_session)
    await repo.create(original_url="https://google.com", short_code="google")
    await repo.create(original_url="https://github.com", short_code="github")

    urls = await repo.get_all()
    assert len(urls) >= 2

@pytest.mark.asyncio
async def test_delete_by_id(db_session: AsyncSession):
    repo = URLRepository(db_session)
    url = await repo.create(original_url="https://google.com", short_code="google")
    
    deleted = await repo.delete_by_id(url.id)
    assert deleted is True

    fetched = await repo.get_by_short_code("google")
    assert fetched is None

@pytest.mark.asyncio
async def test_delete_by_non_existent_id(db_session: AsyncSession):
    import uuid
    repo = URLRepository(db_session)
    deleted = await repo.delete_by_id(uuid.uuid4())
    assert deleted is False

@pytest.mark.asyncio
async def test_save_url(db_session: AsyncSession):
    repo = URLRepository(db_session)
    url = await repo.create(original_url="https://google.com", short_code="google")
    url.click_count = 5
    await repo.save(url)

    fetched = await repo.get_by_short_code("google")
    assert fetched is not None
    assert fetched.click_count == 5
