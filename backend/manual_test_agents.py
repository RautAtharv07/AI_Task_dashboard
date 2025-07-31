#!/usr/bin/env python3
"""
Manual Testing Script for AI Agents
Run this script to interactively test your AI agents
"""

import os
import sys
from sqlalchemy.orm import Session
from database import Session_local
from models import User, Task, EmployeeProfile
from ai_agents.assignment_agent import extract_skills_from_task, match_employees_by_skills, auto_assign_agent
from ai_agents.summary_agent import generate_summary_for_user
from ai_agents.llm_client import get_summary_from_llm
from datetime import datetime
import json

def get_db():
    """Get database session"""
    db = Session_local()
    try:
        return db
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def setup_test_data(db: Session):
    """Set up test data for manual testing"""
    print("Setting up test data...")
    
    # Check if test users already exist
    existing_users = db.query(User).filter(User.email.like("%@test.com")).all()
    if existing_users:
        print("Test users already exist. Skipping setup.")
        return existing_users
    
    # Create test users
    users = []
    
    # Admin user
    admin = User(
        username="admin_test",
        email="admin@test.com",
        role="admin",
        hashed_password="hashed_password",
        skills=["Python", "Management", "Leadership"]
    )
    users.append(admin)
    
    # Employee 1 - Python developer
    emp1 = User(
        username="john_python",
        email="john@test.com",
        role="employee",
        hashed_password="hashed_password",
        skills=["Python", "Django", "FastAPI", "SQLAlchemy"]
    )
    users.append(emp1)
    
    # Employee 2 - JavaScript developer
    emp2 = User(
        username="jane_js",
        email="jane@test.com",
        role="employee",
        hashed_password="hashed_password",
        skills=["JavaScript", "React", "Node.js", "Express"]
    )
    users.append(emp2)
    
    # Employee 3 - Full stack developer
    emp3 = User(
        username="bob_fullstack",
        email="bob@test.com",
        role="employee",
        hashed_password="hashed_password",
        skills=["Python", "JavaScript", "React", "Django", "PostgreSQL"]
    )
    users.append(emp3)
    
    db.add_all(users)
    db.commit()
    
    # Create employee profiles
    profiles = []
    for user in users[1:]:  # Skip admin
        profile = EmployeeProfile(
            user_id=user.id,
            is_available=True,
            skills=user.skills
        )
        profiles.append(profile)
    
    db.add_all(profiles)
    db.commit()
    
    # Create some test tasks
    tasks = []
    
    task1 = Task(
        title="Build REST API",
        description="Create a REST API using FastAPI and SQLAlchemy for user management",
        assignee_id=emp1.id,
        status="pending",
        created_at=datetime.utcnow(),
        status_updated_at=datetime.utcnow()
    )
    tasks.append(task1)
    
    task2 = Task(
        title="Frontend Dashboard",
        description="Build a React dashboard with charts and user interface components",
        assignee_id=emp2.id,
        status="in_progress",
        created_at=datetime.utcnow(),
        status_updated_at=datetime.utcnow()
    )
    tasks.append(task2)
    
    task3 = Task(
        title="Full Stack Application",
        description="Develop a complete web application with Django backend and React frontend",
        assignee_id=emp3.id,
        status="completed",
        created_at=datetime.utcnow(),
        status_updated_at=datetime.utcnow()
    )
    tasks.append(task3)
    
    db.add_all(tasks)
    db.commit()
    
    print(f"Created {len(users)} users and {len(tasks)} tasks")
    return users

