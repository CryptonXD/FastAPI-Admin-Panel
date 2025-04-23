from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Relationships
    courses = relationship("Course", back_populates="author")
    enrollments = relationship("Enrollment", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    ratings = relationship("Rating", back_populates="user")
