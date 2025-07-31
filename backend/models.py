from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON,DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String)
    hashed_password = Column(String)
    skills = Column(JSON, nullable=True, default=[]) # ✅ List of strings, e.g., ["Python", "Django"]
    availability = Column(Boolean, default=True)
    
    tasks = relationship("Task", back_populates="assignee")
    employee_profile = relationship("EmployeeProfile", back_populates="user", uselist=False)


class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    assignee_id = Column(Integer, ForeignKey(User.id)) 
    required_skills = Column(JSON, nullable=True, default=[])  # ✅ Also list of strings
    status = Column(String)  # "pending", "completed", etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    status_updated_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    
    assignee = relationship("User", back_populates="tasks")


class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    is_available = Column(Boolean, default=True)  # ❌ Removed redundant 'skills'
    skills = Column(JSON, nullable=True, default=[])

    user = relationship("User", back_populates="employee_profile")
