# app/models/execution.py
import uuid
from sqlalchemy import Column, Integer, String, Time, DateTime, Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.mixins import TimeStampMixin
from app.models.enums import SetType, RPEScale, ROMQuality


class SessionContext(Base, TimeStampMixin):
    __tablename__ = "session_context"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workout_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    gym_location = Column(String(100))
    equipment_availability = Column(JSONB)
    crowd_level = Column(Integer)
    temperature_celsius = Column(Integer)
    sleep_hours = Column(
        Text
    )  # Numeric(3,1) – can swap to Decimal w/ SQLAlchemy Numeric if preferred
    sleep_quality = Column(Integer)
    stress_level = Column(Integer)
    energy_level = Column(Integer)
    nutrition_timing = Column(String(20))
    caffeine_mg = Column(Integer)
    other_supplements = Column(
        JSONB
    )  # ARRAY(Text) works too; JSONB is often easier in Python
    time_of_day = Column(Time)
    days_since_last_workout = Column(Integer)


class ExercisePerformance(Base, TimeStampMixin):
    __tablename__ = "exercise_performances"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workout_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    workout_block_exercise_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workout_block_exercises.id", ondelete="CASCADE"),
        nullable=False,
    )
    performance_order = Column(Integer, nullable=False)

    planned_sets = Column(Integer)
    completed_sets = Column(Integer)
    total_volume_kg = Column(Text)  # Numeric(8,2)
    total_reps = Column(Integer)
    average_rpe = Column(Text)  # Numeric(3,1)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    total_rest_seconds = Column(Integer)
    performance_notes = Column(Text)
    technique_quality = Column(Integer)


class SetExecution(Base, TimeStampMixin):
    __tablename__ = "set_executions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exercise_performance_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exercise_performances.id", ondelete="CASCADE"),
        nullable=False,
    )
    set_protocol_id = Column(UUID(as_uuid=True), ForeignKey("set_protocols.id"))
    set_number = Column(Integer, nullable=False)
    set_type = Column(
        Enum(SetType, name="set_type_enum"), nullable=False, server_default="working"
    )

    weight_kg = Column(Text)  # Numeric(6,2)
    reps_completed = Column(Integer)
    reps_attempted = Column(Integer)
    rpe_value = Column(Text)  # Numeric(3,1)
    rpe_scale = Column(
        Enum(RPEScale, name="rpe_scale_enum"), nullable=False, server_default="rpe_10"
    )
    rom_quality = Column(
        Enum(ROMQuality, name="rom_quality_enum"), nullable=False, server_default="full"
    )

    eccentric_seconds = Column(Text)  # Numeric(4,2)
    pause_seconds = Column(Text)
    concentric_seconds = Column(Text)
    partial_reps = Column(Integer, nullable=False, default=0)
    assisted_reps = Column(Integer, nullable=False, default=0)
    range_of_motion_degrees = Column(Integer)
    rest_before_seconds = Column(Integer)
    rest_after_seconds = Column(Integer)
    equipment_modifications = Column(JSONB)
    technique_breakdown_rep = Column(Integer)
    pain_level = Column(Integer)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    set_notes = Column(Text)
