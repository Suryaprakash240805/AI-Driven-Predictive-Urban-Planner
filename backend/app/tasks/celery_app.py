from celery import Celery
from app.config import settings

celery_app = Celery(
    "urban_planner",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.layout_task", "app.tasks.report_task",
             "app.tasks.notification_task"],
)
celery_app.conf.update(
    task_serializer="json", result_serializer="json",
    accept_content=["json"], timezone="Asia/Kolkata",
    task_track_started=True,
    task_routes={
        "app.tasks.layout_task.*":       {"queue": "ml"},
        "app.tasks.report_task.*":       {"queue": "reports"},
        "app.tasks.notification_task.*": {"queue": "notifications"},
    }
)
