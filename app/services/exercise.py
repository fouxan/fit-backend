from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.exercise import Exercise, MuscleGroup, Equipment, ExerciseCategory
from app.models.user import User
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate
from app.services.plan_limits import PlanLimitService
from sqlalchemy.exc import IntegrityError

class ExerciseService:
    @staticmethod
    def create_exercise(
        db: Session,
        exercise: ExerciseCreate,
        user: User,
        is_custom: bool = True
    ) -> Exercise:
        """Create a new exercise"""
        if is_custom and not PlanLimitService.check_custom_exercise_permission(db, user):
            raise HTTPException(
                status_code=402,
                detail="Your current plan does not allow creating custom exercises. Please upgrade to create custom exercises."
            )

        # Verify category exists
        category = db.query(ExerciseCategory).filter(
            ExerciseCategory.id == exercise.category_id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Exercise category not found")

        # Verify muscle groups exist
        muscle_groups = db.query(MuscleGroup).filter(
            MuscleGroup.id.in_(exercise.muscle_group_ids)
        ).all()
        if len(muscle_groups) != len(exercise.muscle_group_ids):
            raise HTTPException(status_code=404, detail="One or more muscle groups not found")

        # Verify equipment exists
        equipment = db.query(Equipment).filter(
            Equipment.id.in_(exercise.equipment_ids)
        ).all()
        if len(equipment) != len(exercise.equipment_ids):
            raise HTTPException(status_code=404, detail="One or more equipment items not found")

        try:
            db_exercise = Exercise(
                **exercise.dict(exclude={'muscle_group_ids', 'equipment_ids'}),
                is_custom=is_custom,
                created_by_id=user.id if is_custom else None,
                muscle_groups=muscle_groups,
                equipment=equipment
            )
            db.add(db_exercise)
            db.commit()
            db.refresh(db_exercise)
            return db_exercise
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Exercise with this name already exists")

    @staticmethod
    def get_exercise(db: Session, exercise_id: str) -> Exercise:
        """Get exercise by ID"""
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")
        return exercise

    @staticmethod
    def update_exercise(
        db: Session,
        exercise_id: str,
        exercise_update: ExerciseUpdate,
        user: User
    ) -> Exercise:
        """Update an exercise"""
        db_exercise = ExerciseService.get_exercise(db, exercise_id)
        
        # Check if user has permission to update
        if db_exercise.is_custom and db_exercise.created_by_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this exercise")
        
        # If it's a system exercise, only admins can update
        if not db_exercise.is_custom and not user.is_superuser:
            raise HTTPException(status_code=403, detail="Not authorized to update system exercises")

        update_data = exercise_update.dict(exclude_unset=True)
        
        # Handle relationships if provided
        if 'muscle_group_ids' in update_data:
            muscle_groups = db.query(MuscleGroup).filter(
                MuscleGroup.id.in_(update_data['muscle_group_ids'])
            ).all()
            if len(muscle_groups) != len(update_data['muscle_group_ids']):
                raise HTTPException(status_code=404, detail="One or more muscle groups not found")
            db_exercise.muscle_groups = muscle_groups
            del update_data['muscle_group_ids']

        if 'equipment_ids' in update_data:
            equipment = db.query(Equipment).filter(
                Equipment.id.in_(update_data['equipment_ids'])
            ).all()
            if len(equipment) != len(update_data['equipment_ids']):
                raise HTTPException(status_code=404, detail="One or more equipment items not found")
            db_exercise.equipment = equipment
            del update_data['equipment_ids']

        # Update other fields
        for field, value in update_data.items():
            setattr(db_exercise, field, value)

        try:
            db.commit()
            db.refresh(db_exercise)
            return db_exercise
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Exercise with this name already exists")

    @staticmethod
    def delete_exercise(db: Session, exercise_id: str, user: User) -> None:
        """Delete an exercise"""
        exercise = ExerciseService.get_exercise(db, exercise_id)
        
        # Check if user has permission to delete
        if exercise.is_custom and exercise.created_by_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this exercise")
        
        # If it's a system exercise, only admins can delete
        if not exercise.is_custom and not user.is_superuser:
            raise HTTPException(status_code=403, detail="Not authorized to delete system exercises")

        db.delete(exercise)
        db.commit()

    @staticmethod
    def list_exercises(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[str] = None,
        difficulty: Optional[str] = None,
        equipment_id: Optional[str] = None,
        muscle_group_id: Optional[str] = None,
        include_custom: bool = True
    ) -> List[Exercise]:
        """List exercises with optional filters"""
        query = db.query(Exercise)

        if category_id:
            query = query.filter(Exercise.category_id == category_id)
        
        if difficulty:
            query = query.filter(Exercise.difficulty == difficulty)
        
        if equipment_id:
            query = query.join(Exercise.equipment).filter(Equipment.id == equipment_id)
        
        if muscle_group_id:
            query = query.join(Exercise.muscle_groups).filter(MuscleGroup.id == muscle_group_id)
        
        if not include_custom:
            query = query.filter(Exercise.is_custom == False)

        return query.offset(skip).limit(limit).all()
