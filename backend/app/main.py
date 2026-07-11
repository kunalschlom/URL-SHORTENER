from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.redis import connect_redis, disconnect_redis
from app.api.endpoints.url import router as url_router, api_router  # Fixed import (no 'backend.' prefix)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    # Open the Redis connection once when the app starts
    await connect_redis()
    yield
    # --- Shutdown ---
    # Close the Redis connection cleanly when the app stops
    await disconnect_redis()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A modern URL shortener backend service with click analytics.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(url_router)
