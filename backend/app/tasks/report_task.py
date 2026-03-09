from app.tasks.celery_app import celery_app
from app.services.report_service import generate_project_pdf
from app.services.storage_service import upload_pdf

@celery_app.task(name="app.tasks.report_task.generate_report")
def generate_report(project_data: dict, validations: list,
                    selected_layout: dict, layout_image_path: str | None = None):
    pdf_bytes = generate_project_pdf(project_data, validations,
                                      selected_layout, layout_image_path)
    filename  = f"report_{project_data['id']}.pdf"
    url       = upload_pdf(pdf_bytes, filename)
    return {"pdf_url": url, "project_id": project_data["id"]}
