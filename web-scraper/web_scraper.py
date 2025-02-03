from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timezone
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import ua_generator
import urllib
import typer
import json
import time
import csv
import os


def generate_random_user_agent():
    device = "desktop"
    platform = ("windows", "macos")
    browser = ("chrome", "edge")

    user_agent = ua_generator.generate(
        device=device, browser=browser, platform=platform
    ).text

    return user_agent


def initialize_webdriver(headless=True):
    user_agent = generate_random_user_agent()

    options = Options()
    options.add_argument(f'user-agent="{user_agent}"')
    if headless:
        options.add_argument("--headless=new")

    chromedriver_install = ChromeDriverManager().install()
    webdriver_folder = os.path.dirname(chromedriver_install)
    chromedriver_path = os.path.join(webdriver_folder, "chromedriver")
    webdriver_service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=webdriver_service, options=options)

    return driver


def click_select_city_button(driver):
    select_city_and_store_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/div/header/section/div/div[1]/div[3]/button")
        )
    )

    select_city_and_store_button.click()

    select_city_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="react-select-2-input"]'))
    )

    select_city_button.click()


def get_city_list(driver):
    city_list = []

    driver.get("https://www.exito.com/s")

    click_select_city_button(driver=driver)

    city_listbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="react-select-2-listbox"]'))
    )

    city_options = city_listbox.find_elements(By.XPATH, './/div[@role="option"]')

    for city_option in city_options:
        city_option_name = city_option.text
        city_option_id = city_option.get_attribute("id")
        city_list.append({"city_name": city_option_name, "city_id": city_option_id})

    return city_list


def click_selected_city_button(driver, city_id, path="https://www.exito.com/s"):
    driver.get(path)

    click_select_city_button(driver=driver)

    city_listbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="react-select-2-listbox"]'))
    )

    city_options = city_listbox.find_elements(By.XPATH, './/div[@role="option"]')

    for city_option in city_options:
        if city_option.get_attribute("id") == city_id:
            city_option.click()
            return True

    return False


def click_select_store_button(driver):
    select_store_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="react-select-3-input"]'))
    )

    select_store_button.click()


def get_store_list(driver, city_id):
    store_list = []

    click_selected_city_button(driver=driver, city_id=city_id)

    click_select_store_button(driver=driver)

    store_listbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="react-select-3-listbox"]'))
    )

    store_options = store_listbox.find_elements(By.XPATH, './/div[@role="option"]')

    for store_option in store_options:
        store_option_name = store_option.text
        store_option_id = store_option.get_attribute("id")
        store_list.append(
            {"store_name": store_option_name, "store_id": store_option_id}
        )

    return store_list


def click_selected_store_button(driver, store_id):
    click_select_store_button(driver=driver)

    store_listbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="react-select-3-listbox"]'))
    )

    store_options = store_listbox.find_elements(By.XPATH, './/div[@role="option"]')

    for store_option in store_options:
        if store_option.get_attribute("id") == store_id:
            store_option.click()
            return True

    return False


def click_submit_button(driver):
    # It'd be better to use a more general selector for the submit button in case the class name changes in the future.
    submit_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "PickupPoint_primaryButtonEnable__vh9yw")
        )
    )

    submit_button.click()


def get_product(city, store, product_name):
    if not os.path.exists("results"):
        os.makedirs("results")

    json_file_path = os.path.join("results", f"{product_name}.json")
    if os.path.exists(json_file_path):
        print(f"JSON file for {product_name} already exists. Skipping scraping.")
        with open(json_file_path, "r", encoding="utf-8") as f:
            products = json.load(f)
        return products

    driver = initialize_webdriver(headless=False)

    click_selected_city_button(
        path=f"https://www.exito.com/s?q={product_name}&sort=score_desc&page=0",
        driver=driver,
        city_id=city["city_id"],
    )
    click_selected_store_button(driver=driver, store_id=store["store_id"])
    click_submit_button(driver=driver)

    time.sleep(5)

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "div[data-fs-product-card-image='true']")
        )
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")
    ul_content = soup.find(
        "ul", {"data-fs-product-grid": "true", "data-fs-product-grid-list": "true"}
    )
    article_elements = ul_content.find_all("li")

    products = []
    for article in article_elements:
        url = article.find("a", {"data-testid": "product-link"})["href"]
        # It'd be better to use a more general selector for the product name in case the class name changes in the future.
        name = (
            article.find("div", {"class": "productCard_productInfo__yn2lK"})
            .find("p")
            .text.strip()
        )
        image = (
            article.find("div", {"data-fs-product-card-image": "true"})
            .find("a", {"data-testid": "product-link"})
            .find("img")["src"]
        )
        price = (
            article.find("div", {"data-fs-container-price-otros-geral": "true"})
            .find("p")
            .text.strip()
        )
        unit_price = (
            article.find_all("a", {"data-testid": "product-link"})[1]
            .find("span")
            .text.strip()
            .replace("(", "")
            .replace(")", "")
        )

        try:
            discount = (
                article.find("div", {"data-fs-product-card-prices": "true"})
                .find("span", {"data-percentage": "true"})
                .text.strip()
            )
        except AttributeError:
            discount = 0

        products.append(
            {
                "city": city["city_name"],
                "store": store["store_name"],
                "url": "https://www.exito.com" + url,
                "name": name,
                "price": price,
                "unit_price": unit_price,
                "discount": float(discount),
                "image": image,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

    with open(
        os.path.join("results", "products.csv"), "a", newline="", encoding="utf-8"
    ) as csvfile:
        fieldnames = [
            "city",
            "store",
            "url",
            "name",
            "price",
            "unit_price",
            "discount",
            "image",
            "timestamp",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for product in products:
            writer.writerow(
                {
                    "city": product["city"],
                    "store": product["store"],
                    "url": product["url"],
                    "name": product["name"],
                    "price": product["price"],
                    "unit_price": product["unit_price"],
                    "discount": product["discount"],
                    "image": product["image"],
                    "timestamp": product["timestamp"],
                }
            )

    return products


def main(name: str):
    print(f"Hello {name}")


if __name__ == "__main__":
    typer.run(main)
