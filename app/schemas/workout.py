from typing import List, Optional, Dict, Union
from pydantic import BaseModel, UUID4, conint, confloat
from datetime import datetime
from enum import Enum
from .exercise import Exercise

class WorkoutDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class WorkoutStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class WorkoutExerciseBase(BaseModel):
    exercise_id: UUID4
    order: int
    sets: int
    reps: Optional[int] = None
    duration: Optional[int] = None  # in seconds
    rest_duration: Optional[int] = None  # in seconds
    notes: Optional[str] = None
    rep_scheme: Optional[Dict[str, int]] = None

class WorkoutExerciseCreate(WorkoutExerciseBase):
    pass

class WorkoutExercise(WorkoutExerciseBase):
    id: UUID4
    workout_id: UUID4
    exercise: Exercise
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class WorkoutBase(BaseModel):
    name: str
    description: Optional[str] = None
    difficulty: WorkoutDifficulty
    estimated_duration: Optional[int] = None
    calories_burn_estimate: Optional[int] = None
    is_public: bool = False
    is_template: bool = False

class WorkoutCreate(WorkoutBase):
    exercises: List[WorkoutExerciseCreate]

class Workout(WorkoutBase):
    id: UUID4
    created_by_id: UUID4
    exercises: List[WorkoutExercise]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ExerciseSetBase(BaseModel):
    set_number: int
    reps: Optional[int] = None
    weight: Optional[float] = None
    duration: Optional[int] = None
    rpe: Optional[conint(ge=1, le=10)] = None
    notes: Optional[str] = None

class ExerciseSetCreate(ExerciseSetBase):
    workout_exercise_id: UUID4

class ExerciseSet(ExerciseSetBase):
    id: UUID4
    workout_session_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class WorkoutSessionBase(BaseModel):
    workout_id: UUID4
    notes: Optional[str] = None

class WorkoutSessionCreate(WorkoutSessionBase):
    pass

class WorkoutSessionUpdate(BaseModel):
    notes: Optional[str] = None
    mood_rating: Optional[conint(ge=1, le=5)] = None
    difficulty_rating: Optional[conint(ge=1, le=5)] = None

class WorkoutSession(WorkoutSessionBase):
    id: UUID4
    user_id: UUID4
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: WorkoutStatus
    total_duration: Optional[int] = None
    calories_burned: Optional[int] = None
    mood_rating: Optional[int] = None
    difficulty_rating: Optional[int] = None
    exercise_sets: List[ExerciseSet]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class WorkoutPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration_weeks: int
    difficulty: WorkoutDifficulty
    is_public: bool = False

class WorkoutPlanWorkoutCreate(BaseModel):
    workout_id: UUID4
    week_number: conint(ge=1)
    day_number: conint(ge=1, le=7)

class WorkoutPlanCreate(WorkoutPlanBase):
    workouts: List[WorkoutPlanWorkoutCreate]

class WorkoutPlanWorkout(WorkoutPlanWorkoutCreate):
    workout: Workout

    class Config:
        orm_mode = True

class WorkoutPlan(WorkoutPlanBase):
    id: UUID4
    created_by_id: UUID4
    workouts: List[WorkoutPlanWorkout]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
