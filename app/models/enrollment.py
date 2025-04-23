from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Enrollment(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    course_id = Column(Integer, ForeignKey("course.id"))
    enrolled_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrolled_users")
