from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import UserAlreadyExistsException, UserNotFoundException


class UserService:
    @staticmethod
    def get_user(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_username_or_email(db: Session, username: str) -> Optional[User]:
        """Get user by username or email"""
        return db.query(User).filter(
            or_(User.username == username, User.email == username)
        ).first()
    
    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """Create new user"""
        # Check if user already exists
        existing_user = UserService.get_user_by_email(db, user_create.email)
        if existing_user:
            raise UserAlreadyExistsException("Email already registered")
        
        existing_user = UserService.get_user_by_username(db, user_create.username)
        if existing_user:
            raise UserAlreadyExistsException("Username already taken")
        
        # Create new user
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=get_password_hash(user_create.password),
            full_name=user_create.full_name,
            height=user_create.height,
            weight=user_create.weight,
            date_of_birth=user_create.date_of_birth,
            fitness_goal=user_create.fitness_goal
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: str, user_update: UserUpdate) -> User:
        """Update user"""
        db_user = UserService.get_user(db, user_id)
        if not db_user:
            raise UserNotFoundException()
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Hash password if it's being updated
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        # Check email uniqueness if being updated
        if "email" in update_data and update_data["email"] != db_user.email:
            existing_user = UserService.get_user_by_email(db, update_data["email"])
            if existing_user:
                raise UserAlreadyExistsException("Email already registered")
        
        # Check username uniqueness if being updated
        if "username" in update_data and update_data["username"] != db_user.username:
            existing_user = UserService.get_user_by_username(db, update_data["username"])
            if existing_user:
                raise UserAlreadyExistsException("Username already taken")
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = UserService.get_user_by_username_or_email(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
