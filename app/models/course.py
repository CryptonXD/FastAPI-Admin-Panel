from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Course(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    author_id = Column(Integer, ForeignKey("user.id"))
    
    # Relationships
    author = relationship("User", back_populates="courses")
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    enrolled_users = relationship("Enrollment", back_populates="course")
