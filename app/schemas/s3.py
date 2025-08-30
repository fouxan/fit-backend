# app/schemas/files.py
from pydantic import BaseModel


class PresignedURL(BaseModel):
    url: str
    method: str
    key: str
    expires_in: int
