# app/schemas/analytics.py
from typing import Optional, Dict, Any, List
from pydantic import UUID4
from datetime import datetime, date
from .common import ORMModel


class VolumeAnalyticsRead(ORMModel):
    id: UUID4
    user_id: UUID4
    calculation_date: date
    period_type: str  # daily/weekly/monthly
    total_volume_kg: Optional[float] = None
    total_sets: Optional[int] = None
    total_reps: Optional[int] = None
    average_intensity: Optional[float] = None
    volume_by_muscle_group: Optional[Dict[str, float]] = None
    volume_by_movement: Optional[Dict[str, float]] = None
    volume_per_hour: Optional[float] = None
    sets_per_hour: Optional[float] = None
    created_at: datetime


class StrengthProgressionRead(ORMModel):
    id: UUID4
    user_id: UUID4
    exercise_id: UUID4
    measurement_date: date
    estimated_1rm_kg: Optional[float] = None
    estimation_method: Optional[str] = None
    confidence_score: Optional[float] = None
    base_weight_kg: Optional[float] = None
    base_reps: Optional[int] = None
    base_rpe: Optional[float] = None
    volume_pr: bool = False
    weight_pr: bool = False
    reps_pr: bool = False
    created_at: datetime


class InsightDataPointRead(ORMModel):
    id: UUID4
    user_id: UUID4
    data_type: str
    measurement_date: date
    numeric_value: Optional[float] = None
    text_value: Optional[str] = None
    json_value: Optional[Dict[str, Any]] = None
    source_table: Optional[str] = None
    source_id: Optional[UUID4] = None
    confidence_score: Optional[float] = None
    calculation_method: Optional[str] = None
    created_at: datetime


class UserInsightRead(ORMModel):
    id: UUID4
    user_id: UUID4
    insight_type: str
    insight_category: Optional[str] = None
    title: str
    description: str
    confidence_score: float
    recommendations: Optional[Dict[str, Any]] = None
    supporting_data_ids: Optional[List[UUID4]] = None
    chart_data: Optional[Dict[str, Any]] = None
    is_read: bool
    is_dismissed: bool
    user_feedback: Optional[int] = None
    valid_until: Optional[date] = None
    created_at: datetime


class FeatureUsageRead(ORMModel):
    id: UUID4
    user_id: UUID4
    feature_name: str
    usage_date: date
    usage_count: int
    daily_limit: Optional[int] = None
    monthly_limit: Optional[int] = None
    created_at: datetime
