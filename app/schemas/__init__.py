# Import all schemas
from .token import Token, TokenPayload

# First, import the base models
from .user import User, UserCreate, UserUpdate, UserInDB
from .comment import Comment, CommentCreate, CommentUpdate
from .rating import Rating, RatingCreate, RatingUpdate
from .enrollment import Enrollment, EnrollmentCreate, EnrollmentUpdate

# Then import models that depend on others
from .lesson import Lesson, LessonCreate, LessonUpdate
from .course import Course, CourseCreate, CourseUpdate

# Finally import the compound models
from .lesson import LessonWithDetails
from .course import CourseWithLessons
