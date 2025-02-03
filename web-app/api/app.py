from fastapi import FastAPI
from enum import Enum
from api.models import (
    CoCAResponse,
    CoNAResponse,
    Composition,
    Cost,
    CoRDResponse,
    Product,
)
import requests
from api import init_db

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await init_db()


class Sex(Enum):
    MASCULINE = "0"
    FEMININE = "1"


Feminine_Demographics = [
    "1 a 3 años",
    "4 a 8 años",
    "9 a 13 años",
    "14 a 18 años",
    "19 a 30 años",
    "31 a 50 años",
    "51 a 70 años",
    "Más de 70 años",
]

Pregnant_Demographics = [
    "Gestantes menores de 18 años",
    "Gestantes de 19 a 30 años",
    "Gestantes de 31 a 50 años",
]

Lactating_Demographics = [
    "Lactantes menores de 18 años",
    "Lactantes de 19 a 30 años",
    "Lactantes de 31 a 50 años",
]

Masculine_Demographics = [
    "1 a 3 años",
    "4 a 8 años",
    "9 a 13 años",
    "14 a 18 años",
    "19 a 30 años",
    "31 a 50 años",
    "51 a 70 años",
    "Más de 70 años",
]

Demographics = (
    Feminine_Demographics
    + Pregnant_Demographics
    + Lactating_Demographics
    + Masculine_Demographics
)


async def filter_cost_and_composition(composition, cost_data):
    group_replacements = {
        "gestantes < 18 años": "Gestantes menores de 18 años",
        "gestantes 19 a 30 años": "Gestantes de 19 a 30 años",
        "gestantes 31 a 50 años": "Gestantes de 31 a 50 años",
        "lactantes < 18 años": "Lactantes menores de 18 años",
        "lactantes 19 a 30 años": "Lactantes de 19 a 30 años",
        "lactantes 31 a 50 años": "Lactantes de 31 a 50 años",
        ">70 años": "Más de 70 años",
    }

    def get_index(demo_group, sex):
        sex = int(sex)
        # Determine if pregnant or lactating from demo_group keywords
        dg_lower = demo_group.lower()
        pregnant = "gestantes" in dg_lower
        lactating = "lactantes" in dg_lower
        # Normalize numeric group
        if demo_group in group_replacements:
            demo_group = group_replacements[demo_group]

        age_map = {
            "1 a 3 años": 0,
            "4 a 8 años": 1,
            "9 a 13 años": 2,
            "14 a 18 años": 3,
            "19 a 30 años": 4,
            "31 a 50 años": 5,
            "51 a 70 años": 6,
            "Más de 70 años": 7,
            "Gestantes menores de 18 años": 8,
            "Gestantes de 19 a 30 años": 9,
            "Gestantes de 31 a 50 años": 10,
            "Lactantes menores de 18 años": 11,
            "Lactantes de 19 a 30 años": 12,
            "Lactantes de 31 a 50 años": 13,
        }
        idx = age_map.get(demo_group, 7)  # fallback
        # For masculine, offset by +14
        if sex == 0 and not pregnant and not lactating:
            offsets = {0: 14, 1: 15, 2: 16, 3: 17, 4: 18, 5: 19, 6: 20, 7: 21}
            idx = offsets.get(idx, 21)
        return idx

    comp = [[] for _ in range(22)]
    cost = [[] for _ in range(22)]
    for item in composition:
        i = get_index(item.get("Demo_Group", ""), item.get("Sex", 1))

        product = await Product.find_one({"name": item["Food"]})

        item = Composition(
            food=item["Food"],
            url=product.url,
            image=product.image,
            price=product.price,
            quantity=item.get("quantity", None),
            number_serving=item.get("Number_Serving", None),
            demo_group=item["Demo_Group"],
            sex=item["Sex"],
            group=item["Group"],
        ).model_dump(exclude_none=True)

        comp[i].append(item)
    for item in cost_data:
        i = get_index(item.get("Demo_Group", ""), item.get("Sex", 1))

        item = Cost(
            demo_group=item["Demo_Group"],
            sex=item["Sex"],
            cost_day=item["cost_day"],
            cost_1000kcal=item["Cost_1000kcal"],
        ).model_dump(exclude_none=True)

        cost[i].append(item)
    return {
        "comp": comp,
        "cost": cost,
    }


