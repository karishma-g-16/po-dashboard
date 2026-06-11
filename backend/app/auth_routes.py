from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from backend.database.db import get_db
from backend.database.models import User
from backend.app.schemas import UserCreate, UserResponse, Token
from backend.auth.password import get_password_hash, verify_password
from backend.auth.jwt_handler import create_access_token
from backend.app.auth import get_current_user
from datetime import datetime, timedelta, timezone
import random
import string
from backend.app.schemas import UserCreate, UserResponse, Token, ForgotPasswordRequest, VerifyCodeRequest, ResetPasswordRequest
from backend.utils.email import send_reset_code_email

router = APIRouter(prefix="/api/auth", tags=["auth"])

def generate_reset_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user: raise HTTPException(status_code=400, detail="Email registered")
    new_user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        company_name=user_in.company_name,
        first_name=user_in.first_name,
        last_name=user_in.last_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        # We don't want to reveal if a user exists or not for security
        return {"message": "If the email is registered, a reset code has been sent."}

    code = generate_reset_code()
    user.reset_code = code
    user.reset_code_expires = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.commit()

    success = send_reset_code_email(user.email, code)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email")

    return {"message": "Reset code sent successfully"}

@router.post("/verify-code")
def verify_code(req: VerifyCodeRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or user.reset_code != req.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    if user.reset_code_expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Verification code has expired")

    return {"success": True, "message": "Code verified"}

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or user.reset_code != req.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    if user.reset_code_expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Verification code has expired")

    user.password_hash = get_password_hash(req.new_password)
    user.reset_code = None
    user.reset_code_expires = None
    db.commit()

    return {"success": True, "message": "Password reset successfully"}

@router.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user["id"]).first()
    return user
