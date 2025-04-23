from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Rating(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    lesson_id = Column(Integer, ForeignKey("lesson.id"))
    stars = Column(Integer)
    
    # Ensure stars are between 1 and 5
    __table_args__ = (
        CheckConstraint('stars >= 1 AND stars <= 5', name='check_stars_range'),
    )
    
    # Relationships
    user = relationship("User", back_populates="ratings")
    lesson = relationship("Lesson", back_populates="ratings")
