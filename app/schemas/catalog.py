# app/schemas/catalog.py
from typing import Optional, List, Dict, Any
from pydantic import UUID4, HttpUrl
from datetime import datetime
from .common import ORMModel
from .enums import DifficultyLevel, Mechanics


class ExerciseCategoryBase(ORMModel):
    name: str
    description: Optional[str] = None


class ExerciseCategoryCreate(ExerciseCategoryBase):
    pass


class ExerciseCategoryRead(ExerciseCategoryBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime


class MuscleGroupBase(ORMModel):
    name: str
    description: Optional[str] = None


class MuscleGroupCreate(MuscleGroupBase):
    pass


class MuscleGroupRead(MuscleGroupBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime


class EquipmentBase(ORMModel):
    name: str
    description: Optional[str] = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentRead(EquipmentBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime


class MovementPatternBase(ORMModel):
    name: str
    description: Optional[str] = None


class MovementPatternCreate(MovementPatternBase):
    pass


class MovementPatternRead(MovementPatternBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime


class ExerciseBase(ORMModel):
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    difficulty: DifficultyLevel
    category_id: UUID4
    video_url: Optional[HttpUrl] = None
    image_urls: Optional[List[HttpUrl]] = None
    mechanics: Mechanics = Mechanics.compound
    unilateral: bool = False
    default_tempo: Optional[str] = None
    is_bodyweight: bool = False
    supports_gps: bool = False
    supports_pool: bool = False
    supports_hr: bool = True
    cadence_metric: Optional[str] = None
    notes: Optional[List[str]] = None
    default_sport_profile: Optional[str] = None


class ExerciseCreate(ExerciseBase):
    muscle_group_ids: List[UUID4]
    equipment_ids: List[UUID4]
    movement_pattern_ids: Optional[List[UUID4]] = None


class ExerciseUpdate(ORMModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    category_id: Optional[UUID4] = None
    video_url: Optional[HttpUrl] = None
    image_urls: Optional[List[HttpUrl]] = None
    mechanics: Optional[Mechanics] = None
    unilateral: Optional[bool] = None
    default_tempo: Optional[str] = None
    is_bodyweight: Optional[bool] = None
    supports_gps: Optional[bool] = None
    supports_pool: Optional[bool] = None
    supports_hr: Optional[bool] = None
    cadence_metric: Optional[str] = None
    notes: Optional[List[str]] = None
    default_sport_profile: Optional[str] = None
    muscle_group_ids: Optional[List[UUID4]] = None
    equipment_ids: Optional[List[UUID4]] = None
    movement_pattern_ids: Optional[List[UUID4]] = None


class ExerciseRead(ExerciseBase):
    id: UUID4
    is_custom: bool
    created_by_id: Optional[UUID4] = None
    created_at: datetime
    updated_at: datetime
    category: ExerciseCategoryRead
    muscle_groups: List[MuscleGroupRead]
    equipment: List[EquipmentRead]
    # movement patterns optional to include in responses:
    # movement_patterns: List[MovementPatternRead] = []
