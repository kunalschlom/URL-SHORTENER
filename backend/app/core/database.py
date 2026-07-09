from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import settings

# Common base class for SQLAlchemy models (SQLAlchemy 2.0 style)
class Base(DeclarativeBase):
    pass

# Synchronous Engine and Session Configuration
engine = create_engine(
    settings.sync_database_url,
    pool_pre_ping=True,
    echo=False,  # Set to True for debugging SQL queries
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Asynchronous Engine and Session Configuration
async_engine = create_async_engine(
    settings.async_database_url,
    pool_pre_ping=True,
    echo=False,  # Set to True for debugging SQL queries
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    expire_on_commit=False,
)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for obtaining a synchronous database session.
    Yields a Session and automatically closes it when finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for obtaining an asynchronous database session.
    Yields an AsyncSession and automatically closes/commits/rolls back when finished.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
