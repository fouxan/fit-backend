from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    ForeignKey,
    Text,
    Enum,
    Float,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.base import TimeStampMixin
import uuid
import enum


class WorkoutDifficulty(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class WorkoutStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Workout(Base, TimeStampMixin):
    __tablename__ = "workouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(Enum(WorkoutDifficulty), nullable=False)
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    calories_burn_estimate = Column(Integer, nullable=True)
    is_public = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    exercises = relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan"
    )
    created_by = relationship("User", backref="created_workouts")
    workout_plans = relationship(
        "WorkoutPlan", secondary="workout_plan_workouts", back_populates="workouts"
    )
    sessions = relationship("WorkoutSession", back_populates="workout")


class WorkoutExercise(Base, TimeStampMixin):
    __tablename__ = "workout_exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_id = Column(UUID(as_uuid=True), ForeignKey("workouts.id"), nullable=False)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=False)
    order = Column(Integer, nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=True)  # Nullable for time-based exercises
    duration = Column(Integer, nullable=True)  # in seconds, for time-based exercises
    rest_duration = Column(Integer, nullable=True)  # rest time in seconds
    notes = Column(Text, nullable=True)

    # For variable rep schemes
    rep_scheme = Column(
        JSONB, nullable=True
    )  # e.g., {"1": 12, "2": 10, "3": 8} for pyramid sets

    # Relationships
    workout = relationship("Workout", back_populates="exercises")
    exercise = relationship("ExerciseCatalog")


class WorkoutPlan(Base, TimeStampMixin):
    __tablename__ = "workout_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    duration_weeks = Column(Integer, nullable=False)
    difficulty = Column(Enum(WorkoutDifficulty), nullable=False)
    is_public = Column(Boolean, default=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    workouts = relationship(
        "Workout", secondary="workout_plan_workouts", back_populates="workout_plans"
    )
    created_by = relationship("User", backref="created_workout_plans")


class WorkoutPlanWorkout(Base):
    __tablename__ = "workout_plan_workouts"

    workout_plan_id = Column(
        UUID(as_uuid=True), ForeignKey("workout_plans.id"), primary_key=True
    )
    workout_id = Column(UUID(as_uuid=True), ForeignKey("workouts.id"), primary_key=True)
    week_number = Column(Integer, nullable=False)
    day_number = Column(Integer, nullable=False)  # 1-7 for days of the week


class WorkoutSession(Base, TimeStampMixin):
    __tablename__ = "workout_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    workout_id = Column(UUID(as_uuid=True), ForeignKey("workouts.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(
        Enum(WorkoutStatus), nullable=False, default=WorkoutStatus.NOT_STARTED
    )
    notes = Column(Text, nullable=True)

    # Performance metrics
    total_duration = Column(Integer, nullable=True)  # in seconds
    calories_burned = Column(Integer, nullable=True)
    mood_rating = Column(Integer, nullable=True)  # 1-5 scale
    difficulty_rating = Column(Integer, nullable=True)  # 1-5 scale

    # Relationships
    user = relationship("User", backref="workout_sessions")
    workout = relationship("Workout", back_populates="sessions")
    exercise_sets = relationship(
        "ExerciseSet", back_populates="workout_session", cascade="all, delete-orphan"
    )


class ExerciseSet(Base, TimeStampMixin):
    __tablename__ = "exercise_sets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_session_id = Column(
        UUID(as_uuid=True), ForeignKey("workout_sessions.id"), nullable=False
    )
    workout_exercise_id = Column(
        UUID(as_uuid=True), ForeignKey("workout_exercises.id"), nullable=False
    )
    set_number = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)  # in kg
    duration = Column(Integer, nullable=True)  # in seconds for time-based exercises
    rpe = Column(Integer, nullable=True)  # Rate of Perceived Exertion (1-10)
    notes = Column(Text, nullable=True)

    # Relationships
    workout_session = relationship("WorkoutSession", back_populates="exercise_sets")
    workout_exercise = relationship("WorkoutExercise")
