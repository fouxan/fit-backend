from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
# from app.core.rate_limiter import rate_limiter
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.exercise import (
    Exercise, ExerciseCreate, ExerciseUpdate,
)
from app.services.exercise import ExerciseService

router = APIRouter()

@router.post("/exercises/", response_model=Exercise)
def create_exercise(
    exercise: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new custom exercise"""
    return ExerciseService.create_exercise(db, exercise, current_user)

@router.get("/exercises/{exercise_id}", response_model=Exercise)
def get_exercise(
    exercise_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get exercise details"""
    return ExerciseService.get_exercise(db, exercise_id)

@router.put("/exercises/{exercise_id}", response_model=Exercise)
def update_exercise(
    exercise_id: str,
    exercise: ExerciseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an exercise"""
    return ExerciseService.update_exercise(db, exercise_id, exercise, current_user)

@router.delete("/exercises/{exercise_id}")
def delete_exercise(
    exercise_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an exercise"""
    ExerciseService.delete_exercise(db, exercise_id, current_user)
    return {"status": "success"}

@router.get("/exercises/", response_model=List[Exercise])
def list_exercises(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[str] = None,
    difficulty: Optional[str] = None,
    equipment_id: Optional[str] = None,
    muscle_group_id: Optional[str] = None,
    include_custom: bool = True
):
    """List exercises with optional filters"""
    return ExerciseService.list_exercises(
        db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        difficulty=difficulty,
        equipment_id=equipment_id,
        muscle_group_id=muscle_group_id,
        include_custom=include_custom
    )
