from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import User
from app.schemas import UserResponse
from app.auth import get_current_user

router = APIRouter(tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str
    password: str

class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str

@router.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Simple simulated local authentication for developer testing
    # Find or auto-create a user record for this email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        name = request.email.split("@")[0].capitalize()
        user = User(
            auth0_sub=f"auth0|local_{request.email.replace('@', '_')}",
            username=name,
            email=request.email,
            role="Personal"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Return a simulated token starting with "mock-token-" containing user info for local development
    mock_token = f"mock-token-{user.auth0_sub}:{user.email}:{user.username}"
    
    return {
        "access_token": mock_token,
        "user": {
            "id": user.id,
            "auth0_user_id": user.auth0_sub,
            "email": user.email,
            "name": user.username,
            "role": user.role,
        }
    }

@router.post("/auth/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        name = request.email.split("@")[0].capitalize()
        user = User(
            auth0_sub=f"auth0|local_{request.email.replace('@', '_')}",
            username=name,
            email=request.email,
            role="Personal"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    mock_token = f"mock-token-{user.auth0_sub}:{user.email}:{user.username}"
    return {
        "access_token": mock_token,
        "user": {
            "id": user.id,
            "auth0_user_id": user.auth0_sub,
            "email": user.email,
            "name": user.username,
            "role": user.role,
        }
    }

@router.get("/api/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        auth0_user_id=current_user.auth0_sub,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
