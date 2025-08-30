from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import get_settings
from app.api.v1 import auth, users, workouts, exercises
import uvicorn

settings = get_settings()

# Create FastAPI instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers - temporarily disabled
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(workouts.router, prefix="/api/v1/workouts", tags=["Workouts"])
app.include_router(exercises.router, prefix="/api/v1/exercises", tags=["Exercises"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Fitness Tracker API!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=settings.LOGGING_CONFIG,
        log_level=settings.UVICORN_LOG_LEVEL,
    )

