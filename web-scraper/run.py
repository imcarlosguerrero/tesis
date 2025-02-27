from web_scraper import get_product, initialize_webdriver
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED, TimeoutError
import concurrent.futures
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
    max_retries = 3  # maximum number of attempts per product
    task_timeout = 120  # seconds before a task is considered timed out

    with ProcessPoolExecutor(max_workers=6) as executor:
        # Dictionary to hold futures keyed by product
        futures = {product: executor.submit(scrape_product, product) for product in products}
        # Tracker for available retries per product
        retries = {product: 0 for product in products}

        while futures:
            # Wait up to task_timeout seconds for any future to complete
            done, _ = wait(futures.values(), timeout=task_timeout, return_when=FIRST_COMPLETED)
            
            # If no task finished in the timeout period, handle timeouts
            if not done:
                # All running tasks have timed out. Cancel and retry.
                for product, future in list(futures.items()):
                    if not future.done():
                        future.cancel()
                        retries[product] += 1
                        if retries[product] < max_retries:
                            print(f"Timeout for {product}. Retrying (attempt {retries[product]+1}/{max_retries})...")
                            futures[product] = executor.submit(scrape_product, product)
                        else:
                            print(f"Failed retrieving {product} after {max_retries} retries.")
                            del futures[product]
                continue

            # Process tasks that completed within the timeout
            for product, future in list(futures.items()):
                if future.done():
                    try:
                        future.result()
                    except Exception as e:
                        retries[product] += 1
                        if retries[product] < max_retries:
                            print(f"Exception for {product}: {e}. Retrying (attempt {retries[product]+1}/{max_retries})...")
                            futures[product] = executor.submit(scrape_product, product)
                        else:
                            print(f"Failed retrieving {product} after {max_retries} retries.")
                    # Remove product if successfully processed or max retries exhausted
                    if product in futures and future.done() and retries[product] >= max_retries:
                        del futures[product]
                    elif product in futures and future.done() and retries[product] < max_retries:
                        # Check if the last submission succeeded by next loop iteration
                        del futures[product]
