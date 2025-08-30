from typing import List, Optional
from pydantic import BaseModel, UUID4, HttpUrl
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ExerciseCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class ExerciseCategoryCreate(ExerciseCategoryBase):
    pass

class ExerciseCategory(ExerciseCategoryBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MuscleGroupBase(BaseModel):
    name: str
    description: Optional[str] = None

class MuscleGroupCreate(MuscleGroupBase):
    pass

class MuscleGroup(MuscleGroupBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EquipmentBase(BaseModel):
    name: str
    description: Optional[str] = None

class EquipmentCreate(EquipmentBase):
    pass

class Equipment(EquipmentBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    difficulty: DifficultyLevel
    category_id: UUID4
    video_url: Optional[HttpUrl] = None
    image_urls: Optional[List[HttpUrl]] = None

class ExerciseCreate(ExerciseBase):
    muscle_group_ids: List[UUID4]
    equipment_ids: List[UUID4]

class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    category_id: Optional[UUID4] = None
    video_url: Optional[HttpUrl] = None
    image_urls: Optional[List[HttpUrl]] = None
    muscle_group_ids: Optional[List[UUID4]] = None
    equipment_ids: Optional[List[UUID4]] = None

class Exercise(ExerciseBase):
    id: UUID4
    is_custom: bool
    created_by_id: Optional[UUID4]
    created_at: datetime
    updated_at: datetime
    category: ExerciseCategory
    muscle_groups: List[MuscleGroup]
    equipment: List[Equipment]

    class Config:
        from_attributes = True
