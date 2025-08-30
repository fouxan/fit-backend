from __future__ import annotations
from typing import Optional, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func
from sqlalchemy.exc import IntegrityError, NoResultFound
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import UserAlreadyExistsException, UserNotFoundException
import logging
logger = logging.getLogger(__name__)

def _norm_email(email: str) -> str:
    return email.strip().lower()

def _norm_username(u: str) -> str:
    return u.strip()

class UserService:
    @staticmethod
    def get_user(db: Session, user_id: str) -> Optional[User]:
        """Get user by primary key (fast path)."""
        return db.get(User, user_id)

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        email = _norm_email(email)
        stmt = select(User).where(func.lower(User.email) == email)
        return db.execute(stmt).scalars().first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        username = _norm_username(username)
        stmt = select(User).where(User.username == username)
        return db.execute(stmt).scalars().first()

    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """Create new user with DB-level uniqueness handling."""
        email = _norm_email(user_create.email)
        username = _norm_username(user_create.username)

        db_user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(user_create.password),
            full_name=user_create.full_name,
            height=user_create.height,
            weight=user_create.weight,
            date_of_birth=user_create.date_of_birth,
            fitness_goal=user_create.fitness_goal,
        )
        db.add(db_user)
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            if "email" in str(e).lower():
                raise UserAlreadyExistsException("Email already registered")
            if "username" in str(e).lower():
                raise UserAlreadyExistsException("Username already taken")
            raise
        db.refresh(db_user)
        return db_user

    # ---------- UPDATE ----------
    @staticmethod
    def update_user(db: Session, user_id: str, user_update: UserUpdate) -> User:
        """Update user fields safely. Rejects changing protected fields."""
        db_user = UserService.get_user(db, user_id)
        if not db_user:
            raise UserNotFoundException()

        update_data = user_update.model_dump(exclude_unset=True)

        protected = {"id", "hashed_password", "is_superuser", "is_staff"}
        for p in list(update_data.keys()):
            if p in protected:
                update_data.pop(p)

        if "email" in update_data and update_data["email"]:
            update_data["email"] = _norm_email(update_data["email"])
        if "username" in update_data and update_data["username"]:
            update_data["username"] = _norm_username(update_data["username"])

        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(db_user, field, value)

        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            if "email" in str(e).lower():
                raise UserAlreadyExistsException("Email already registered")
            if "username" in str(e).lower():
                raise UserAlreadyExistsException("Username already taken")
            raise

        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate by username, verify password, and (optionally) activity flag."""
        user = UserService.get_user_by_username(db, username)
        logger.debug(f"Authenticating user: {username}")
        
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        # if not user.is_active:
        #     return None
        return user

    @staticmethod
    def change_password(db: Session, user_id: str, new_password: str) -> None:
        user = UserService.get_user(db, user_id)
        if not user:
            raise UserNotFoundException()
        user.hashed_password = get_password_hash(new_password)
        db.commit()

    @staticmethod
    def set_email_verified(db: Session, user_id: str, verified: bool = True) -> None:
        user = UserService.get_user(db, user_id)
        if not user:
            raise UserNotFoundException()
        if hasattr(user, "email_verified"):
            user.email_verified = verified
            db.commit()

    @staticmethod
    def deactivate_user(db: Session, user_id: str) -> None:
        user = UserService.get_user(db, user_id)
        if not user:
            raise UserNotFoundException()
        if hasattr(user, "is_active"):
            user.is_active = False
            db.commit()

    @staticmethod
    def reactivate_user(db: Session, user_id: str) -> None:
        user = UserService.get_user(db, user_id)
        if not user:
            raise UserNotFoundException()
        if hasattr(user, "is_active"):
            user.is_active = True
            db.commit()

    @staticmethod
    def list_users(
        db: Session,
        *,
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None,
    ) -> Sequence[User]:
        stmt = select(User)
        if search:
            s = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(User.email).like(s),
                    func.lower(User.username).like(s),
                    func.lower(User.full_name).like(s),
                )
            )
        stmt = stmt.order_by(User.created_at.desc()).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def exists_by_email(db: Session, email: str) -> bool:
        stmt = select(1).where(func.lower(User.email) == _norm_email(email)).limit(1)
        return db.execute(stmt).first() is not None

    @staticmethod
    def exists_by_username(db: Session, username: str) -> bool:
        stmt = select(1).where(User.username == _norm_username(username)).limit(1)
        return db.execute(stmt).first() is not None
