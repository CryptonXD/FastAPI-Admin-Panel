from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Course])
def read_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    title: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve courses with optional title filter.
    """
    if title:
        # Filter courses by title
        courses = db.query(models.Course).filter(
            models.Course.title.ilike(f"%{title}%")
        ).offset(skip).limit(limit).all()
    else:
        courses = crud.course.get_multi(db, skip=skip, limit=limit)
    return courses


@router.post("/", response_model=schemas.Course)
def create_course(
    *,
    db: Session = Depends(deps.get_db),
    course_in: schemas.CourseCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new course.
    """
    course = crud.course.create_with_author(db=db, obj_in=course_in, author_id=current_user.id)
    return course


@router.get("/{id}", response_model=schemas.CourseWithLessons)
def read_course(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get course by ID.
    """
    course = crud.course.get_with_lessons(db=db, id=id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.put("/{id}", response_model=schemas.Course)
def update_course(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    course_in: schemas.CourseUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a course.
    """
    course = crud.course.get(db=db, id=id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    course = crud.course.update(db=db, db_obj=course, obj_in=course_in)
    return course


@router.delete("/{id}", response_model=schemas.Course)
def delete_course(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a course.
    """
    course = crud.course.get(db=db, id=id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    course = crud.course.remove(db=db, id=id)
    return course


@router.get("/by-author/me", response_model=List[schemas.Course])
def read_courses_by_current_user(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get courses created by current user.
    """
    courses = crud.course.get_multi_by_author(
        db=db, author_id=current_user.id, skip=skip, limit=limit
    )
    return courses


@router.post("/{id}/enroll", response_model=schemas.Enrollment)
def enroll_in_course(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Enroll current user in course.
    """
    course = crud.course.get(db=db, id=id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    enrollment_in = schemas.EnrollmentCreate(course_id=id)
    enrollment = crud.enrollment.create_with_owner(
        db=db, obj_in=enrollment_in, user_id=current_user.id
    )
    return enrollment
