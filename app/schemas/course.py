from typing import List, Optional, Any

from pydantic import BaseModel, Field


# Shared properties
class CourseBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


# Properties to receive on course creation
class CourseCreate(CourseBase):
    title: str


# Properties to receive on course update
class CourseUpdate(CourseBase):
    pass


class CourseInDBBase(CourseBase):
    id: int
    author_id: int
    title: str

    model_config = {"from_attributes": True}


# Additional properties to return via API
class Course(CourseInDBBase):
    pass


# Course with lessons
class CourseWithLessons(Course):
    lessons: List[Any] = Field(default_factory=list)
