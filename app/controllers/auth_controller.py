from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.config import settings
from app.core.rate_limit import limiter
from app.core.security import create_access_token, verify_password, ALGORITHM
from app.repositories.user_repository import get_user_by_username
from app.entities.user import User
from app.services.auth_service import (
    register as svc_register,
    login as svc_login,
    change_password as svc_change_password,
    admin_reset_password as svc_admin_reset_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api-deutsche/auth/login-with-token")


class LoginDTO(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None


class UserPublic(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    password: str


class ChangePasswordDTO(BaseModel):
    old_password: str
    new_password: str


class AdminResetPasswordDTO(BaseModel):
    new_password: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _access_token_expiry_seconds() -> int:
    minutes = int(getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    return minutes * 60


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise _credentials_exception()
    except JWTError:
        raise _credentials_exception()

    user = get_user_by_username(db, username=username)
    if user is None:
        raise _credentials_exception()
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    user = svc_register(db, data.username, data.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    return {"message": "User created successfully", "user_id": user.id}


@router.post("/login-with-token", response_model=Token)
@limiter.limit("10/minute")
def issue_token(
    request: Request,
    data: LoginDTO,
    db: Session = Depends(get_db),
):
    user = get_user_by_username(db, data.username)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    expires_minutes = int(getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    token = create_access_token(
        data={"sub": user.username, "id": user.id},
        expires_delta=timedelta(minutes=expires_minutes),
    )
    return Token(access_token=token, expires_in=_access_token_expiry_seconds())


@router.post("/login", response_model=Token)
def login_user_legacy(data: UserCreate, db: Session = Depends(get_db)):
    user = svc_login(db, data.username, data.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    expires_minutes = int(getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    token = create_access_token(
        data={"sub": user.username, "id": user.id},
        expires_delta=timedelta(minutes=expires_minutes),
    )
    return Token(access_token=token, expires_in=_access_token_expiry_seconds())


@router.get("/me", response_model=UserPublic)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/change-password/{user_id}")
def change_password_user(
    user_id: int,
    data: ChangePasswordDTO,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")

    user, err = svc_change_password(db, user_id, data.old_password, data.new_password)
    if err == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if err == "bad_old":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")
    return {"message": "Password changed", "user_id": user.id}


@router.patch("/admin/reset-password/{user_id}")
def admin_reset_password_user(
    user_id: int,
    data: AdminResetPasswordDTO,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = svc_admin_reset_password(db, user_id, data.new_password)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "Password reset", "user_id": user.id}
