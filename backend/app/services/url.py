import secrets
from typing import Sequence
from urllib.parse import urlparse
from uuid import UUID

from app.models.url import URL
from app.repositories.url import URLRepository

BASE62_CHARACTERS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

class URLService:
    def __init__(self, repository: URLRepository):
        self.repository = repository

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

    async def redirect_lookup(self, short_code: str) -> URL | None:
        url = await self.repository.get_by_short_code(short_code)
        if url:
            url.click_count += 1
            await self.repository.save(url)
        return url

    async def get_all_urls(self, skip: int = 0, limit: int = 100) -> Sequence[URL]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def delete_url(self, short_code: str) -> bool:
        return await self.repository.delete(short_code)

    async def delete_url_by_id(self, id: UUID) -> bool:
        return await self.repository.delete_by_id(id)
