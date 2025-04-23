from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.db import base  # noqa: F401

# Make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly


def init_db(db: Session) -> None:
    # Create admin user if it doesn't exist
    user = crud.user.get_by_email(db, email="admin@example.com")
    if not user:
        user_in = schemas.UserCreate(
            email="admin@example.com",
            password="adminpassword",
            full_name="Admin User",
            is_admin=True,
        )
        user = crud.user.create(db, obj_in=user_in)
        
    # Create a test user if it doesn't exist
    test_user = crud.user.get_by_email(db, email="test@example.com")
    if not test_user:
        user_in = schemas.UserCreate(
            email="test@example.com",
            password="testpassword",
            full_name="Test User",
            is_admin=False,
        )
        test_user = crud.user.create(db, obj_in=user_in)
        
    # Create a sample course if it doesn't exist
    course = crud.course.get_by_title(db, title="Introduction to Python")
    if not course:
        course_in = schemas.CourseCreate(
            title="Introduction to Python",
            description="Learn the basics of Python programming language",
        )
        course = crud.course.create_with_author(db=db, obj_in=course_in, author_id=user.id)
        
        # Create some lessons for the course
        lesson1_in = schemas.LessonCreate(
            title="Python Basics",
            video_url="https://example.com/video1.mp4",
            content="This lesson covers Python basics including variables, data types, and operators.",
            course_id=course.id,
        )
        lesson1 = crud.lesson.create_with_course(db=db, obj_in=lesson1_in, course_id=course.id)
        
        lesson2_in = schemas.LessonCreate(
            title="Control Flow",
            video_url="https://example.com/video2.mp4",
            content="This lesson covers control flow statements like if-else, for loops, and while loops.",
            course_id=course.id,
        )
        lesson2 = crud.lesson.create_with_course(db=db, obj_in=lesson2_in, course_id=course.id)
        
        # Enroll test user in the course
        enrollment_in = schemas.EnrollmentCreate(course_id=course.id)
        crud.enrollment.create_with_owner(db=db, obj_in=enrollment_in, user_id=test_user.id)
        
        # Add a comment from the test user
        comment_in = schemas.CommentCreate(
            text="Great lesson! Really clear explanations.",
            lesson_id=lesson1.id,
        )
        crud.comment.create_with_owner(db=db, obj_in=comment_in, user_id=test_user.id)
        
        # Add a rating from the test user
        rating_in = schemas.RatingCreate(
            stars=5,
            lesson_id=lesson1.id,
        )
        crud.rating.create_with_owner(db=db, obj_in=rating_in, user_id=test_user.id)
