from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
def get_general_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get general statistics (users, courses, lessons).
    Only accessible by admins.
    """
    # Count total users, courses, lessons
    total_users = db.query(func.count(models.User.id)).scalar()
    total_courses = db.query(func.count(models.Course.id)).scalar()
    total_lessons = db.query(func.count(models.Lesson.id)).scalar()
    total_comments = db.query(func.count(models.Comment.id)).scalar()
    total_ratings = db.query(func.count(models.Rating.id)).scalar()
    
    # Get average rating across all lessons
    avg_rating = db.query(func.avg(models.Rating.stars)).scalar() or 0
    
    return {
        "total_users": total_users,
        "total_courses": total_courses,
        "total_lessons": total_lessons,
        "total_comments": total_comments,
        "total_ratings": total_ratings,
        "average_rating": float(avg_rating)
    }


@router.get("/popular-courses", response_model=List[Dict[str, Any]])
def get_popular_courses(
    db: Session = Depends(deps.get_db),
    limit: int = 5,
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get most popular courses based on enrollment count.
    Only accessible by admins.
    """
    popular_courses = (
        db.query(
            models.Course.id,
            models.Course.title,
            func.count(models.Enrollment.id).label("enrollment_count")
        )
        .join(models.Enrollment, models.Enrollment.course_id == models.Course.id)
        .group_by(models.Course.id)
        .order_by(func.count(models.Enrollment.id).desc())
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": course.id,
            "title": course.title,
            "enrollment_count": course.enrollment_count
        }
        for course in popular_courses
    ]


@router.get("/popular-lessons", response_model=List[Dict[str, Any]])
def get_popular_lessons(
    db: Session = Depends(deps.get_db),
    limit: int = 5,
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get most popular lessons based on comment and rating count.
    Only accessible by admins.
    """
    popular_lessons = (
        db.query(
            models.Lesson.id,
            models.Lesson.title,
            func.count(models.Comment.id).label("comment_count"),
            func.count(models.Rating.id).label("rating_count"),
            func.avg(models.Rating.stars).label("avg_rating")
        )
        .outerjoin(models.Comment, models.Comment.lesson_id == models.Lesson.id)
        .outerjoin(models.Rating, models.Rating.lesson_id == models.Lesson.id)
        .group_by(models.Lesson.id)
        .order_by((func.count(models.Comment.id) + func.count(models.Rating.id)).desc())
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": lesson.id,
            "title": lesson.title,
            "comment_count": lesson.comment_count,
            "rating_count": lesson.rating_count,
            "avg_rating": float(lesson.avg_rating) if lesson.avg_rating else 0
        }
        for lesson in popular_lessons
    ]


@router.get("/active-users", response_model=List[Dict[str, Any]])
def get_active_users(
    db: Session = Depends(deps.get_db),
    limit: int = 5,
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get most active users based on enrollments, comments, and ratings.
    Only accessible by admins.
    """
    active_users = (
        db.query(
            models.User.id,
            models.User.full_name,
            models.User.email,
            func.count(models.Enrollment.id).label("enrollment_count"),
            func.count(models.Comment.id).label("comment_count"),
            func.count(models.Rating.id).label("rating_count")
        )
        .outerjoin(models.Enrollment, models.Enrollment.user_id == models.User.id)
        .outerjoin(models.Comment, models.Comment.user_id == models.User.id)
        .outerjoin(models.Rating, models.Rating.user_id == models.User.id)
        .group_by(models.User.id)
        .order_by(
            (
                func.count(models.Enrollment.id) + 
                func.count(models.Comment.id) + 
                func.count(models.Rating.id)
            ).desc()
        )
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "enrollment_count": user.enrollment_count,
            "comment_count": user.comment_count,
            "rating_count": user.rating_count,
            "activity_score": user.enrollment_count + user.comment_count + user.rating_count
        }
        for user in active_users
    ]
