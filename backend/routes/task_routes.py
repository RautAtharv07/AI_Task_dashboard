from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import Session_local
from models import Task, User,EmployeeProfile
from schemas import TaskCreate, TaskUpdate, TaskOut
from auth_utils import get_current_user
from dependencies.roles import require_admin, require_manager, require_employee
from ai_agents.assignment_agent import auto_assign_agent
from ai_agents.notification_agent import send_email


router = APIRouter(prefix="/tasks", tags=["Tasks"])

def get_db():
    db = Session_local()
    try:
        yield db
    finally:
        db.close()

# ✅ Create a new task with auto-assignment
@router.post("/auto-assign")
def create_and_assign_task(task: TaskCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    result = auto_assign_agent(db, task.required_skills)

    if not result['assigned_to']:
        raise HTTPException(status_code=404, detail="No suitable employee found")
    

    new_task = Task(
        title=task.title,
        description=task.description,
        status = task.status,
        required_skills=task.required_skills,
        assignee_id=result["assigned_to"]
    )
    assignee = db.query(User).filter(User.id == result["assigned_to"]).first()
    if assignee and assignee.email:
        send_email(
            recipient=assignee.email,
            subject=f"[New Task Assigned] {new_task.title}",
           message=f"Hello {assignee.username},\n\nYou have been assigned a new task:\n\nTitle: {new_task.title}\nDescription: {new_task.description}\n\nBest,\nTaskBot"
        )
        

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {
        "message": "Task created and assigned successfully",
        "task_id": new_task.id,
        "assigned_to": result['assigned_to'],
        "skills_extracted": task.required_skills
    }

# ✅ Get all tasks
@router.get("/", response_model=list[TaskOut])
def get_all_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    return db.query(Task).all()


# ✅ Get tasks assigned to the current user
@router.get("/my", response_model=list[TaskOut])
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee)
):
    return db.query(Task).filter(Task.assignee_id == current_user.id).all()

# ✅ Update a task by ID
@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, updated_task: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = updated_task.title
    task.description = updated_task.description
    db.commit()
    db.refresh(task)
    return task

# ✅ Delete a task
@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}

@router.put("/{task_id}/assign", response_model=TaskOut)
def assign_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_data.title:
        task.title = task_data.title
    if task_data.description:
        task.description = task_data.description
    if task_data.assignee_id:
        # Optional: Check if user exists
        user = db.query(User).filter(User.id == task_data.assignee_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Assignee not found")
        task.assignee_id = task_data.assignee_id

    db.commit()
    db.refresh(task)
    return task
