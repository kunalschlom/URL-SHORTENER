import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.url import URLService
from app.repositories.url import URLRepository
from app.models.url import URL

def test_validate_url_valid():
    service = URLService(repository=MagicMock())
    service.validate_url("https://example.com")
    service.validate_url("http://example.com/path?query=1")

def test_validate_url_invalid():
    service = URLService(repository=MagicMock())
    with pytest.raises(ValueError):
        service.validate_url("invalid-url")
    with pytest.raises(ValueError):
        service.validate_url("ftp://example.com")
    with pytest.raises(ValueError):
        service.validate_url("")

def test_generate_short_code_length():
    service = URLService(repository=MagicMock())
    code = service.generate_short_code()
    assert len(code) == 6
    assert all(c in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" for c in code)

@pytest.mark.asyncio
async def test_create_url_success():
    repo = MagicMock(spec=URLRepository)
    repo.get_by_short_code = AsyncMock(return_value=None)
    repo.create = AsyncMock(return_value=URL(original_url="https://google.com", short_code="abcde1"))
    service = URLService(repository=repo)
    url = await service.create_url("https://google.com")
  
    assert url is not None
    repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_create_url_collision_retry():
    repo = MagicMock(spec=URLRepository)
    repo.get_by_short_code = AsyncMock(side_effect=[URL(original_url="https://other.com", short_code="coll1"), None])
    repo.create = AsyncMock(return_value=URL(original_url="https://google.com", short_code="abcde2"))

    service = URLService(repository=repo)
    url = await service.create_url("https://google.com")
    
    assert url is not None
    assert repo.get_by_short_code.call_count == 2
    repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_create_url_max_collisions():
    repo = MagicMock(spec=URLRepository)
    repo.get_by_short_code = AsyncMock(return_value=URL(original_url="https://other.com", short_code="coll"))

    service = URLService(repository=repo)
    with pytest.raises(RuntimeError):
        await service.create_url("https://google.com")

@pytest.mark.asyncio
async def test_redirect_lookup():
    db_url = URL(original_url="https://google.com", short_code="google", click_count=0)
    repo = MagicMock(spec=URLRepository)
    repo.get_by_short_code = AsyncMock(return_value=db_url)
    repo.save = AsyncMock(return_value=db_url)

    service = URLService(repository=repo)
    url = await service.redirect_lookup("google")

    assert url is not None
    assert url.click_count == 1
    repo.save.assert_called_once_with(db_url)
