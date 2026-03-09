import asyncio
from app.tasks.celery_app import celery_app
from app.services.ml_service import request_layout_generation

@celery_app.task(name="app.tasks.layout_task.trigger_layout_generation",
                 bind=True, max_retries=3, default_retry_delay=30)
def trigger_layout_generation(self, project_id: str, land_polygon: dict,
                               land_info: dict, use_type: str):
    """
    Async Celery task: calls the ML microservice to generate layouts
    and pushes the result back via WebSocket notification.
    """
    try:
        result = asyncio.get_event_loop().run_until_complete(
            request_layout_generation(project_id, land_polygon, land_info, use_type)
        )
        return result
    except Exception as exc:
        raise self.retry(exc=exc)
