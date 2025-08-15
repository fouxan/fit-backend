from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.base import TimeStampMixin
import uuid


class User(Base, TimeStampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    tz = Column(String, nullable=True)
    units = Column(String, nullable=True)
    locale = Column(String, nullable=True)

    # Subscriptions
    subscriptions = relationship("Subscription", back_populates="user")

    # Fitness-related fields for future use
    height = Column(Integer, nullable=True)  # in cm
    weight = Column(Integer, nullable=True)  # in kg
    date_of_birth = Column(String, nullable=True)  # Store as string for now
    fitness_goal = Column(String, nullable=True)

    device_connections = relationship(
        "DeviceConnections",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class DeviceConnections(Base, TimeStampMixin):
    __tablename__ = "device_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # e.g., "Fitbit", "Garmin"
    device_type = Column(
        String, nullable=False
    )  # e.g., "smartwatch", "fitness_tracker"
    device_id = Column(String, nullable=False)  # Unique identifier for the device
    connected_at = Column(String, nullable=False)  # Store as string for now
    scopes = Column(ARRAY(String), nullable=True)
    status = Column(String, nullable=False, default="active")
    access_meta = Column(JSONB, nullable=True)

    # Relationships
    user = relationship("User", back_populates="device_connections")
