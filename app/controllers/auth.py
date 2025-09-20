# app/controllers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models import schemas, models
from ..services.auth_service import create_user, login_user, get_user_by_email
from ..utils.dependencies import get_db, get_current_user_email

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = create_user(db, user)
    return schemas.UserResponse(
        id=db_user.id,
        email=db_user.email,
        is_active=db_user.is_active,
        created_at=db_user.created_at.isoformat()
    )

@router.post("/login", response_model=schemas.Token)
async def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login a user and return access token."""
    return login_user(db, user_credentials)

@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user(
    email: str = Depends(get_current_user_email), 
    db: Session = Depends(get_db)
):
    """Get current user information."""
    user = get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return schemas.UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at.isoformat()
    )
