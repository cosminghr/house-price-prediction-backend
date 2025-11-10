from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.services.user_service import list_users, get_user_by_id, update_user, delete_user, delete_all_users

router = APIRouter()


class UserRead(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=List[UserRead])
def get_users(db=Depends(get_db)):
    return list_users(db)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db=Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def patch_user(user_id: int, data: UserUpdate, db=Depends(get_db)):
    user = update_user(db, user_id, username=data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("")
def delete_users(db=Depends(get_db)):
    count = delete_all_users(db)
    return {"message": "All users deleted", "deleted": count}


@router.delete("/{user_id}")
def delete_user_by_id(user_id: int, db=Depends(get_db)):
    ok = delete_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User deleted", "user_id": user_id}
