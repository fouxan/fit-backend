from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.dependencies import get_current_user, get_current_active_superuser
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.services.user import UserService

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get current user information
    """
    return current_user


@router.put("/me", response_model=UserRead)
async def update_current_user(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Update current user information
    """
    updated_user = UserService.update_user(db, str(current_user.id), user_update)
    return updated_user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
    db: Session = Depends(get_db)
):
    """
    Get specific user by ID (admin only)
    """
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/", response_model=List[UserRead])
async def get_users(
    current_user: Annotated[User, Depends(get_current_active_superuser)],
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all users (admin only)
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users
