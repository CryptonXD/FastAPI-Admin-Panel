from typing import List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate


class CRUDComment(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: CommentCreate, user_id: int
    ) -> Comment:
        obj_in_data = obj_in.dict()
        db_obj = Comment(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        return (
            db.query(self.model)
            .filter(Comment.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
    def get_multi_by_lesson(
        self, db: Session, *, lesson_id: int, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        return (
            db.query(self.model)
            .filter(Comment.lesson_id == lesson_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


comment = CRUDComment(Comment)
