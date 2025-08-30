# app/models/user.py
import uuid
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.mixins import TimeStampMixin


class User(Base, TimeStampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    tz = Column(String)
    units = Column(String)
    locale = Column(String)

    # fitness profile
    height = Column(Integer)  # cm
    weight = Column(Integer)  # kg
    date_of_birth = Column(String)
    fitness_goal = Column(String)

    # NEW per Phase 1
    training_experience = Column(String(20))
    primary_goals = Column(
        ARRAY(String)
    )  # TEXT[] in DB is compatible with ARRAY(String)
    injury_history = Column(JSONB)
    training_frequency = Column(Integer)

    # relationships
    # subscriptions = relationship("Subscription", back_populates="user")
    # device_connections = relationship(
    #     "DeviceConnections", back_populates="user", cascade="all, delete-orphan"
    # )
    # preferences = relationship(
    #     "UserPreferences",
    #     back_populates="user",
    #     uselist=False,
    #     cascade="all, delete-orphan",
    # )
