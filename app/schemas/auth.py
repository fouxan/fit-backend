# app/schemas/auth.py
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str  # username or email
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str
