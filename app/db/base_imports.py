# Import all the models so that Base has them before being imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.course import Course  # noqa
from app.models.lesson import Lesson  # noqa
from app.models.comment import Comment  # noqa
from app.models.rating import Rating  # noqa
from app.models.enrollment import Enrollment  # noqa
