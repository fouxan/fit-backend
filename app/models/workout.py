# app/models/workout.py
import uuid
from sqlalchemy import Column, String, Text, Integer, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.mixins import TimeStampMixin
from app.models.enums import WorkoutDifficulty, WorkoutStatus


class Workout(Base, TimeStampMixin):
    __tablename__ = "workouts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    difficulty = Column(
        Enum(WorkoutDifficulty, name="workoutdifficulty"), nullable=False
    )
    estimated_duration = Column(Integer)
    calories_burn_estimate = Column(Integer)
    is_public = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    created_by = relationship("User", backref="created_workouts")
    exercises = relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan"
    )
    workout_plans = relationship(
        "WorkoutPlan", secondary="workout_plan_workouts", back_populates="workouts"
    )
    sessions = relationship(
        "WorkoutSession", back_populates="workout", cascade="all, delete-orphan"
    )


class WorkoutExercise(Base, TimeStampMixin):
    __tablename__ = "workout_exercises"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workouts.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exercise_catalog.id", ondelete="CASCADE"),
        nullable=False,
    )
    order = Column(Integer, nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer)
    duration = Column(Integer)
    rest_duration = Column(Integer)
    notes = Column(Text)
    rep_scheme = Column(JSONB)

    workout = relationship("Workout", back_populates="exercises")
    exercise = relationship("ExerciseCatalog")


class WorkoutPlan(Base, TimeStampMixin):
    __tablename__ = "workout_plans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    duration_weeks = Column(Integer, nullable=False)
    difficulty = Column(
        Enum(WorkoutDifficulty, name="workoutdifficulty"), nullable=False
    )
    is_public = Column(Boolean, default=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", backref="created_workout_plans")
    workouts = relationship(
        "Workout", secondary="workout_plan_workouts", back_populates="workout_plans"
    )


class WorkoutPlanWorkout(Base):
    __tablename__ = "workout_plan_workouts"
    workout_plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workout_plans.id", ondelete="CASCADE"),
        primary_key=True,
    )
    workout_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workouts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    week_number = Column(Integer, nullable=False)
    day_number = Column(Integer, nullable=False)


class WorkoutSession(Base, TimeStampMixin):
    __tablename__ = "workout_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    workout_id = Column(UUID(as_uuid=True), ForeignKey("workouts.id"), nullable=False)
    start_time = Column(TimeStampMixin.created_at.type)  # DateTime(tz)
    end_time = Column(TimeStampMixin.updated_at.type)
    status = Column(
        Enum(WorkoutStatus, name="workoutstatus"),
        nullable=False,
        default=WorkoutStatus.NOT_STARTED,
    )
    notes = Column(Text)
    total_duration = Column(Integer)
    calories_burned = Column(Integer)
    mood_rating = Column(Integer)
    difficulty_rating = Column(Integer)

    user = relationship("User", backref="workout_sessions")
    workout = relationship("Workout", back_populates="sessions")
    # exercise_sets = relationship(
    #     "ExerciseSet", back_populates="workout_session", cascade="all, delete-orphan"
    # )
