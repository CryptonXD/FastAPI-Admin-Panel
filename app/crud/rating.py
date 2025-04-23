from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.rating import Rating
from app.schemas.rating import RatingCreate, RatingUpdate


class CRUDRating(CRUDBase[Rating, RatingCreate, RatingUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: RatingCreate, user_id: int
    ) -> Rating:
        # Check if user already rated this lesson
        existing_rating = (
            db.query(self.model)
            .filter(Rating.user_id == user_id, Rating.lesson_id == obj_in.lesson_id)
            .first()
        )
        
        if existing_rating:
            # Update existing rating
            existing_rating.stars = obj_in.stars
            db.add(existing_rating)
            db.commit()
            db.refresh(existing_rating)
            return existing_rating
        else:
            # Create new rating
            obj_in_data = obj_in.dict()
            db_obj = Rating(**obj_in_data, user_id=user_id)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

    def get_by_user_and_lesson(
        self, db: Session, *, user_id: int, lesson_id: int
    ) -> Optional[Rating]:
        return (
            db.query(self.model)
            .filter(Rating.user_id == user_id, Rating.lesson_id == lesson_id)
            .first()
        )
    
    def get_average_for_lesson(
        self, db: Session, *, lesson_id: int
    ) -> float:
        result = db.query(func.avg(Rating.stars)).filter(Rating.lesson_id == lesson_id).scalar()
        return float(result) if result else 0.0


rating = CRUDRating(Rating)
