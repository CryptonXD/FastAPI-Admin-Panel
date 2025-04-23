from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Lesson])
def read_lessons(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve lessons.
    """
    lessons = crud.lesson.get_multi(db, skip=skip, limit=limit)
    return lessons


@router.post("/", response_model=schemas.Lesson)
def create_lesson(
    *,
    db: Session = Depends(deps.get_db),
    lesson_in: schemas.LessonCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new lesson.
    """
    # Check if user is course author or admin
    course = crud.course.get(db=db, id=lesson_in.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    lesson = crud.lesson.create_with_course(
        db=db, obj_in=lesson_in, course_id=lesson_in.course_id
    )
    return lesson


@router.get("/{id}", response_model=schemas.LessonWithDetails)
def read_lesson(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get lesson by ID.
    """
    lesson_with_details = crud.lesson.get_with_comments_and_ratings(db=db, id=id)
    if not lesson_with_details:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check if user is enrolled in the course
    course_id = lesson_with_details["lesson"].course_id
    enrollment = crud.enrollment.get_by_user_and_course(
        db=db, user_id=current_user.id, course_id=course_id
    )
    course = crud.course.get(db=db, id=course_id)
    
    # Allow access if user is course author, admin, or enrolled
    if not (enrollment or course.author_id == current_user.id or current_user.is_admin):
        raise HTTPException(status_code=403, detail="You must be enrolled in this course to view lessons")
    
    return lesson_with_details


@router.put("/{id}", response_model=schemas.Lesson)
def update_lesson(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    lesson_in: schemas.LessonUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a lesson.
    """
    lesson = crud.lesson.get(db=db, id=id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    course = crud.course.get(db=db, id=lesson.course_id)
    if course.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    lesson = crud.lesson.update(db=db, db_obj=lesson, obj_in=lesson_in)
    return lesson


@router.delete("/{id}", response_model=schemas.Lesson)
def delete_lesson(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a lesson.
    """
    lesson = crud.lesson.get(db=db, id=id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    course = crud.course.get(db=db, id=lesson.course_id)
    if course.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    lesson = crud.lesson.remove(db=db, id=id)
    return lesson
