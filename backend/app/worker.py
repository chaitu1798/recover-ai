from celery import Celery
from app.config import settings

celery = Celery(
    "recoverai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery.task(name="health_check_task")
def health_check_task():
    return "ok"
