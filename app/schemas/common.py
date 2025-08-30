# app/schemas/common.py
from pydantic import BaseModel, ConfigDict, UUID4, EmailStr, HttpUrl
from typing import Any, Dict, List, Optional
from datetime import datetime, date, time


class ORMModel(BaseModel):
    # Pydantic v2 ORM mode
    model_config = ConfigDict(from_attributes=True)
