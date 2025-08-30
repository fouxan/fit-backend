# app/models/protocols.py
import uuid
from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base
from app.models.mixins import TimeStampMixin
from app.models.enums import SetType


class SetProtocol(Base, TimeStampMixin):
    __tablename__ = "set_protocols"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_block_exercise_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workout_block_exercises.id", ondelete="CASCADE"),
        nullable=False,
    )
    protocol_type = Column(Enum(SetType, name="set_type_enum"), nullable=False)
    set_order = Column(Integer, nullable=False)
    protocol_data = Column(JSONB)
