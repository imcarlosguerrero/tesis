from beanie import Document
from pydantic import BaseModel
from typing import Literal, List, Optional
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


class CoCAResponse(BaseModel):
    food: str
    url: str
    image: str
    price: str
    quantity: float
    demo_group: str
    sex: int
    group: str
    cost_day: float
    cost_1000kcal: float


class Cost(BaseModel):
    demo_group: str
    sex: int
    cost_day: float
    cost_1000kcal: float


class Composition(BaseModel):
    food: str
    url: str
    image: str
    price: str
    quantity: Optional[float] = None
    number_serving: Optional[float] = None
    demo_group: str
    sex: int
    group: str


class CoNAResponse(BaseModel):
    cost: List[Cost]
    composition: List[Composition]


class CoRDResponse(BaseModel):
    cost: List[Cost]
    composition: List[Composition]