@app.get("/api/get_coca")
async def get_coca(
    age: int,
    sex: Sex,
    pregnant: bool = False,
    lactating: bool = False,
    exclude: str = None,
):
    if age < 1:
        return {"error": "Invalid age"}

    if sex == Sex.MASCULINE and (pregnant or lactating):
        return {"error": "Men cannot be pregnant or lactating."}

    if pregnant and lactating:
        return {
            "error": "Pregnant and lactating at the same time is not supported, please choose one."
        }

    coca = requests.get(
        f"http://localhost:4000/api/r/get_coca?exclude={exclude}"
    ).json()

    age_ranges = []
    if sex == Sex.FEMININE and not (pregnant or lactating):
        age_ranges = [
            (4, 0),
            (9, 1),
            (14, 2),
            (19, 3),
            (31, 4),
            (51, 5),
            (71, 6),
            (float("inf"), 7),
        ]
    elif sex == Sex.FEMININE and pregnant:
        age_ranges = [
            (18, 8),
            (31, 9),
            (float("inf"), 10),
        ]
    elif sex == Sex.FEMININE and lactating:
        age_ranges = [
            (18, 11),
            (31, 12),
            (float("inf"), 13),
        ]
    elif sex == Sex.MASCULINE:
        age_ranges = [
            (4, 14),
            (9, 15),
            (14, 16),
            (19, 17),
            (31, 18),
            (51, 19),
            (71, 20),
            (float("inf"), 21),
        ]

    for max_age, index in age_ranges:
        if age < max_age:
            product = await Product.find_one({"name": coca["cost"][index]["Food"]})

            return CoCAResponse(
                food=coca["cost"][index]["Food"],
                url=product.url,
                price=product.price,
                image=product.image,
                quantity=coca["cost"][index]["quantity"],
                demo_group=coca["cost"][index]["Demo_Group"],
                sex=coca["cost"][index]["Sex"],
                group=coca["cost"][index]["Group"],
                cost_day=coca["cost"][index]["cost_day"],
                cost_1000kcal=coca["cost"][index]["Cost_1000kcal"],
            ).model_dump(exclude_none=True)


@app.get("/api/get_cona")
async def get_cona(
    age: int,
    sex: Sex,
    pregnant: bool = False,
    lactating: bool = False,
    exclude: str = None,
):
    if age < 1:
        return {"error": "Invalid age"}

    if sex == Sex.MASCULINE and (pregnant or lactating):
        return {"error": "Men cannot be pregnant or lactating."}

    if pregnant and lactating:
        return {
            "error": "Pregnant and lactating at the same time is not supported, please choose one."
        }

    cona = requests.get(
        f"http://localhost:4000/api/r/get_cona?exclude={exclude}"
    ).json()

    filtered_cona = await filter_cost_and_composition(cona["comp"], cona["cost"])

    age_ranges = []
    if sex == Sex.FEMININE and not (pregnant or lactating):
        age_ranges = [
            (4, 0),
            (9, 1),
            (14, 2),
            (19, 3),
            (31, 4),
            (51, 5),
            (71, 6),
            (float("inf"), 7),
        ]
    elif sex == Sex.FEMININE and pregnant:
        age_ranges = [
            (18, 8),
            (31, 9),
            (float("inf"), 10),
        ]
    elif sex == Sex.FEMININE and lactating:
        age_ranges = [
            (18, 11),
            (31, 12),
            (float("inf"), 13),
        ]
    elif sex == Sex.MASCULINE:
        age_ranges = [
            (4, 14),
            (9, 15),
            (14, 16),
            (19, 17),
            (31, 18),
            (51, 19),
            (71, 20),
            (float("inf"), 21),
        ]

    for max_age, index in age_ranges:
        if age < max_age:
            return CoNAResponse(
                cost=filtered_cona["cost"][index],
                composition=filtered_cona["comp"][index],
            ).model_dump(exclude_none=True)


@app.get("/api/get_cord")
async def get_cord(
    age: int,
    sex: Sex,
    pregnant: bool = False,
    lactating: bool = False,
    exclude: str = None,
):
    if age < 1:
        return {"error": "Invalid age"}

    if sex == Sex.MASCULINE and (pregnant or lactating):
        return {"error": "Men cannot be pregnant or lactating."}

    if pregnant and lactating:
        return {
            "error": "Pregnant and lactating at the same time is not supported, please choose one."
        }

    cord = requests.get(
        f"http://localhost:4000/api/r/get_cord?exclude={exclude}"
    ).json()

    filtered_cord = await filter_cost_and_composition(cord["comp"], cord["cost"])

    age_ranges = []
    if sex == Sex.FEMININE and not (pregnant or lactating):
        age_ranges = [
            (4, 0),
            (9, 1),
            (14, 2),
            (19, 3),
            (31, 4),
            (51, 5),
            (71, 6),
            (float("inf"), 7),
        ]
    elif sex == Sex.FEMININE and pregnant:
        age_ranges = [
            (18, 8),
            (31, 9),
            (float("inf"), 10),
        ]
    elif sex == Sex.FEMININE and lactating:
        age_ranges = [
            (18, 11),
            (31, 12),
            (float("inf"), 13),
        ]
    elif sex == Sex.MASCULINE:
        age_ranges = [
            (4, 14),
            (9, 15),
            (14, 16),
            (19, 17),
            (31, 18),
            (51, 19),
            (71, 20),
            (float("inf"), 21),
        ]

    for max_age, index in age_ranges:
        if age < max_age:
            return CoRDResponse(
                cost=filtered_cord["cost"][index],
                composition=filtered_cord["comp"][index],
            ).model_dump(exclude_none=True)


@app.get("/api/get_products")
async def get_products():
    products = await Product.all().sort(+Product.name).to_list()
    return products
