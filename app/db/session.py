import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lazy database engine creation
_engine = None
_async_session = None


def get_engine():
    """Get or create the database engine lazily"""
    global _engine
    if _engine is None:
        # Ensure we're using asyncpg by explicitly specifying the driver
        database_url = settings.DATABASE_URL
        if not database_url.startswith("postgresql+asyncpg://"):
            # Force asyncpg if not already specified
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        
        _engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            future=True,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        logger.info("Database engine created successfully")
    return _engine


def get_async_session():
    """Get or create the async session factory lazily"""
    global _async_session
    if _async_session is None:
        engine = get_engine()
        _async_session = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        logger.info("Async session factory created successfully")
    return _async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async_session = get_async_session()
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    from app.models.base import Base
    
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


async def close_db():
    """Close database connections"""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        logger.info("Database connections closed")
