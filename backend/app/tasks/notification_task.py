from app.tasks.celery_app import celery_app
from app.services.notification_service import (
    notify_validator_new_project, notify_user_validation_result
)

@celery_app.task(name="app.tasks.notification_task.send_validator_notification")
def send_validator_notification(validator_email: str, project_name: str, stage: int):
    notify_validator_new_project(validator_email, project_name, stage)

@celery_app.task(name="app.tasks.notification_task.send_user_notification")
def send_user_notification(user_email: str, project_name: str,
                            decision: str, feedback: str, stage: int):
    notify_user_validation_result(user_email, project_name, decision, feedback, stage)
