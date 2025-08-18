from datetime import datetime
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.core.security import create_access_token, create_refresh_token
from app.core.exceptions import InvalidCredentialsException, UnauthorizedException
from app.schemas.auth import Token
from app.services.user import UserService


class AuthService:
    @staticmethod
    def login(db: Session, username: str, password: str) -> Token:
        """Authenticate user and return tokens"""
        user = UserService.authenticate_user(db, username, password)
        if not user:
            raise InvalidCredentialsException()

        if not user.is_active:
            raise UnauthorizedException("User account is inactive")

        access_token = create_access_token(subject=user.username)
        refresh_token = create_refresh_token(subject=user.username)

        return Token(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def refresh_token(db: Session, refresh_token: str) -> Token:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            token_type: str = payload.get("type")

            if username is None or token_type != "refresh":
                raise UnauthorizedException("Invalid refresh token")

        except JWTError:
            raise UnauthorizedException("Invalid refresh token")

        user = UserService.get_user_by_username(db, username)
        if not user:
            raise UnauthorizedException("User not found")

        if not user.is_active:
            raise UnauthorizedException("User account is inactive")

        access_token = create_access_token(subject=user.username)
        new_refresh_token = create_refresh_token(subject=user.username)

        return Token(access_token=access_token, refresh_token=new_refresh_token)

    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """Verify JWT token and return username"""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            token_type: str = payload.get("type")

            if username is None or token_type != "access":
                return None

            return username
        except JWTError:
            return None
