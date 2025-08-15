from fastapi import APIRouter
from app.api.v1 import auth, users, exercises, workouts, webhooks

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(exercises.router, prefix="/fitness", tags=["exercises"])
api_router.include_router(workouts.router, prefix="/fitness", tags=["workouts"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
