# app/schemas/workout.py
from typing import Optional, List, Dict, Any
from pydantic import UUID4
from datetime import datetime
from .common import ORMModel
from .enums import WorkoutDifficulty, WorkoutStatus
from .catalog import ExerciseRead


class WorkoutExerciseBase(ORMModel):
    exercise_id: UUID4
    order: int
    sets: int
    reps: Optional[int] = None
    duration: Optional[int] = None  # seconds
    rest_duration: Optional[int] = None
    notes: Optional[str] = None
    rep_scheme: Optional[Dict[str, int]] = None


class WorkoutExerciseCreate(WorkoutExerciseBase):
    pass


class WorkoutExerciseRead(WorkoutExerciseBase):
    id: UUID4
    workout_id: UUID4
    exercise: ExerciseRead
    created_at: datetime
    updated_at: datetime


class WorkoutBase(ORMModel):
    name: str
    description: Optional[str] = None
    difficulty: WorkoutDifficulty
    estimated_duration: Optional[int] = None
    calories_burn_estimate: Optional[int] = None
    is_public: bool = False
    is_template: bool = False


class WorkoutCreate(WorkoutBase):
    exercises: List[WorkoutExerciseCreate]


class WorkoutRead(WorkoutBase):
    id: UUID4
    created_by_id: UUID4
    exercises: List[WorkoutExerciseRead]
    created_at: datetime
    updated_at: datetime


class WorkoutPlanWorkoutCreate(ORMModel):
    workout_id: UUID4
    week_number: int  # 1+
    day_number: int  # 1-7


class WorkoutPlanBase(ORMModel):
    name: str
    description: Optional[str] = None
    duration_weeks: int
    difficulty: WorkoutDifficulty
    is_public: bool = False


class WorkoutPlanCreate(WorkoutPlanBase):
    workouts: List[WorkoutPlanWorkoutCreate]


class WorkoutPlanWorkoutRead(WorkoutPlanWorkoutCreate):
    workout: WorkoutRead


class WorkoutPlanRead(WorkoutPlanBase):
    id: UUID4
    created_by_id: UUID4
    workouts: List[WorkoutPlanWorkoutRead]
    created_at: datetime
    updated_at: datetime


class WorkoutSessionBase(ORMModel):
    workout_id: UUID4
    notes: Optional[str] = None


class WorkoutSessionCreate(WorkoutSessionBase):
    pass


class WorkoutSessionUpdate(ORMModel):
    notes: Optional[str] = None
    mood_rating: Optional[int] = None  # 1-5
    difficulty_rating: Optional[int] = None  # 1-5


class WorkoutSessionRead(WorkoutSessionBase):
    id: UUID4
    user_id: UUID4
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: WorkoutStatus
    total_duration: Optional[int] = None
    calories_burned: Optional[int] = None
    mood_rating: Optional[int] = None
    difficulty_rating: Optional[int] = None
    created_at: datetime
    updated_at: datetime
