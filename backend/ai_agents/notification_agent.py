import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import Session_local
from models import Task, User

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))


def send_email(recipient: str, subject: str, message: str):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Email failed: {e}")

# ----- Notification Logic -----


def notify_due_soon(db: Session):
    soon = datetime.utcnow() + timedelta(hours=2)
    tasks = db.query(Task).filter(Task.due_date <= soon, Task.status != "Completed").all()
    for task in tasks:
        if task.assignee and task.assignee.email:
            send_email(
                recipient=task.assignee.email,
                subject=f"[Upcoming Task Due] {task.title}",
                message=f"Reminder: Your task '{task.title}' is due by {task.due_date.strftime('%Y-%m-%d %H:%M')}."
            )

def notify_overdue(db: Session):
    now = datetime.utcnow()
    tasks = db.query(Task).filter(Task.due_date < now, Task.status != "Completed").all()
    for task in tasks:
        if task.assignee and task.assignee.email:
            send_email(
                recipient=task.assignee.email,
                subject=f"[Overdue Task] {task.title}",
                message=f"The task '{task.title}' is overdue. Please take necessary action."
            )

# ----- Run All Notifications -----
def run_notifications():
    db = Session_local()
    try:
        notify_due_soon(db)
        notify_overdue(db)
    finally:
        db.close()
