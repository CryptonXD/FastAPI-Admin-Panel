from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.db.session import engine
from sqlalchemy import text, inspect

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
def admin_overview(
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Admin dashboard overview endpoint.
    Only accessible to admin users.
    """
    return {
        "message": "Admin Dashboard API",
        "endpoints": {
            "users": "/admin/users",
            "courses": "/admin/courses",
            "lessons": "/admin/lessons",
            "enrollments": "/admin/enrollments",
            "comments": "/admin/comments",
            "ratings": "/admin/ratings",
            "db_schema": "/admin/db-schema",
        }
    }


@router.get("/users", response_model=List[schemas.User])
def admin_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get all users.
    Only accessible to admin users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/courses", response_model=List[schemas.CourseWithLessons])
def admin_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get all courses with lessons.
    Only accessible to admin users.
    """
    courses = crud.course.get_multi(db, skip=skip, limit=limit)
    result = []
    for course in courses:
        lessons = crud.lesson.get_multi_by_course(
            db=db, course_id=course.id, skip=0, limit=100
        )
        course_with_lessons = schemas.CourseWithLessons(
            **course.__dict__,
            lessons=lessons
        )
        result.append(course_with_lessons)
    return result


@router.get("/lessons", response_model=List[schemas.LessonWithDetails])
def admin_lessons(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get all lessons with comments.
    Only accessible to admin users.
    """
    lessons = crud.lesson.get_multi(db, skip=skip, limit=limit)
    result = []
    for lesson in lessons:
        comments = crud.comment.get_multi_by_lesson(
            db=db, lesson_id=lesson.id, skip=0, limit=100
        )
        ratings = crud.rating.get_multi_by_lesson(
            db=db, lesson_id=lesson.id, skip=0, limit=100
        )
        lesson_with_data = schemas.LessonWithDetails(
            **lesson.__dict__,
            comments=comments,
            ratings=ratings
        )
        result.append(lesson_with_data)
    return result


@router.get("/enrollments", response_model=List[schemas.Enrollment])
def admin_enrollments(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get all enrollments.
    Only accessible to admin users.
    """
    enrollments = crud.enrollment.get_multi(db, skip=skip, limit=limit)
    return enrollments


@router.get("/comments", response_model=List[schemas.Comment])
def admin_comments(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get all comments.
    Only accessible to admin users.
    """
    comments = crud.comment.get_multi(db, skip=skip, limit=limit)
    return comments


@router.get("/ratings", response_model=List[schemas.Rating])
def admin_ratings(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get all ratings.
    Only accessible to admin users.
    """
    ratings = crud.rating.get_multi(db, skip=skip, limit=limit)
    return ratings


@router.get("/db-schema", response_model=Dict[str, Any])
def db_schema(
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get database schema information.
    Only accessible to admin users.
    """
    inspector = inspect(engine)
    schema_info = {}
    
    # Get all tables
    tables = inspector.get_table_names()
    for table_name in tables:
        columns = []
        for column in inspector.get_columns(table_name):
            columns.append({
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column.get("nullable", True),
                "default": str(column.get("default", "None")),
            })
        
        # Get primary keys
        primary_keys = inspector.get_primary_keys(table_name)
        
        # Get foreign keys
        foreign_keys = []
        for fk in inspector.get_foreign_keys(table_name):
            foreign_keys.append({
                "referred_table": fk["referred_table"],
                "referred_columns": fk["referred_columns"],
                "constrained_columns": fk["constrained_columns"],
            })
        
        # Add table info to schema
        schema_info[table_name] = {
            "columns": columns,
            "primary_key": primary_keys,
            "foreign_keys": foreign_keys,
        }
    
    return {"tables": schema_info}
