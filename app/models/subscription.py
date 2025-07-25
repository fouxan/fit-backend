from enum import Enum
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid
from datetime import datetime


class PlanType(str, Enum):
    FREE = "free"
    PLUS = "plus"
    PRO = "pro"


class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    description = Column(String)
    price = Column(Integer, nullable=False)  # Price in cents
    stripe_price_id = Column(String)
    features = Column(JSON, nullable=False)  # Store features and limits as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
    stripe_subscription_id = Column(String)
    stripe_customer_id = Column(String)
    is_active = Column(Boolean, default=True)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")


# Plan feature limits for different tiers
PLAN_FEATURES = {
    PlanType.FREE: {
        "api_rate_limit": 100,  # requests per hour
        "max_workouts": 10,     # max saved workouts
        "max_plans": 1,         # max training plans
        "analytics": False,     # access to analytics
        "custom_exercises": False,  # ability to create custom exercises
        "export_data": False,   # ability to export workout data
        "priority_support": False,
    },
    PlanType.PLUS: {
        "api_rate_limit": 1000,
        "max_workouts": 50,
        "max_plans": 5,
        "analytics": True,
        "custom_exercises": True,
        "export_data": True,
        "priority_support": False,
    },
    PlanType.PRO: {
        "api_rate_limit": 5000,
        "max_workouts": -1,     # unlimited
        "max_plans": -1,        # unlimited
        "analytics": True,
        "custom_exercises": True,
        "export_data": True,
        "priority_support": True,
    }
}
