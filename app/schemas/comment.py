from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class CommentBase(BaseModel):
    text: Optional[str] = None


# Properties to receive on comment creation
class CommentCreate(CommentBase):
    text: str
    lesson_id: int


# Properties to receive on comment update
class CommentUpdate(CommentBase):
    pass


class CommentInDBBase(CommentBase):
    id: int
    user_id: int
    lesson_id: int
    created_at: datetime
    text: str

    model_config = {"from_attributes": True}


# Additional properties to return via API
class Comment(CommentInDBBase):
    pass
