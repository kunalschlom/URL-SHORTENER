from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.core.database import get_async_db
from app.core.redis import get_redis
from app.repositories import URLRepository
from app.services import URLService
from app.schemas import URLCreate, URLResponse

router = APIRouter()
api_router = APIRouter()


async def get_url_service(
    db: AsyncSession = Depends(get_async_db),
    redis: aioredis.Redis = Depends(get_redis),
) -> URLService:
    repository = URLRepository(db)
    return URLService(repository, redis)  # Pass redis into the service


@api_router.post("/shorten", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(payload: URLCreate, service: URLService = Depends(get_url_service)):
    return await service.create_url(original_url=payload.original_url)


@api_router.get("/urls", response_model=list[URLResponse])
async def get_urls(
    skip: int = 0,
    limit: int = 100,
    service: URLService = Depends(get_url_service),
):
    return await service.get_all_urls_with_live_counts(skip=skip, limit=limit)


@api_router.delete("/urls/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_url(id: UUID, service: URLService = Depends(get_url_service)):
    deleted = await service.delete_url_by_id(id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok"}


@router.get("/{short_code}")
async def redirect_to_url(short_code: str, service: URLService = Depends(get_url_service)):
    original_url = await service.redirect_lookup(short_code)
    if not original_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")
    return RedirectResponse(url=original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
