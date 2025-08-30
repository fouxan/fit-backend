# # app/models/devices.py
# import uuid
# from sqlalchemy import Column, String, Boolean, ForeignKey
# from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
# from sqlalchemy.orm import relationship
# from app.db.base import Base
# from app.models.mixins import TimeStampMixin


# class DeviceConnections(Base, TimeStampMixin):
#     __tablename__ = "device_connections"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
#     provider = Column(String, nullable=False)
#     device_type = Column(String, nullable=False)
#     device_id = Column(String, nullable=False)
#     connected_at = Column(String, nullable=False)  # mirrors your model/migration
#     scopes = Column(ARRAY(String))
#     status = Column(String, nullable=False, default="active")
#     access_meta = Column(JSONB)
#     user = relationship("User", back_populates="device_connections")
