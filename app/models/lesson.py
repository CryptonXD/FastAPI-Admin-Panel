from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Lesson(Base):
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.id"))
    title = Column(String, index=True)
    video_url = Column(String)
    content = Column(Text)
    
    # Relationships
    course = relationship("Course", back_populates="lessons")
    comments = relationship("Comment", back_populates="lesson", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="lesson", cascade="all, delete-orphan")
