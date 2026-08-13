from celery import Celery
from config import settings

celery_app = Celery(
    "agri_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
)

@celery_app.task(name="generate_batch_advisory")
def generate_batch_advisory(farm_ids: list):
    return {"status": "queued", "farm_count": len(farm_ids)}
