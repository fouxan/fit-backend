# app/models/exercise_biomech_variations.py
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.mixins import TimeStampMixin


class ExerciseBiomechanics(Base, TimeStampMixin):
    __tablename__ = "exercise_biomechanics"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exercise_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exercise_catalog.id", ondelete="CASCADE"),
        nullable=False,
    )

    primary_muscles = Column(JSONB)
    secondary_muscles = Column(JSONB)
    stabilizer_muscles = Column(JSONB)
    joints_involved = Column(ARRAY(String))
    movement_plane = Column(String(20))
    optimal_rom_degrees = Column(Integer)
    joint_angles = Column(JSONB)
    force_curve_type = Column(String(20))
    recommended_eccentric_seconds = Column(Numeric(3, 1))
    recommended_pause_seconds = Column(Numeric(3, 1))
    recommended_concentric_seconds = Column(Numeric(3, 1))


class ExerciseVariation(Base):
    __tablename__ = "exercise_variations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_exercise_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exercise_catalog.id", ondelete="CASCADE"),
        nullable=False,
    )
    variation_exercise_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exercise_catalog.id", ondelete="CASCADE"),
        nullable=False,
    )
    variation_type = Column(String(20))  # progression/regression/lateral
    difficulty_modifier = Column(Numeric(3, 2))
    variation_factors = Column(JSONB)
