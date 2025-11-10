from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.services.auth_service import register, login, change_password, admin_reset_password

router = APIRouter()


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


@router.post("/register", status_code=201)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    user = register(db, data.username, data.password)
    if user is None:
        raise HTTPException(status_code=409, detail="Username already exists")
    return {"message": "User created successfully", "user_id": user.id}


@router.post("/login")
def login_user(data: UserCreate, db: Session = Depends(get_db)):
    user = login(db, data.username, data.password)
    if user is None:
        return {"error": "Invalid credentials"}
    return {"message": "Login successful", "user_id": user.id}


@router.patch("/change-password/{user_id}")
def change_password_user(user_id: int, data: ChangePasswordDTO, db: Session = Depends(get_db)):
    user, err = change_password(db, user_id, data.old_password, data.new_password)
    if err == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if err == "bad_old":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")
    return {"message": "Password changed", "user_id": user.id}


@router.patch("/admin/reset-password/{user_id}")
def admin_reset_password_user(user_id: int, data: AdminResetPasswordDTO, db: Session = Depends(get_db)):
    user = admin_reset_password(db, user_id, data.new_password)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "Password reset", "user_id": user.id}
