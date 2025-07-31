from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from database import Session_local
from schemas import UserCreate, UserLogin
from models import User, EmployeeProfile
from utils import hash_password, verify_password
from auth import create_access_token,decode_token

router = APIRouter()

# 🔐 Must be SAME as in create_access_token
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# HTTPBearer instead of OAuth2
oauth2_scheme = HTTPBearer()

# ✅ Dependency for DB session
def get_db():
    db = Session_local()
    try:
        yield db
    finally:
        db.close()

# ✅ Register route
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = User(
        username=user.username,
        email=user.email,
        role=user.role,
        hashed_password=hash_password(user.password),
        skills=user.skills
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if user.role == "employee":
        if not user.skills:
            raise HTTPException(status_code=400, detail="Skills required for employee registration")
        profile = EmployeeProfile(
            user_id=new_user.id,
            skills=user.skills  # Keep as list for JSON field
        )
        db.add(profile)
        db.commit()

    return {"message": "User registered successfully"}

# ✅ Login route (returns Bearer Token)
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": db_user.email, "role": db_user.role})
    return {"access_token": token, "token_type": "bearer"}
