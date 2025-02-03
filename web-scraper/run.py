from web_scraper import get_product, initialize_webdriver
from multiprocessing import Pool
import json
import os

products = [
    "Brócoli",
    "Cebolla cabezona blanca bogotana",
    "Cebolla junca Aquitania",
    "Cebolla junca Tenerife",
    "Chócolo mazorca",
    "Cilantro",
    "Coliflor",
    "Fríjol verde cargamanto",
    "Habichuela",
    "Lechuga Batavia",
    "Lechuga crespa verde",
    "Pepino cohombro",
    "Pimentón",
    "Remolacha bogotana",
    "Repollo blanco",
    "Tomate chonto",
    "Tomate larga vida",
    "Zanahoria",
    "Zanahoria bogotana",
    "Aguacate papelillo",
    "Banano criollo",
    "Coco",
    "Curuba",
    "Fresa",
    "Granadilla",
    "Guanábana",
    "Guayaba pera",
    "Kiwi",
    "Limón común",
    "Limón Tahití",
    "Lulo",
    "Mandarina Arrayana",
    "Mandarina Oneco",
    "Mango común",
    "Mango Tommy",
    "Manzana roja importada",
    "Manzana royal gala importada",
    "Manzana verde importada",
    "Maracuyá",
    "Melón Cantalup",
    "Mora de Castilla",
    "Naranja Sweet",
    "Papaya Maradol",
    "Patilla",
    "Patilla baby",
    "Pera importada",
    "Piña gold",
    "Piña manzana",
    "Tomate de árbol",
    "Uva importada",
    "Uva Isabela",
    "Uva red globe nacional",
    "Arracacha amarilla",
    "Papa capira",
    "Papa criolla limpia",
    "Papa criolla sucia",
    "Papa parda pastusa",
    "Papa suprema",
    "Papa única",
    "Plátano hartón verde",
    "Yuca ICA",
    "Arroz de primera",
    "Cuchuco de maíz",
    "Fríjol calima",
    "Lenteja importada",
    "Maíz amarillo trillado",
    "Maíz blanco trillado",
    "Huevo rojo A",
    "Huevo rojo AA",
    "Huevo rojo extra",
    "Leche en polvo",
    "Queso campesino",
    "Queso Caquetá",
    "Queso costeño",
    "Queso cuajada",
    "Queso doble crema",
    "cerdo brazo",  # "Carne de cerdo, brazo sin hueso",
    "cerdo costilla",  # "Carne de cerdo, costilla",
    "cerdo espinazo",  # "Carne de cerdo, espinazo",
    "cerdo lomo",  # "Carne de cerdo, lomo sin hueso",
    "cerdo pernil sin hueso",  # Carne de cerdo, pernil sin hueso
    "cerdo papada",  # "Carne de cerdo, tocino papada",
    "res bola brazo",  # "Carne de res, bola de brazo",
    "res bola pierna",  # "Carne de res, bola de pierna",
    "res cadera",  # "Carne de res, cadera",
    "res chatas",  # "Carne de res, chatas",
    "res costilla",  # "Carne de res, costilla",
    "res falda",  # "Carne de res, falda",
    "res morrillo",  # "Carne de res, morrillo",
    "res muchacho",  # "Carne de res, muchacho",
    "res pecho",  # "Carne de res, pecho",
    # "Carne de res, punta de anca",  # No disponible
    "res, sobrebarriga",
    "pollo pechuga",
    "Pierna pernil con rabadilla",
    "pollo pierna",
    "Pollo entero congelado sin vísceras",
    "Almejas con concha",
    "Basa, entero congelado importado",
    "Basa, filete congelado importado",
    "Bocachico importado congelado",
    "Trucha en corte mariposa",
    "Aceite vegetal mezcla",
    "Chocolate amargo",
    "Galletas saladas",
    "Gelatina",
    "Harina de trigo",
    "Harina precocida de maíz",
    "Jugo instantáneo (sobre)",
    "Lomitos de atún en lata",
    "Margarina",
    "Mayonesa doy pack",
    "Panela redonda morena",
    "Pastas alimenticias",
    "Sal yodada",
    "Salsa de tomate doy pack",
    "Sardinas en lata",
]


def clean_results_folder():
    results_folder = "results"
    if not os.path.exists(results_folder):
        return

    for filename in os.listdir(results_folder):
        if filename.endswith(".json"):
            product_name = filename[:-5]  # Remove the .json extension
            if product_name not in products:
                file_path = os.path.join(results_folder, filename)
                os.remove(file_path)
                print(f"Deleted {file_path}")


def scrape_product(product):
    print(f"Getting {product}...")

    json_file_path = os.path.join("results", f"{product}.json")
    if os.path.exists(json_file_path):
        print(f"JSON file for {product} already exists. Skipping scraping.")
        with open(json_file_path, "r", encoding="utf-8") as f:
            products = json.load(f)
        return products

    get_product(
        city={"city_name": "Cali", "city_id": "react-select-2-option-6"},
        store={
            "store_name": "Exito Wow Valle del Lili",
            "store_id": "react-select-3-option-7",
        },
        product_name=product,
    )


if __name__ == "__main__":
    clean_results_folder()
    with Pool(3) as p:
        p.map(scrape_product, products)
