from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate


class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    def create_with_author(
        self, db: Session, *, obj_in: CourseCreate, author_id: int
    ) -> Course:
        obj_in_data = obj_in.dict()
        db_obj = Course(**obj_in_data, author_id=author_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_author(
        self, db: Session, *, author_id: int, skip: int = 0, limit: int = 100
    ) -> List[Course]:
        return (
            db.query(self.model)
            .filter(Course.author_id == author_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
    def get_by_title(
        self, db: Session, *, title: str
    ) -> Optional[Course]:
        return db.query(self.model).filter(Course.title == title).first()
        
    def get_with_lessons(
        self, db: Session, *, id: int
    ) -> Optional[Course]:
        return (
            db.query(self.model)
            .filter(Course.id == id)
            .options(joinedload(Course.lessons))
            .first()
        )


course = CRUDCourse(Course)
