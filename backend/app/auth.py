from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database.models import User
from backend.auth.jwt_handler import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    payload = decode_access_token(token)
    if payload is None: raise credentials_exception
    email: str = payload.get("sub")
    role: str = payload.get("role", "user")
    user = db.query(User).filter(User.email == email).first()
    if user is None: raise credentials_exception
    # Return as dict to match your provided code
    return {"id": user.id, "email": user.email, "company_name": user.company_name, "role": role}
