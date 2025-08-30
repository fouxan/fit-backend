from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.workout import (
    Workout, WorkoutExercise, WorkoutSession, 
    WorkoutPlan, WorkoutPlanWorkout, WorkoutStatus
)
from app.models.user import User
from app.schemas.workout import (
    WorkoutCreate, WorkoutExerciseCreate,
    WorkoutPlanCreate, WorkoutSessionCreate, WorkoutSessionUpdate
)
from app.services.exercise import ExerciseService

class WorkoutService:
    @staticmethod
    def create_workout(
        db: Session,
        workout: WorkoutCreate,
        user: User
    ) -> Workout:
        """Create a new workout"""
        # Check workout limit

        # Verify all exercises exist
        for exercise in workout.exercises:
            ExerciseService.get_exercise(db, exercise.exercise_id)

        try:
            db_workout = Workout(
                **workout.dict(exclude={'exercises'}),
                created_by_id=user.id
            )
            db.add(db_workout)
            db.flush()  # Get the workout ID without committing

            # Create workout exercises
            for idx, exercise in enumerate(workout.exercises):
                db_workout_exercise = WorkoutExercise(
                    **exercise.dict(),
                    workout_id=db_workout.id,
                    order=idx + 1
                )
                db.add(db_workout_exercise)

            db.commit()
            db.refresh(db_workout)
            return db_workout
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error creating workout")

    @staticmethod
    def get_workout(db: Session, workout_id: str, user: User) -> Workout:
        """Get workout by ID"""
        workout = db.query(Workout).filter(Workout.id == workout_id).first()
        if not workout:
            raise HTTPException(status_code=404, detail="Workout not found")
        
        # Check access permissions
        if not workout.is_public and workout.created_by_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this workout")
        
        return workout

    @staticmethod
    def list_workouts(
        db: Session,
        user: User,
        skip: int = 0,
        limit: int = 20,
        include_public: bool = True,
        difficulty: Optional[str] = None
    ) -> List[Workout]:
        """List workouts"""
        query = db.query(Workout)
        
        if include_public:
            query = query.filter(
                (Workout.created_by_id == user.id) | (Workout.is_public == True)
            )
        else:
            query = query.filter(Workout.created_by_id == user.id)
        
        if difficulty:
            query = query.filter(Workout.difficulty == difficulty)
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_workout_plan(
        db: Session,
        plan: WorkoutPlanCreate,
        user: User
    ) -> WorkoutPlan:
        """Create a new workout plan"""
        # Check plan limit

        # Verify all workouts exist and are accessible
        for workout_data in plan.workouts:
            WorkoutService.get_workout(db, workout_data.workout_id, user)

        try:
            db_plan = WorkoutPlan(
                **plan.dict(exclude={'workouts'}),
                created_by_id=user.id
            )
            db.add(db_plan)
            db.flush()

            # Create workout plan associations
            for workout_data in plan.workouts:
                db_plan_workout = WorkoutPlanWorkout(
                    workout_plan_id=db_plan.id,
                    **workout_data.dict()
                )
                db.add(db_plan_workout)

            db.commit()
            db.refresh(db_plan)
            return db_plan
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error creating workout plan")

    @staticmethod
    def start_workout_session(
        db: Session,
        session: WorkoutSessionCreate,
        user: User
    ) -> WorkoutSession:
        """Start a new workout session"""
        # Verify workout exists and is accessible
        workout = WorkoutService.get_workout(db, session.workout_id, user)

        # Check if there's already an active session
        active_session = db.query(WorkoutSession).filter(
            WorkoutSession.user_id == user.id,
            WorkoutSession.status == WorkoutStatus.IN_PROGRESS
        ).first()

        if active_session:
            raise HTTPException(
                status_code=400,
                detail="You already have an active workout session"
            )

        try:
            db_session = WorkoutSession(
                **session.dict(),
                user_id=user.id,
                status=WorkoutStatus.IN_PROGRESS,
                start_time=datetime.utcnow()
            )
            db.add(db_session)
            db.commit()
            db.refresh(db_session)
            return db_session
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error starting workout session")

    @staticmethod
    def complete_workout_session(
        db: Session,
        session_id: str,
        update_data: WorkoutSessionUpdate,
        user: User
    ) -> WorkoutSession:
        """Complete a workout session"""
        session = db.query(WorkoutSession).filter(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == user.id
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Workout session not found")

        if session.status != WorkoutStatus.IN_PROGRESS:
            raise HTTPException(status_code=400, detail="Workout session is not in progress")

        try:
            # Update session data
            session.end_time = datetime.utcnow()
            session.status = WorkoutStatus.COMPLETED
            session.total_duration = int((session.end_time - session.start_time).total_seconds())
            
            # Update optional fields
            if update_data.notes:
                session.notes = update_data.notes
            if update_data.mood_rating:
                session.mood_rating = update_data.mood_rating
            if update_data.difficulty_rating:
                session.difficulty_rating = update_data.difficulty_rating

            db.commit()
            db.refresh(session)
            return session
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error completing workout session")

    # @staticmethod
    # def record_exercise_set(
    #     db: Session,
    #     session_id: str,
    #     set_data: ExerciseSetCreate,
    #     user: User
    # ) -> ExerciseSet:
    #     """Record an exercise set in a workout session"""
    #     # Verify session exists and is active
    #     session = db.query(WorkoutSession).filter(
    #         WorkoutSession.id == session_id,
    #         WorkoutSession.user_id == user.id,
    #         WorkoutSession.status == WorkoutStatus.IN_PROGRESS
    #     ).first()

    #     if not session:
    #         raise HTTPException(
    #             status_code=404,
    #             detail="Active workout session not found"
    #         )

    #     # Verify workout exercise exists and belongs to the session's workout
    #     workout_exercise = db.query(WorkoutExercise).filter(
    #         WorkoutExercise.id == set_data.workout_exercise_id,
    #         WorkoutExercise.workout_id == session.workout_id
    #     ).first()

    #     if not workout_exercise:
    #         raise HTTPException(
    #             status_code=404,
    #             detail="Workout exercise not found in current workout"
    #         )

    #     try:
    #         db_set = ExerciseSet(
    #             **set_data.dict(),
    #             workout_session_id=session_id
    #         )
    #         db.add(db_set)
    #         db.commit()
    #         db.refresh(db_set)
    #         return db_set
    #     except IntegrityError:
    #         db.rollback()
    #         raise HTTPException(status_code=400, detail="Error recording exercise set")
