from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.enrollment import Enrollment
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate


class CRUDEnrollment(CRUDBase[Enrollment, EnrollmentCreate, EnrollmentUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: EnrollmentCreate, user_id: int
    ) -> Enrollment:
        # Check if user is already enrolled in this course
        existing_enrollment = (
            db.query(self.model)
            .filter(Enrollment.user_id == user_id, Enrollment.course_id == obj_in.course_id)
            .first()
        )
        
        if existing_enrollment:
            return existing_enrollment
        
        # Create new enrollment
        obj_in_data = obj_in.dict()
        db_obj = Enrollment(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user_and_course(
        self, db: Session, *, user_id: int, course_id: int
    ) -> Optional[Enrollment]:
        return (
            db.query(self.model)
            .filter(Enrollment.user_id == user_id, Enrollment.course_id == course_id)
            .first()
        )
    
    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Enrollment]:
        return (
            db.query(self.model)
            .filter(Enrollment.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_multi_by_course(
        self, db: Session, *, course_id: int, skip: int = 0, limit: int = 100
    ) -> List[Enrollment]:
        return (
            db.query(self.model)
            .filter(Enrollment.course_id == course_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


enrollment = CRUDEnrollment(Enrollment)
