from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Enrollment])
def read_enrollments(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve enrollments for current user.
    """
    if crud.user.is_admin(current_user):
        enrollments = crud.enrollment.get_multi(db, skip=skip, limit=limit)
    else:
        enrollments = crud.enrollment.get_multi_by_user(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
    return enrollments


@router.get("/by-course/{course_id}", response_model=List[schemas.User])
def get_enrolled_users(
    course_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all users enrolled in a specific course.
    Only course author or admin can access this endpoint.
    """
    course = crud.course.get(db=db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if current user is course author or admin
    if course.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get all enrollments for the course
    enrollments = crud.enrollment.get_multi_by_course(
        db=db, course_id=course_id, skip=skip, limit=limit
    )
    
    # Get users from enrollments
    users = [db.query(models.User).get(enrollment.user_id) for enrollment in enrollments]
    return users


@router.post("/", response_model=schemas.Enrollment)
def create_enrollment(
    *,
    db: Session = Depends(deps.get_db),
    enrollment_in: schemas.EnrollmentCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new enrollment.
    """
    # Check if course exists
    course = crud.course.get(db=db, id=enrollment_in.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if user is already enrolled
    existing_enrollment = crud.enrollment.get_by_user_and_course(
        db=db, user_id=current_user.id, course_id=enrollment_in.course_id
    )
    if existing_enrollment:
        return existing_enrollment
    
    enrollment = crud.enrollment.create_with_owner(
        db=db, obj_in=enrollment_in, user_id=current_user.id
    )
    return enrollment


@router.delete("/{id}", response_model=schemas.Enrollment)
def delete_enrollment(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an enrollment.
    """
    enrollment = crud.enrollment.get(db=db, id=id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Only allow enrollment owner or admin to delete
    if enrollment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    enrollment = crud.enrollment.remove(db=db, id=id)
    return enrollment
