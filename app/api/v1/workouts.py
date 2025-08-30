from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
# from app.core.rate_limiter import rate_limiter
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.workout import (
    WorkoutRead, WorkoutCreate,
    WorkoutPlanRead, WorkoutPlanCreate,
    WorkoutSessionRead, WorkoutSessionCreate,
    WorkoutSessionUpdate
)
from app.services.workout import WorkoutService

router = APIRouter()

# Workout routes
@router.post("/workouts/", response_model=WorkoutRead)
def create_workout(
    workout: WorkoutCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new workout"""
    return WorkoutService.create_workout(db, workout, current_user)

@router.get("/workouts/{workout_id}", response_model=WorkoutRead)
def get_workout(
    workout_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workout details"""
    return WorkoutService.get_workout(db, workout_id, current_user)

@router.get("/workouts/", response_model=List[WorkoutRead])
def list_workouts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    include_public: bool = True,
    difficulty: Optional[str] = None
):
    """List workouts"""
    return WorkoutService.list_workouts(
        db,
        current_user,
        skip=skip,
        limit=limit,
        include_public=include_public,
        difficulty=difficulty
    )

# Workout Plan routes
@router.post("/workout-plans/", response_model=WorkoutPlanRead)
def create_workout_plan(
    plan: WorkoutPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new workout plan"""
    return WorkoutService.create_workout_plan(db, plan, current_user)

# Workout Session routes
@router.post("/workout-sessions/", response_model=WorkoutSessionRead)
def start_workout_session(
    session: WorkoutSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new workout session"""
    return WorkoutService.start_workout_session(db, session, current_user)

@router.post("/workout-sessions/{session_id}/complete", response_model=WorkoutSessionRead)
def complete_workout_session(
    session_id: str,
    update_data: WorkoutSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete a workout session"""
    return WorkoutService.complete_workout_session(db, session_id, update_data, current_user)
