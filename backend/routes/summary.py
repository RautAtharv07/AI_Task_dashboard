from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Session_local
from models import User
from ai_agents.summary_agent import fetch_tasks_for_summary, create_summary_prompt, call_llm

router = APIRouter()


def get_db():
    db = Session_local()
    try:
        yield db
    finally:
        db.close()

@router.get("/summary/{employee_id}")
def generate_employee_summary(employee_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == employee_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    task_data = fetch_tasks_for_summary(db, employee_id)
    prompt = create_summary_prompt(task_data, user.username)
    summary = call_llm(prompt)

    return summary
