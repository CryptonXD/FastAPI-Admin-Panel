from typing import Optional

from pydantic import BaseModel, field_validator


# Shared properties
class RatingBase(BaseModel):
    stars: Optional[int] = None


# Properties to receive on rating creation
class RatingCreate(RatingBase):
    stars: int
    lesson_id: int
    
    @field_validator("stars")
    def stars_must_be_in_range(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Stars must be between 1 and 5")
        return v


# Properties to receive on rating update
class RatingUpdate(RatingBase):
    @field_validator("stars")
    def stars_must_be_in_range(cls, v):
        if v and (v < 1 or v > 5):
            raise ValueError("Stars must be between 1 and 5")
        return v


class RatingInDBBase(RatingBase):
    id: int
    user_id: int
    lesson_id: int
    stars: int

    model_config = {"from_attributes": True}


# Additional properties to return via API
class Rating(RatingInDBBase):
    pass
