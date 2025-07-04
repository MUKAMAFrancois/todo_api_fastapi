# database dependency
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import Depends
from typing import Annotated, AsyncGenerator
from core.config import settings

# get_db
async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    Returns a MongoDB database session.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    try:
        yield client[settings.DATABASE_NAME]
    finally:
        client.close()