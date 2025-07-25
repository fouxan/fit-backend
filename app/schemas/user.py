from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, UUID4
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    date_of_birth: Optional[str] = None
    fitness_goal: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    date_of_birth: Optional[str] = None
    fitness_goal: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: UUID4
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    hashed_password: str
