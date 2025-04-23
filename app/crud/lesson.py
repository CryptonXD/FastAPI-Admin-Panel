from typing import List, Optional, Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.lesson import Lesson
from app.models.rating import Rating
from app.schemas.lesson import LessonCreate, LessonUpdate


class CRUDLesson(CRUDBase[Lesson, LessonCreate, LessonUpdate]):
    def create_with_course(
        self, db: Session, *, obj_in: LessonCreate, course_id: int
    ) -> Lesson:
        # Извлекаем данные из obj_in, исключая course_id, если он есть в схеме
        obj_in_data = obj_in.dict(exclude={"course_id"}) if hasattr(obj_in, "course_id") else obj_in.dict()
        
        # Создаем объект с course_id из параметра функции
        db_obj = Lesson(**obj_in_data, course_id=course_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_course(
        self, db: Session, *, course_id: int, skip: int = 0, limit: int = 100
    ) -> List[Lesson]:
        return (
            db.query(self.model)
            .filter(Lesson.course_id == course_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_with_comments_and_ratings(
        self, db: Session, *, id: int
    ) -> Optional[Dict[str, Any]]:
        lesson = (
            db.query(self.model)
            .filter(Lesson.id == id)
            .options(joinedload(Lesson.comments), joinedload(Lesson.ratings))
            .first()
        )
        
        if lesson:
            # Calculate average rating
            avg_rating = db.query(func.avg(Rating.stars)).filter(Rating.lesson_id == id).scalar() or 0
            
            return {
                "lesson": lesson,
                "average_rating": float(avg_rating)
            }
        return None


lesson = CRUDLesson(Lesson)
