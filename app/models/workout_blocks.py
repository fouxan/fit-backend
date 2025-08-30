# app/models/workout_blocks.py
import uuid
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.mixins import TimeStampMixin
from app.models.enums import SetType

# IMPORTANT: workout_block_type_enum exists in DB; reference by name to avoid re-creating
from sqlalchemy import Enum as SAEnum
from app.models.enums import WorkoutBlockType


class WorkoutBlock(Base, TimeStampMixin):
    __tablename__ = "workout_blocks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workouts.id", ondelete="CASCADE"),
        nullable=False,
    )
    block_order = Column(Integer, nullable=False)
    block_name = Column(String(100))
    block_type = Column(
        SAEnum(WorkoutBlockType, name="workout_block_type_enum"),
        nullable=False,
        server_default="straight_sets",
    )
    rest_between_exercises = Column(Integer)
    rounds = Column(Integer, default=1, nullable=False)
    round_rest_seconds = Column(Integer)
    notes = Column(Text)

    exercises = relationship(
        "WorkoutBlockExercise", back_populates="block", cascade="all, delete-orphan"
    )


class WorkoutBlockExercise(Base):
    __tablename__ = "workout_block_exercises"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_block_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workout_blocks.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exercise_catalog.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_order = Column(Integer, nullable=False)

    target_sets = Column(Integer)
    target_reps_min = Column(Integer)
    target_reps_max = Column(Integer)
    target_weight_kg = Column(
        Text
    )  # Numeric in DB; Text works but you can import Numeric(6,2)
    target_rpe = Column(Text)  # Numeric(3,1)

    rest_after_seconds = Column(Integer)
    tempo_prescription = Column(String(20))
    equipment_variant = Column(JSONB)
    notes = Column(Text)

    block = relationship("WorkoutBlock", back_populates="exercises")
    exercise = relationship("ExerciseCatalog")
