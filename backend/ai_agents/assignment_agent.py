# assignment_logic.py

from sqlalchemy.orm import Session
from models import EmployeeProfile
import logging

# Set up logging to help debug issues
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def match_employees_by_skills(db: Session, required_skills: list):
    """
    Match employees based on their skills against required skills.
    Returns the best matching employee profile or None if no match found.
    """
    if not required_skills:
        logger.warning("No required skills provided")
        return None
    
    matched = []
    required_skills_lower = [s.strip().lower() for s in required_skills if s.strip()]
    
    if not required_skills_lower:
        logger.warning("No valid required skills after processing")
        return None

    try:
        # Query available employees
        profiles = db.query(EmployeeProfile).filter(
            EmployeeProfile.is_available.is_(True)
        ).all()
        
        logger.info(f"Found {len(profiles)} available employees")
        
        if not profiles:
            logger.warning("No available employees found")
            return None

        for profile in profiles:
            # Skip if no skills defined
            if not profile.skills:
                logger.debug(f"Employee {profile.user.id if profile.user else 'Unknown'} has no skills defined")
                continue

            # Normalize and parse skills
            user_skills = normalize_skills(profile.skills)
            
            if not user_skills:
                logger.debug(f"Employee {profile.user.id if profile.user else 'Unknown'} has no valid skills")
                continue

            # Calculate match score
            matching_skills = set(required_skills_lower) & set(user_skills)
            match_score = len(matching_skills)
            match_percentage = (match_score / len(required_skills_lower)) * 100

            logger.debug(f"Employee {profile.user.id if profile.user else 'Unknown'}: "
                        f"Skills: {user_skills}, Match score: {match_score}, "
                        f"Match percentage: {match_percentage:.1f}%")

            if match_score > 0:
                matched.append({
                    'profile': profile,
                    'match_score': match_score,
                    'match_percentage': match_percentage,
                    'matching_skills': list(matching_skills)
                })

        if not matched:
            logger.warning("No employees found with matching skills")
            return None

        # Sort by match score (descending), then by match percentage
        matched.sort(key=lambda x: (x['match_score'], x['match_percentage']), reverse=True)
        
        best_match = matched[0]
        logger.info(f"Best match: Employee {best_match['profile'].user.id if best_match['profile'].user else 'Unknown'} "
                   f"with {best_match['match_score']} matching skills "
                   f"({best_match['match_percentage']:.1f}% match)")
        
        return best_match['profile']

    except Exception as e:
        logger.error(f"Error in match_employees_by_skills: {str(e)}")
        return None


def normalize_skills(skills):
    """
    Normalize skills from various formats (string, list, etc.) to a clean list.
    """
    user_skills = []
    
    try:
        if isinstance(skills, list):
            user_skills = [s.strip().lower() for s in skills if s and s.strip()]
        elif isinstance(skills, str):
            # Handle comma-separated, semicolon-separated, or pipe-separated skills
            for delimiter in [',', ';', '|']:
                if delimiter in skills:
                    user_skills = [s.strip().lower() for s in skills.split(delimiter) if s and s.strip()]
                    break
            else:
                # If no delimiter found, treat as single skill
                user_skills = [skills.strip().lower()] if skills.strip() else []
        else:
            logger.warning(f"Unexpected skills format: {type(skills)}")
            
    except Exception as e:
        logger.error(f"Error normalizing skills: {str(e)}")
        
    return user_skills


def auto_assign_agent(db: Session, skills: list, task_id: str = None):
    """
    Auto-assign a task to the best matching available employee.
    """
    logger.info(f"Starting auto-assignment for skills: {skills}")
    
    if not skills:
        logger.warning("No skills provided for assignment")
        return {
            "success": False,
            "assigned_to": None,
            "message": "No skills provided for assignment"
        }

    try:
        best_match = match_employees_by_skills(db, skills)

        if best_match:
            # Verify the employee profile has a valid user relationship
            if not best_match.user:
                logger.error(f"Employee profile {best_match.id} has no associated user")
                return {
                    "success": False,
                    "assigned_to": None,
                    "message": "Selected employee has no valid user account"
                }

            # Mark employee as unavailable
            best_match.is_available = False
            
            try:
                db.commit()
                logger.info(f"Successfully assigned task {task_id or 'Unknown'} to user {best_match.user.id}")
                
                return {
                    "success": True,
                    "assigned_to": best_match.user.id,
                    "employee_profile_id": best_match.id,
                    "message": f"Task assigned to user {best_match.user.id}"
                }
                
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to commit assignment: {str(e)}")
                return {
                    "success": False,
                    "assigned_to": None,
                    "message": f"Database error during assignment: {str(e)}"
                }
        else:
            logger.warning("No suitable employee found for assignment")
            return {
                "success": False,
                "assigned_to": None,
                "message": "No available employees found with matching skills"
            }

    except Exception as e:
        logger.error(f"Error in auto_assign_agent: {str(e)}")
        db.rollback()
        return {
            "success": False,
            "assigned_to": None,
            "message": f"Assignment failed: {str(e)}"
        }


def get_available_employees_with_skills(db: Session):
    """
    Helper function to get all available employees and their skills for debugging.
    """
    try:
        profiles = db.query(EmployeeProfile).filter(
            EmployeeProfile.is_available.is_(True)
        ).all()
        
        employees_info = []
        for profile in profiles:
            user_skills = normalize_skills(profile.skills) if profile.skills else []
            employees_info.append({
                'user_id': profile.user.id if profile.user else None,
                'profile_id': profile.id,
                'skills': user_skills,
                'raw_skills': profile.skills
            })
        
        return employees_info
    except Exception as e:
        logger.error(f"Error getting available employees: {str(e)}")
        return []


def release_employee(db: Session, user_id: int):
    """
    Release an employee back to available status after task completion.
    """
    try:
        profile = db.query(EmployeeProfile).filter(
            EmployeeProfile.user_id == user_id
        ).first()
        
        if profile:
            profile.is_available = True
            db.commit()
            logger.info(f"Released employee {user_id} back to available status")
            return True
        else:
            logger.warning(f"No employee profile found for user {user_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error releasing employee {user_id}: {str(e)}")
        db.rollback()
        return False