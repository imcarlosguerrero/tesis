from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from api.models import Product


async def init_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(database=client["test"], document_models=[Product])
