import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from api.dependencies.database import get_db
from mongomock_motor import AsyncMongoMockClient

# Create a mock MongoDB client for testing
@pytest_asyncio.fixture(scope="function")
async def test_db():
    mock_client = AsyncMongoMockClient()
    yield mock_client.get_database("testdb")

# Override the get_db dependency to use the mock client
@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear() 