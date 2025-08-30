from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import Token, LoginRequest, RefreshTokenRequest
from app.schemas.user import UserCreate, UserRead
from app.services.auth import AuthService
from app.services.user import UserService
# from app.services.subscription import SubscriptionService
# from utils.logger import logger

router = APIRouter()

# subscription_service = SubscriptionService()


@router.post("/register", response_model=UserRead)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user and set up their subscription
    """
    # Create the user
    user = UserService.create_user(db, user_create)
    
    # try:
    #     # Set up their subscription
    #     await subscription_service.create_initial_subscription(
    #         db=db,
    #         user=user,
    #         plan_type=user_create.selected_plan,
    #         payment_method_id=user_create.payment_method_id
    #     )
    # except Exception as e:
    #     # If subscription setup fails, the user is still created with free plan
    #     logger.error(f"Error setting up subscription for user {user.id}: {str(e)}")
    
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    token = AuthService.login(db, form_data.username, form_data.password)
    return token


@router.post("/login-json", response_model=Token)
async def login_json(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Alternative JSON login endpoint
    """
    token = AuthService.login(db, login_data.username, login_data.password)
    return token


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    token = AuthService.refresh_token(db, refresh_data.refresh_token)
    return token
