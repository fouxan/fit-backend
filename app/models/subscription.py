# # app/models/subscription.py
# import uuid
# from datetime import datetime
# from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
# from sqlalchemy.dialects.postgresql import UUID, JSONB
# from sqlalchemy.orm import relationship
# from app.db.base import Base


# class Plan(Base):
#     __tablename__ = "plans"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     name = Column(String, nullable=False)
#     type = Column(String, nullable=False)
#     description = Column(String)
#     price = Column(Integer, nullable=False)  # cents
#     stripe_price_id = Column(String)
#     features = Column(JSONB, nullable=False)
#     created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
#     updated_at = Column(
#         DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
#     )
#     subscriptions = relationship("Subscription", back_populates="plan")


# class Subscription(Base):
#     __tablename__ = "subscriptions"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
#     plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
#     stripe_subscription_id = Column(String)
#     stripe_customer_id = Column(String)
#     is_active = Column(Boolean, default=True, nullable=False)
#     current_period_start = Column(DateTime(timezone=True))
#     current_period_end = Column(DateTime(timezone=True))
#     cancel_at_period_end = Column(Boolean, default=False, nullable=False)
#     created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
#     updated_at = Column(
#         DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
#     )
#     user = relationship("User", back_populates="subscriptions")
#     plan = relationship("Plan", back_populates="subscriptions")
