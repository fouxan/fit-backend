# app/schemas/execution.py
from typing import Optional, Dict, Any
from pydantic import UUID4
from datetime import datetime, time
from .common import ORMModel
from .enums import SetType, RPEScale, ROMQuality


class SessionContextBase(ORMModel):
    workout_session_id: UUID4
    gym_location: Optional[str] = None
    equipment_availability: Optional[Dict[str, Any]] = None
    crowd_level: Optional[int] = None
    temperature_celsius: Optional[int] = None
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[int] = None
    stress_level: Optional[int] = None
    energy_level: Optional[int] = None
    nutrition_timing: Optional[str] = None
    caffeine_mg: Optional[int] = None
    other_supplements: Optional[Dict[str, Any]] = None
    time_of_day: Optional[time] = None
    days_since_last_workout: Optional[int] = None


class SessionContextCreate(SessionContextBase):
    pass


class SessionContextRead(SessionContextBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime


class ExercisePerformanceBase(ORMModel):
    workout_session_id: UUID4
    workout_block_exercise_id: UUID4
    performance_order: int
    planned_sets: Optional[int] = None
    completed_sets: Optional[int] = None
    total_volume_kg: Optional[float] = None
    total_reps: Optional[int] = None
    average_rpe: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_rest_seconds: Optional[int] = None
    performance_notes: Optional[str] = None
    technique_quality: Optional[int] = None


class ExercisePerformanceCreate(ExercisePerformanceBase):
    pass


class ExercisePerformanceRead(ExercisePerformanceBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime


class SetExecutionBase(ORMModel):
    exercise_performance_id: UUID4
    set_protocol_id: Optional[UUID4] = None
    set_number: int
    set_type: SetType = SetType.working
    weight_kg: Optional[float] = None
    reps_completed: Optional[int] = None
    reps_attempted: Optional[int] = None
    rpe_value: Optional[float] = None
    rpe_scale: RPEScale = RPEScale.rpe_10
    rom_quality: ROMQuality = ROMQuality.full
    eccentric_seconds: Optional[float] = None
    pause_seconds: Optional[float] = None
    concentric_seconds: Optional[float] = None
    partial_reps: int = 0
    assisted_reps: int = 0
    range_of_motion_degrees: Optional[int] = None
    rest_before_seconds: Optional[int] = None
    rest_after_seconds: Optional[int] = None
    equipment_modifications: Optional[Dict[str, Any]] = None
    technique_breakdown_rep: Optional[int] = None
