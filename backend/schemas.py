from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# User Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole
    skills: Optional[List[str]] = None

    @validator('skills')
    def validate_skills(cls, v):
        if v is not None:
            # Remove empty strings and duplicates
            skills = [skill.strip() for skill in v if skill.strip()]
            return list(set(skills)) if skills else None
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    skills: Optional[List[str]] = None

    @validator('skills')
    def validate_skills(cls, v):
        if v is not None:
            skills = [skill.strip() for skill in v if skill.strip()]
            return list(set(skills)) if skills else None
        return v


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    skills: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        from_attributes = True  # Updated for Pydantic v2 (was orm_mode = True)


class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    role: str
    skills: Optional[List[str]] = None

    class Config:
        from_attributes = True


# Task Schemas
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    assignee_id: Optional[int] = None
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    required_skills: Optional[List[str]] = None

    @validator('required_skills')
    def validate_required_skills(cls, v):
        if v is not None:
            skills = [skill.strip() for skill in v if skill.strip()]
            return list(set(skills)) if skills else None
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    assignee_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    required_skills: Optional[List[str]] = None

    @validator('required_skills')
    def validate_required_skills(cls, v):
        if v is not None:
            skills = [skill.strip() for skill in v if skill.strip()]
            return list(set(skills)) if skills else None
        return v


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    assignee: Optional[UserProfile] = None  # Nested user info
    status: str = "pending"
    priority: str = "medium"
    required_skills: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    due_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskSummary(BaseModel):
    id: int
    title: str
    status: str
    priority: str
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# Assignment Related Schemas
class TaskAssignment(BaseModel):
    task_id: int
    assignee_id: int
    reason: Optional[str] = None


class AutoAssignRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


class AutoAssignResponse(BaseModel):
    message: str
    task_id: int
    assigned_to: int
    assignee_username: str
    skills_extracted: List[str]
    match_score: float


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    email: Optional[str] = None


# Response Schemas
class SuccessResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    detail: str
    success: bool = False


# Dashboard/Statistics Schemas
class TaskStats(BaseModel):
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    cancelled_tasks: int


class UserStats(BaseModel):
    total_users: int
    active_users: int
    admins: int
    managers: int
    employees: int


class DashboardStats(BaseModel):
    task_stats: TaskStats
    user_stats: UserStats
    recent_tasks: List[TaskSummary]


# Employee Profile Schemas (if you have a separate employee profile model)
class EmployeeProfileCreate(BaseModel):
    user_id: int
    department: Optional[str] = None
    position: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    availability: bool = True


class EmployeeProfileUpdate(BaseModel):
    department: Optional[str] = None
    position: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    availability: Optional[bool] = None


class EmployeeProfileOut(BaseModel):
    id: int
    user_id: int
    user: Optional[UserProfile] = None
    department: Optional[str] = None
    position: Optional[str] = None
    experience_years: Optional[int] = None
    availability: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True