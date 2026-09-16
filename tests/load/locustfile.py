import os

from locust import (
    HttpUser,
    between,
    task,
)


TASK_ID = os.getenv(
    "LOAD_TEST_TASK_ID"
)


class ContractAPIUser(HttpUser):
    """
    Basic API load test.

    These endpoints are intentionally lightweight.
    Heavy ML processing is tested separately so we
    do not accidentally flood Celery/Pinecone.
    """

    wait_time = between(
        0.5,
        2.0,
    )

    @task(5)
    def health_check(self):
        self.client.get(
            "/health",
            name="/health",
        )

    @task(3)
    def root_endpoint(self):
        self.client.get(
            "/",
            name="/",
        )

    @task(2)
    def task_status(self):
        if not TASK_ID:
            return

        self.client.get(
            f"/api/contracts/tasks/{TASK_ID}",
            name="/api/contracts/tasks/{task_id}",
        )