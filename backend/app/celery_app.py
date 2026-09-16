import os

from celery import Celery
from dotenv import load_dotenv

from backend.app.utils.logging_config import (
    setup_logging,
)


load_dotenv()

setup_logging()


CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL",
    "redis://localhost:6379/0",
)

CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND",
    "redis://localhost:6379/1",
)


celery_app = Celery(
    "contract_intelligence",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "backend.app.tasks.contract_tasks",
    ],
)


celery_app.conf.update(
    task_track_started=True,

    result_expires=3600,

    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    timezone="Asia/Kolkata",
    enable_utc=True,

    # Keep our JSON logging configuration.
    worker_hijack_root_logger=False,
)