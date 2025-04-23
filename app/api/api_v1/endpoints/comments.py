from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Comment])
def read_comments(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve comments.
    """
    if crud.user.is_admin(current_user):
        comments = crud.comment.get_multi(db, skip=skip, limit=limit)
    else:
        comments = crud.comment.get_multi_by_owner(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
    return comments


@router.post("/", response_model=schemas.Comment)
def create_comment(
    *,
    db: Session = Depends(deps.get_db),
    comment_in: schemas.CommentCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new comment.
    """
    # Check if lesson exists
    lesson = crud.lesson.get(db=db, id=comment_in.lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check if user is enrolled in the course that contains this lesson
    course = crud.course.get(db=db, id=lesson.course_id)
    enrollment = crud.enrollment.get_by_user_and_course(
        db=db, user_id=current_user.id, course_id=course.id
    )
    
    # Only allow enrolled users, course author, or admin to comment
    if not (enrollment or course.author_id == current_user.id or current_user.is_admin):
        raise HTTPException(status_code=403, 
                           detail="You must be enrolled in this course to comment on lessons")
    
    comment = crud.comment.create_with_owner(
        db=db, obj_in=comment_in, user_id=current_user.id
    )
    return comment


@router.get("/by-lesson/{lesson_id}", response_model=List[schemas.Comment])
def read_comments_by_lesson(
    *,
    db: Session = Depends(deps.get_db),
    lesson_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get comments for a specific lesson.
    """
    # Check if lesson exists
    lesson = crud.lesson.get(db=db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check if user is enrolled in the course that contains this lesson
    course = crud.course.get(db=db, id=lesson.course_id)
    enrollment = crud.enrollment.get_by_user_and_course(
        db=db, user_id=current_user.id, course_id=course.id
    )
    
    # Only allow enrolled users, course author, or admin to view comments
    if not (enrollment or course.author_id == current_user.id or current_user.is_admin):
        raise HTTPException(status_code=403, 
                           detail="You must be enrolled in this course to view comments")
    
    comments = crud.comment.get_multi_by_lesson(
        db=db, lesson_id=lesson_id, skip=skip, limit=limit
    )
    return comments


@router.delete("/{id}", response_model=schemas.Comment)
def delete_comment(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a comment.
    """
    comment = crud.comment.get(db=db, id=id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Only allow comment owner or admin to delete
    if comment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    comment = crud.comment.remove(db=db, id=id)
    return comment
