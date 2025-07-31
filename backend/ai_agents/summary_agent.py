import os
import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Task  # ✅ your SQLAlchemy Task model
from openai import OpenAI


API_KEY = os.getenv("TOGETHER_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.together.xyz/v1",
)


def fetch_tasks_for_summary(db: Session, user_id: int):
    today = datetime.utcnow().date()
    now = datetime.utcnow()

    tasks = db.query(Task).filter(
        Task.assignee_id == user_id,
        or_(
            Task.created_at >= today,
            Task.status_updated_at >= today
        )
    ).all()

    all_tasks_data = []
    overdue = []
    upcoming = []
    stagnant = []

    for task in tasks:
        task_info = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "deadline": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat(),
            "status_updated_at": task.status_updated_at.isoformat(),
        }
        all_tasks_data.append(task_info)

        if task.due_date:
            if task.due_date < now:
                overdue.append(task_info)
            elif task.due_date <= now + timedelta(days=2):
                upcoming.append(task_info)

        if task.status == "pending" and task.status_updated_at.date() < today:
            stagnant.append(task_info)

    return {
        "all_tasks": all_tasks_data,
        "overdue": overdue,
        "upcoming": upcoming,
        "stagnant": stagnant
    }


def create_summary_prompt(data: dict, employee_name: str):
    prompt = f"""
You are a smart assistant helping managers with daily task summaries for their employees.

Employee: {employee_name}

Summary Data:
- Total Tasks: {len(data['all_tasks'])}
- Overdue Tasks: {len(data['overdue'])}
- Upcoming Deadlines (next 2 days): {len(data['upcoming'])}
- Pending Tasks not updated today: {len(data['stagnant'])}

Now generate a helpful daily summary in JSON with the following structure:
{{
  "employee": "{employee_name}",
  "total_tasks": <int>,
  "overdue": [{{"id": ..., "title": ..., "deadline": ..., "description": ...}}],
  "upcoming": [{{...}}],
  "stagnant": [{{...}}],
  "suggested_actions": "..."
}}

Be concise but informative. Mention urgent tasks and suggest follow-up actions.
"""
    return prompt


def call_llm(prompt: str) -> dict:
    headers = {
        "Authorization": f"Bearer {os.getenv('ALLTOGETHER_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.2",
                messages=[
                    {"role": "system", "content": "You are a smart assistant helping managers with daily task summaries for their employees."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=512,
                temperature=0.7
            )

    message = response.choices[0].message.content
    
    try:
        return eval(message) if message.strip().startswith("{") else {"raw": message}
    except Exception:
        return {"raw": message}
