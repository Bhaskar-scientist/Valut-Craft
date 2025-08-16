import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import uuid

from app.main import app
from app.db.session import get_db
from app.models.base import Base
from app.core.config import settings

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://vaultcraft:vaultcraft123@localhost:5432/vaultcraft_test"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db_setup():
    """Setup test database tables"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(test_db_setup):
    """Create a fresh database session for each test"""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_organization():
    """Sample organization data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "name": "Test Organization",
        "created_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "password": "testpassword123",
        "org_id": str(uuid.uuid4())
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
        "status": "ACTIVE"
    }
