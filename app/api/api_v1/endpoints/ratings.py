from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.post("/", response_model=schemas.Rating)
def create_rating(
    *,
    db: Session = Depends(deps.get_db),
    rating_in: schemas.RatingCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create or update a rating for a lesson.
    """
    # Check if lesson exists
    lesson = crud.lesson.get(db=db, id=rating_in.lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check if user is enrolled in the course that contains this lesson
    course = crud.course.get(db=db, id=lesson.course_id)
    enrollment = crud.enrollment.get_by_user_and_course(
        db=db, user_id=current_user.id, course_id=course.id
    )
    
    # Only allow enrolled users to rate
    if not enrollment and not current_user.is_admin:
        raise HTTPException(status_code=403, 
                           detail="You must be enrolled in this course to rate lessons")
    
    rating = crud.rating.create_with_owner(
        db=db, obj_in=rating_in, user_id=current_user.id
    )
    return rating


@router.get("/by-lesson/{lesson_id}", response_model=List[schemas.Rating])
def read_ratings_by_lesson(
    *,
    db: Session = Depends(deps.get_db),
    lesson_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get ratings for a specific lesson.
    """
    # Check if lesson exists
    lesson = crud.lesson.get(db=db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    ratings = db.query(models.Rating).filter(models.Rating.lesson_id == lesson_id).all()
    return ratings


@router.get("/average/lesson/{lesson_id}", response_model=float)
def get_average_rating(
    *,
    db: Session = Depends(deps.get_db),
    lesson_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get average rating for a lesson.
    """
    # Check if lesson exists
    lesson = crud.lesson.get(db=db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    average = crud.rating.get_average_for_lesson(db=db, lesson_id=lesson_id)
    return average


@router.delete("/{id}", response_model=schemas.Rating)
def delete_rating(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a rating.
    """
    rating = crud.rating.get(db=db, id=id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    # Only allow rating owner or admin to delete
    if rating.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    rating = crud.rating.remove(db=db, id=id)
    return rating
