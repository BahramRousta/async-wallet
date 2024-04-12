import json

from locust import HttpUser, task, between


class HelloWorldUser(HttpUser):
    wait_time = between(1, 6)  # Time between consecutive tasks

    @task
    def deposit(self):
        for i in range(400_000, 600_000):
            data = {
                "wallet_id": "f0b70509-0d5d-4240-9466-4ed99106d513",
                "amount": i
                }

            response = self.client.post(f"/deposit/", json=data)
            if response.status_code != 201:
                print(f"Failed to create wallet: {response.text}")

