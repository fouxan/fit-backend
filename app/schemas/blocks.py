# app/schemas/blocks.py
from typing import Optional, Dict, Any
from pydantic import UUID4
from datetime import datetime
from .common import ORMModel
from .enums import WorkoutBlockType, SetType


class WorkoutBlockBase(ORMModel):
    workout_id: UUID4
    block_order: int
    block_name: Optional[str] = None
    block_type: WorkoutBlockType = WorkoutBlockType.straight_sets
    rest_between_exercises: Optional[int] = None
    rounds: int = 1
    round_rest_seconds: Optional[int] = None
    notes: Optional[str] = None


class WorkoutBlockCreate(WorkoutBlockBase):
    pass


class WorkoutBlockRead(WorkoutBlockBase):
    id: UUID4
    created_at: datetime


class WorkoutBlockExerciseBase(ORMModel):
    workout_block_id: UUID4
    exercise_id: UUID4
    exercise_order: int
    target_sets: Optional[int] = None
    target_reps_min: Optional[int] = None
    target_reps_max: Optional[int] = None
    target_weight_kg: Optional[float] = None
    target_rpe: Optional[float] = None
    rest_after_seconds: Optional[int] = None
    tempo_prescription: Optional[str] = None
    equipment_variant: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class WorkoutBlockExerciseCreate(WorkoutBlockExerciseBase):
    pass


class WorkoutBlockExerciseRead(WorkoutBlockExerciseBase):
    id: UUID4


class SetProtocolBase(ORMModel):
    workout_block_exercise_id: UUID4
    protocol_type: SetType
    set_order: int
    protocol_data: Optional[Dict[str, Any]] = None


class SetProtocolCreate(SetProtocolBase):
    pass


class SetProtocolRead(SetProtocolBase):
    id: UUID4
    created_at: datetime
