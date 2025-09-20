# app/utils/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..models import db as db_module
from ..services.auth_service import get_user_by_email
from .auth import verify_token, get_token_exception

security = HTTPBearer()

def get_db():
    db = db_module.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and verify the current user's email from the JWT token."""
    token = credentials.credentials
    email = verify_token(token)
    if email is None:
        raise get_token_exception()
    return email

def get_current_user(
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    """Get the current authenticated user."""
    user = get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
