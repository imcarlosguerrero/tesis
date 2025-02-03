import os
import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, Document
from typing import Literal
from pymongo import IndexModel
import pymongo


class Product(Document):
    city: Literal["Cali"]
    store: Literal["Exito Wow Valle del Lili"]
    name: str
    url: str
    price: str
    unit_price: str
    discount: float
    image: str
    timestamp: str
    TCAC: str
    subgroup: str

    class Settings:
        name = "products"

        indexes = [
            IndexModel(
                [
                    ("name", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]


async def init_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(database=client["test"], document_models=[Product])


async def load_products():
    folder_path = "results"
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                data["name"] = data["name"][0].upper() + data["name"][1:].lower()
                product = Product(**data)
                await product.insert()


async def main():
    await init_db()
    await load_products()


if __name__ == "__main__":
    asyncio.run(main())
