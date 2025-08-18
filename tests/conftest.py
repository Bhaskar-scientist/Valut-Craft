import asyncio
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from app.core.config import settings
from app.db.session import get_db
from app.main import app
from app.models.base import Base

# Test database URL
TEST_DATABASE_URL = (
    "postgresql+asyncpg://vaultcraft:vaultcraft123@localhost:5432/vaultcraft"
)

# Lazy test database setup
_test_engine = None
_testing_session_local = None


def get_test_engine():
    """Get or create the test database engine lazily"""
    global _test_engine
    if _test_engine is None:
        _test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    return _test_engine


def get_testing_session_local():
    """Get or create the test session factory lazily"""
    global _testing_session_local
    if _testing_session_local is None:
        engine = get_test_engine()
        _testing_session_local = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
    return _testing_session_local


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_db_setup():
    """Setup test database tables"""
    engine = get_test_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(test_db_setup):
    """Create a fresh database session for each test"""
    TestingSessionLocal = get_testing_session_local()
    async with TestingSessionLocal() as session:
        yield session
        # Clean up any data created during the test
        await session.rollback()
        # Truncate tables to ensure clean state
        async with session.begin():
            await session.execute(text("TRUNCATE TABLE users, organizations CASCADE"))
            await session.commit()


@pytest_asyncio.fixture
async def client(db_session):
    """Create an async test client with database dependency override"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_organization():
    """Sample organization data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "name": "Test Organization",
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_user():
    """Sample organization data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "password": "testpassword123",
        "org_id": str(uuid.uuid4()),
    }


@pytest.fixture
def sample_wallet():
    """Sample wallet data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "balance": "1000.00",
        "currency": "INR",
        "type": "PRIMARY",
        "status": "ACTIVE",
    }
