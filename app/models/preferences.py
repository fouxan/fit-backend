# # app/models/preferences.py
# import uuid
# from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import relationship
# from app.db.base import Base
# from app.models.mixins import TimeStampMixin


# class UserPreferences(Base, TimeStampMixin):
#     __tablename__ = "user_preferences"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(
#         UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
#     )

#     preferred_units = Column(String(10), nullable=False, default="metric")
#     default_rest_seconds = Column(Integer, nullable=False, default=120)
#     track_rpe = Column(Boolean, nullable=False, default=True)
#     track_rom = Column(Boolean, nullable=False, default=False)
#     track_tempo = Column(Boolean, nullable=False, default=False)

#     workout_reminders = Column(Boolean, nullable=False, default=True)
#     progress_updates = Column(Boolean, nullable=False, default=True)
#     insight_notifications = Column(Boolean, nullable=False, default=True)

#     share_workouts = Column(Boolean, nullable=False, default=False)
#     research_participation = Column(Boolean, nullable=False, default=False)

#     user = relationship("User", back_populates="preferences")
