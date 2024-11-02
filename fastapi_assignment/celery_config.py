from celery import Celery
from fastapi_assignment import config

# Initialize Celery
celery = Celery(
    "app",
    broker=config.REDIS_URL,
    backend=config.MONGO_URL,  # MongoDB as result backend
)
print(celery.conf.broker_url)

# Configure Celery with JSON serialization and UTC timezone
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_backend="mongodb",
    mongodb_backend_settings={
        "database": config.DB_NAME,
        "taskmeta_collection": config.CELERY_RESULT_COLLECTION,
    },
    imports=("fastapi_assignment.tasks",),
)
