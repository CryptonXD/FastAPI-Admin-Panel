from typing import List, Optional, Any

from pydantic import BaseModel, Field


# Shared properties
class LessonBase(BaseModel):
    title: Optional[str] = None
    video_url: Optional[str] = None
    content: Optional[str] = None


# Properties to receive on lesson creation
class LessonCreate(LessonBase):
    title: str
    course_id: int


# Properties to receive on lesson update
class LessonUpdate(LessonBase):
    pass


class LessonInDBBase(LessonBase):
    id: int
    course_id: int
    title: str

    model_config = {"from_attributes": True}


# Additional properties to return via API
class Lesson(LessonInDBBase):
    pass


# Lesson with comments and ratings
class LessonWithDetails(Lesson):
    comments: List[Any] = Field(default_factory=list) 
    ratings: List[Any] = Field(default_factory=list)
    average_rating: Optional[float] = None
