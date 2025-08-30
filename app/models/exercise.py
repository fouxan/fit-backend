# app/models/exercise.py
import uuid
from sqlalchemy import Column, String, Text, Boolean, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.mixins import TimeStampMixin
from app.models.enums import DifficultyLevel, Mechanics


# Junctions
class ExerciseMuscleGroup(Base):
    __tablename__ = "exercise_muscle_groups"
    exercise_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exercise_catalog.id", ondelete="CASCADE"),
        primary_key=True,
    )
    muscle_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("muscle_groups.id", ondelete="CASCADE"),
        primary_key=True,
    )


class ExerciseEquipment(Base):
    __tablename__ = "exercise_equipment"
    exercise_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exercise_catalog.id", ondelete="CASCADE"),
        primary_key=True,
    )
    equipment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("equipment.id", ondelete="CASCADE"),
        primary_key=True,
    )


class ExerciseMovementPattern(Base):
    __tablename__ = "exercise_movement_patterns"
    exercise_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exercise_catalog.id", ondelete="CASCADE"),
        primary_key=True,
    )
    movement_pattern_id = Column(
        UUID(as_uuid=True),
        ForeignKey("movement_patterns.id", ondelete="CASCADE"),
        primary_key=True,
    )


class MuscleGroup(Base, TimeStampMixin):
    __tablename__ = "muscle_groups"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    exercises = relationship(
        "ExerciseCatalog",
        secondary=ExerciseMuscleGroup.__table__,
        back_populates="muscle_groups",
    )


class Equipment(Base, TimeStampMixin):
    __tablename__ = "equipment"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    exercises = relationship(
        "ExerciseCatalog",
        secondary=ExerciseEquipment.__table__,
        back_populates="equipment",
    )


class ExerciseCategory(Base, TimeStampMixin):
    __tablename__ = "exercise_categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    exercises = relationship("ExerciseCatalog", back_populates="category")


class MovementPattern(Base, TimeStampMixin):
    __tablename__ = "movement_patterns"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    exercises = relationship(
        "ExerciseCatalog",
        secondary=ExerciseMovementPattern.__table__,
        back_populates="movement_patterns",
    )


class ExerciseCatalog(Base, TimeStampMixin):
    __tablename__ = "exercise_catalog"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    instructions = Column(Text)
    difficulty = Column(Enum(DifficultyLevel, name="difficultylevel"), nullable=False)
    is_custom = Column(Boolean, default=False, nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    category_id = Column(
        UUID(as_uuid=True), ForeignKey("exercise_categories.id"), nullable=False
    )
    video_url = Column(String)
    image_urls = Column(ARRAY(String))
    mechanics = Column(
        Enum(Mechanics, name="mechanics_enum"),
        nullable=False,
        server_default="compound",
    )
    unilateral = Column(Boolean, default=False, nullable=False)
    default_tempo = Column(String)
    is_bodyweight = Column(Boolean, default=False, nullable=False)
    supports_gps = Column(Boolean, default=False, nullable=False)
    supports_pool = Column(Boolean, default=False, nullable=False)
    supports_hr = Column(Boolean, default=True, nullable=False)
    cadence_metric = Column(String)
    notes = Column(ARRAY(Text))
    default_sport_profile = Column(String)

    category = relationship("ExerciseCategory", back_populates="exercises")
    muscle_groups = relationship(
        "MuscleGroup", secondary="exercise_muscle_groups", back_populates="exercises"
    )
    movement_patterns = relationship(
        "MovementPattern",
        secondary="exercise_movement_patterns",
        back_populates="exercises",
    )
    equipment = relationship(
        "Equipment", secondary="exercise_equipment", back_populates="exercises"
    )
