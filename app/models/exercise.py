from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.base import TimeStampMixin
from app.models.user import User
from app.models.subscription import Subscription
import uuid
import enum


class DifficultyLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


# Junction Tables
class ExerciseMuscleGroup(Base):
    __tablename__ = "exercise_muscle_groups"

    exercise_id = Column(
        UUID(as_uuid=True), ForeignKey("exercise_catalog.id"), primary_key=True
    )
    muscle_group_id = Column(
        UUID(as_uuid=True), ForeignKey("muscle_groups.id"), primary_key=True
    )


class ExerciseEquipment(Base):
    __tablename__ = "exercise_equipment"

    exercise_id = Column(
        UUID(as_uuid=True), ForeignKey("exercise_catalog.id"), primary_key=True
    )
    equipment_id = Column(
        UUID(as_uuid=True), ForeignKey("equipment.id"), primary_key=True
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
    description = Column(Text, nullable=True)

    # Relationships
    exercises = relationship(
        "ExerciseCatalog",
        secondary=ExerciseMuscleGroup.__table__,
        back_populates="muscle_groups",
    )


class Equipment(Base, TimeStampMixin):
    __tablename__ = "equipment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    exercises = relationship(
        "ExerciseCatalog",
        secondary=ExerciseEquipment.__table__,
        back_populates="equipment",
    )


class ExerciseCategory(Base, TimeStampMixin):
    __tablename__ = "exercise_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    exercises = relationship("ExerciseCatalog", back_populates="category")


class MovementPattern(Base, TimeStampMixin):
    __tablename__ = "movement_patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    exercises = relationship(
        "ExerciseCatalog",
        secondary=ExerciseMovementPattern.__table__,
        back_populates="movement_patterns",
    )


class ExerciseCatalog(Base, TimeStampMixin):
    __tablename__ = "exercise_catalog"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    is_custom = Column(Boolean, default=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    category_id = Column(
        UUID(as_uuid=True), ForeignKey("exercise_categories.id"), nullable=False
    )
    video_url = Column(String, nullable=True)
    image_urls = Column(ARRAY(String), nullable=True)
    mechanics = Column(
        Enum("compound", "isolation", name="mechanics_enum"),
        nullable=False,
        default="compound",
    )
    unilateral = Column(Boolean, default=False)
    default_tempo = Column(String, nullable=True)  # e.g., "3-1-1-0"
    is_bodyweight = Column(Boolean, default=False)
    supports_gps = Column(Boolean, default=False)
    supports_pool = Column(Boolean, default=False)
    supports_hr = Column(Boolean, default=True)
    cadence_metric = Column(
        String, nullable=True
    )  # e.g., "steps/min", "strokes/min", "rpm"
    notes = Column(ARRAY(Text), nullable=True)  # Notes can be an array of strings
    default_sport_profile = Column(
        String, nullable=True
    )  # e.g., "outdoor_run", "pool_swim"

    # Relationships
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
    created_by = relationship("User", backref="created_exercises")
