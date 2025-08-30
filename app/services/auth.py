from datetime import datetime, timedelta

from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config.settings import get_settings
from app.core.security import create_access_token, create_refresh_token
from app.core.exceptions import InvalidCredentialsException, UnauthorizedException
from app.schemas.auth import Token
from app.services.user import UserService
from app.services.email import EmailService
import logging
logger = logging.getLogger(__name__)

settings = get_settings()
email_service = EmailService()


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

    @staticmethod
    async def initiate_password_reset(db: Session, email: str):
        """Initiate password reset process"""
        user = UserService.get_user_by_email(db, email)
        if not user:
            raise UnauthorizedException("User not found")

        reset_token = create_access_token(subject=user.username, expires_delta=timedelta(hours=1))
        await email_service.send_password_reset(user.email, reset_token)


        return {"msg": "Password reset initiated"}
    
    def reset_password(db: Session, token: str, new_password: str):
        """Reset user password using the provided token"""
        try:
            logger.info(f"Resetting password for user {token} with payload:")
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            
            

            if username is None:
                raise UnauthorizedException("Invalid token")

        except JWTError:
            raise UnauthorizedException("Invalid token")

        user = UserService.get_user_by_username(db, username)
        if not user:
            raise UnauthorizedException("User not found")

        UserService.change_password(db, user.id, new_password)
        return {"msg": "Password reset successful"}