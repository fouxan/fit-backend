# app/schemas/preferences.py
from pydantic import UUID4
from typing import Optional
from .common import ORMModel


class UserPreferencesBase(ORMModel):
    preferred_units: str = "metric"
    default_rest_seconds: int = 120
    track_rpe: bool = True
    track_rom: bool = False
    track_tempo: bool = False
    workout_reminders: bool = True
    progress_updates: bool = True
    insight_notifications: bool = True
    share_workouts: bool = False
    research_participation: bool = False


class UserPreferencesCreate(UserPreferencesBase):
    user_id: UUID4


class UserPreferencesUpdate(ORMModel):
    preferred_units: Optional[str] = None
    default_rest_seconds: Optional[int] = None
    track_rpe: Optional[bool] = None
    track_rom: Optional[bool] = None
    track_tempo: Optional[bool] = None
    workout_reminders: Optional[bool] = None
    progress_updates: Optional[bool] = None
    insight_notifications: Optional[bool] = None
    share_workouts: Optional[bool] = None
    research_participation: Optional[bool] = None


class UserPreferencesRead(UserPreferencesBase):
    id: UUID4
    user_id: UUID4
