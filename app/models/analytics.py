# app/models/analytics.py
import uuid
from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base
from app.models.mixins import TimeStampMixin


class VolumeAnalytics(Base, TimeStampMixin):
    __tablename__ = "volume_analytics"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    calculation_date = Column(Date, nullable=False)
    period_type = Column(String(10), nullable=False)  # daily/weekly/monthly
    total_volume_kg = Column(String)  # Numeric(10,2)
    total_sets = Column(Integer)
    total_reps = Column(Integer)
    average_intensity = Column(String)  # Numeric(5,2)
    volume_by_muscle_group = Column(JSONB)
    volume_by_movement = Column(JSONB)
    volume_per_hour = Column(String)  # Numeric(8,2)
    sets_per_hour = Column(String)  # Numeric(6,2)


class StrengthProgression(Base, TimeStampMixin):
    __tablename__ = "strength_progressions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exercise_catalog.id", ondelete="CASCADE"),
        nullable=False,
    )
    measurement_date = Column(Date, nullable=False)
    estimated_1rm_kg = Column(String)  # Numeric(6,2)
    estimation_method = Column(String(20))
    confidence_score = Column(String)  # Numeric(3,2)
    base_weight_kg = Column(String)  # Numeric(6,2)
    base_reps = Column(Integer)
    base_rpe = Column(String)  # Numeric(3,1)
    volume_pr = Column(Boolean, default=False, nullable=False)
    weight_pr = Column(Boolean, default=False, nullable=False)
    reps_pr = Column(Boolean, default=False, nullable=False)


class InsightDataPoint(Base, TimeStampMixin):
    __tablename__ = "insight_data_points"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    data_type = Column(String(50), nullable=False)
    measurement_date = Column(Date, nullable=False)
    numeric_value = Column(String)  # Numeric(10,4)
    text_value = Column(String)
    json_value = Column(JSONB)
    source_table = Column(String(50))
    source_id = Column(UUID(as_uuid=True))
    confidence_score = Column(String)  # Numeric(3,2)
    calculation_method = Column(String(50))


class UserInsight(Base, TimeStampMixin):
    __tablename__ = "user_insights"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    insight_type = Column(String(50), nullable=False)
    insight_category = Column(String(30))
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=False)
    confidence_score = Column(String, nullable=False)  # Numeric(3,2)
    recommendations = Column(JSONB)
    supporting_data_ids = Column(
        JSONB
    )  # ARRAY(UUID) – JSONB is easy in Python; switch to ARRAY(UUID) if needed
    chart_data = Column(JSONB)
    is_read = Column(Boolean, default=False, nullable=False)
    is_dismissed = Column(Boolean, default=False, nullable=False)
    user_feedback = Column(Integer)
    valid_until = Column(Date)


class FeatureUsage(Base, TimeStampMixin):
    __tablename__ = "feature_usage"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    feature_name = Column(String(50), nullable=False)
    usage_date = Column(Date, nullable=False)
    usage_count = Column(Integer, nullable=False, default=1)
    daily_limit = Column(Integer)
    monthly_limit = Column(Integer)