def test_skill_extraction():
    """Test skill extraction from task descriptions"""
    print("\n" + "="*50)
    print("TESTING SKILL EXTRACTION")
    print("="*50)
    
    test_cases = [
        {
            "title": "Build Python API",
            "description": "Create a REST API using FastAPI and SQLAlchemy for user management"
        },
        {
            "title": "Frontend Development",
            "description": "Build React components with TypeScript and Material-UI"
        },
        {
            "title": "Database Design",
            "description": "Design PostgreSQL schema and implement database migrations"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Title: {case['title']}")
        print(f"Description: {case['description']}")
        
        try:
            skills = extract_skills_from_task(case['title'], case['description'])
            print(f"Extracted Skills: {skills}")
        except Exception as e:
            print(f"Error: {e}")

def test_employee_matching(db: Session):
    """Test employee matching based on skills"""
    print("\n" + "="*50)
    print("TESTING EMPLOYEE MATCHING")
    print("="*50)
    
    test_skills = [
        ["Python", "Django"],
        ["JavaScript", "React"],
        ["Python", "JavaScript", "React"],
        ["Machine Learning", "TensorFlow"],
        ["PostgreSQL", "Database Design"]
    ]
    
    for i, skills in enumerate(test_skills, 1):
        print(f"\nTest Case {i}:")
        print(f"Required Skills: {skills}")
        
        try:
            matched_user = match_employees_by_skills(db, skills)
            if matched_user:
                print(f"Matched User: {matched_user.username} ({matched_user.email})")
                print(f"User Skills: {matched_user.skills}")
            else:
                print("No matching employee found")
        except Exception as e:
            print(f"Error: {e}")

def test_auto_assignment(db: Session):
    """Test automatic task assignment"""
    print("\n" + "="*50)
    print("TESTING AUTO ASSIGNMENT")
    print("="*50)
    
    test_tasks = [
        {
            "title": "Python Backend Development",
            "description": "Build a Django application with REST API endpoints"
        },
        {
            "title": "React Frontend",
            "description": "Create React components with TypeScript and Redux"
        },
        {
            "title": "Full Stack Project",
            "description": "Develop a complete web application with Django and React"
        }
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\nTest Case {i}:")
        print(f"Task: {task['title']}")
        print(f"Description: {task['description']}")
        
        try:
            result = auto_assign_agent(db, task['title'], task['description'])
            print(f"Skills Extracted: {result['skills_extracted']}")
            
            if result['assigned_to']:
                assigned_user = db.query(User).filter(User.id == result['assigned_to']).first()
                print(f"Assigned to: {assigned_user.username} ({assigned_user.email})")
            else:
                print("No assignment made")
        except Exception as e:
            print(f"Error: {e}")

def test_summary_generation(db: Session):
    """Test summary generation for users"""
    print("\n" + "="*50)
    print("TESTING SUMMARY GENERATION")
    print("="*50)
    
    # Get all employee users
    employees = db.query(User).filter(User.role == "employee").all()
    
    for employee in employees:
        print(f"\nGenerating summary for: {employee.username} ({employee.email})")
        
        try:
            result = generate_summary_for_user(db, employee.id)
            print(f"Summary: {result['result']}")
        except Exception as e:
            print(f"Error: {e}")

def test_llm_client():
    """Test LLM client directly"""
    print("\n" + "="*50)
    print("TESTING LLM CLIENT")
    print("="*50)
    
    test_prompts = [
        "User completed 3 tasks today: API development, frontend work, and testing",
        "No tasks were completed today",
        "User worked on Python backend and React frontend components"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest Case {i}:")
        print(f"Prompt: {prompt}")
        
        try:
            summary = get_summary_from_llm(prompt)
            print(f"Summary: {summary}")
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main testing function"""
    print("AI Agents Manual Testing")
    print("="*50)
    
    # Check environment variables
    required_env_vars = ["TOGETHER_API_KEY", "ALLTOGETHER_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Warning: Missing environment variables: {missing_vars}")
        print("Some tests may fail without proper API keys")
        print("Set these variables in your .env file")
    
    # Get database connection
    db = get_db()
    if not db:
        print("Failed to connect to database")
        return
    
    try:
        # Set up test data
        users = setup_test_data(db)
        
        # Run tests
        while True:
            print("\n" + "="*50)
            print("MANUAL TESTING MENU")
            print("="*50)
            print("1. Test Skill Extraction")
            print("2. Test Employee Matching")
            print("3. Test Auto Assignment")
            print("4. Test Summary Generation")
            print("5. Test LLM Client")
            print("6. Run All Tests")
            print("7. Exit")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                test_skill_extraction()
            elif choice == "2":
                test_employee_matching(db)
            elif choice == "3":
                test_auto_assignment(db)
            elif choice == "4":
                test_summary_generation(db)
            elif choice == "5":
                test_llm_client()
            elif choice == "6":
                test_skill_extraction()
                test_employee_matching(db)
                test_auto_assignment(db)
                test_summary_generation(db)
                test_llm_client()
            elif choice == "7":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please enter 1-7.")
            
            input("\nPress Enter to continue...")
    
    finally:
        db.close()

if __name__ == "__main__":
    main() 