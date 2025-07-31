from fastapi import Depends, HTTPException, status
from models import User
from auth_utils import get_current_user


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def require_manager(current_user: User = Depends(get_current_user)):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Manager access required")
    return current_user

def require_employee(current_user: User = Depends(get_current_user)):
    if current_user.role != "employee":
        raise HTTPException(status_code=403, detail="Employee access required")
    return current_user
