from locust import HttpUser, task, between
import random

ages = [0, 1, 3, 5, 6, 12, 17, 54, 32, 43, 50]


class AppUser(HttpUser):
    wait_time = between(2, 5)

    @task
    def index(self):
        self.client.get("api/get_products")

    @task
    def test_coca(self):
        age = random.choice(ages)
        self.client.get(f"api/get_coca?age={age}&sex=0")
