# Import base class for SQLAlchemy models
from app.db.base_class import Base  # noqa

# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User  # noqa
from app.models.course import Course  # noqa
from app.models.lesson import Lesson  # noqa
from app.models.comment import Comment  # noqa
from app.models.rating import Rating  # noqa
from app.models.enrollment import Enrollment  # noqa
