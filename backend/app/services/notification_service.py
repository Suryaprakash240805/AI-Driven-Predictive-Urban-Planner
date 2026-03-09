import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

def send_email(to: str, subject: str, body_html: str):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = settings.SMTP_USER
        msg["To"]      = to
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to, msg.as_string())
    except Exception as e:
        print(f"[EMAIL] Failed to send to {to}: {e}")

def notify_validator_new_project(validator_email: str, project_name: str, stage: int):
    send_email(
        to=validator_email,
        subject=f"[Urban Planner] New project pending – Stage {stage} review",
        body_html=f"""
        <div style="font-family:Inter,sans-serif;background:#0A0A1E;color:#E8E8F0;padding:32px;">
          <h2 style="color:#D4AF37;">New Project Awaiting Your Review</h2>
          <p>A new project <strong>{project_name}</strong> requires your Stage {stage} validation.</p>
          <a href="http://localhost:3000/validator"
             style="background:#D4AF37;color:#0A0A1E;padding:12px 24px;border-radius:8px;
                    font-weight:700;text-decoration:none;display:inline-block;margin-top:16px;">
            Open Validator Dashboard
          </a>
          <p style="color:#7A7A9A;font-size:12px;margin-top:24px;">
            Urban Planner · SDG 11 – Sustainable Cities
          </p>
        </div>"""
    )

def notify_user_validation_result(user_email: str, project_name: str,
                                   decision: str, feedback: str, stage: int):
    color   = "#5DBB63" if decision == "approved" else "#E05C5C"
    action  = "approved" if decision == "approved" else "rejected"
    send_email(
        to=user_email,
        subject=f"[Urban Planner] Your project was {action} at Stage {stage}",
        body_html=f"""
        <div style="font-family:Inter,sans-serif;background:#0A0A1E;color:#E8E8F0;padding:32px;">
          <h2 style="color:{color};">Project {action.title()} – Stage {stage}</h2>
          <p>Your project <strong>{project_name}</strong> was <strong>{action}</strong>.</p>
          {"<p>Feedback: " + feedback + "</p>" if feedback else ""}
          <a href="http://localhost:3000/dashboard"
             style="background:#D4AF37;color:#0A0A1E;padding:12px 24px;border-radius:8px;
                    font-weight:700;text-decoration:none;display:inline-block;margin-top:16px;">
            View Dashboard
          </a>
        </div>"""
    )
