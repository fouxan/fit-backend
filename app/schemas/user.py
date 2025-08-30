# app/schemas/user.py
from typing import Optional, List, Dict, Any
from pydantic import EmailStr, UUID4, ConfigDict, BaseModel
from datetime import datetime
from .common import ORMModel


class UserBase(ORMModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    date_of_birth: Optional[str] = None
    fitness_goal: Optional[str] = None

    # new profile fields
    training_experience: Optional[str] = None
    primary_goals: Optional[List[str]] = None
    injury_history: Optional[Dict[str, Any]] = None
    training_frequency: Optional[int] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(ORMModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    date_of_birth: Optional[str] = None
    fitness_goal: Optional[str] = None
    password: Optional[str] = None
    training_experience: Optional[str] = None
    primary_goals: Optional[List[str]] = None
    injury_history: Optional[Dict[str, Any]] = None
    training_frequency: Optional[int] = None


class UserRead(UserBase):
    id: UUID4
    username: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
