from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.subscription import PLAN_FEATURES, PlanType
from app.models.user import User
from app.services.user import UserService

class PlanLimitService:
    @staticmethod
    def check_custom_exercise_permission(db: Session, user: User) -> bool:
        """Check if user can create custom exercises"""
        subscription = UserService.get_active_subscription(db, user.id)
        plan_type = PlanType.FREE if not subscription else subscription.plan.type
        return PLAN_FEATURES[plan_type]["custom_exercises"]

    @staticmethod
    def check_workout_limit(db: Session, user: User) -> None:
        """Check if user has reached their workout limit"""
        subscription = UserService.get_active_subscription(db, user.id)
        plan_type = PlanType.FREE if not subscription else subscription.plan.type
        max_workouts = PLAN_FEATURES[plan_type]["max_workouts"]
        
        if max_workouts != -1:  # -1 means unlimited
            current_workouts = db.query(Workout).filter(
                Workout.created_by_id == user.id,
                Workout.is_template == False
            ).count()
            
            if current_workouts >= max_workouts:
                raise HTTPException(
                    status_code=402,
                    detail=f"Workout limit reached. Upgrade your plan to create more workouts."
                )

    @staticmethod
    def check_plan_limit(db: Session, user: User) -> None:
        """Check if user has reached their workout plan limit"""
        subscription = UserService.get_active_subscription(db, user.id)
        plan_type = PlanType.FREE if not subscription else subscription.plan.type
        max_plans = PLAN_FEATURES[plan_type]["max_plans"]
        
        if max_plans != -1:  # -1 means unlimited
            current_plans = db.query(WorkoutPlan).filter(
                WorkoutPlan.created_by_id == user.id
            ).count()
            
            if current_plans >= max_plans:
                raise HTTPException(
                    status_code=402,
                    detail=f"Workout plan limit reached. Upgrade your plan to create more plans."
                )

    @staticmethod
    def can_access_analytics(db: Session, user: User) -> bool:
        """Check if user can access analytics"""
        subscription = UserService.get_active_subscription(db, user.id)
        plan_type = PlanType.FREE if not subscription else subscription.plan.type
        return PLAN_FEATURES[plan_type]["analytics"]

    @staticmethod
    def can_export_data(db: Session, user: User) -> bool:
        """Check if user can export their data"""
        subscription = UserService.get_active_subscription(db, user.id)
        plan_type = PlanType.FREE if not subscription else subscription.plan.type
        return PLAN_FEATURES[plan_type]["export_data"]
