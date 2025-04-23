from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class EnrollmentBase(BaseModel):
    course_id: Optional[int] = None


# Properties to receive on enrollment creation
class EnrollmentCreate(EnrollmentBase):
    course_id: int


# Properties to receive on enrollment update
class EnrollmentUpdate(EnrollmentBase):
    pass


class EnrollmentInDBBase(EnrollmentBase):
    id: int
    user_id: int
    course_id: int
    enrolled_at: datetime

    model_config = {"from_attributes": True}


# Additional properties to return via API
class Enrollment(EnrollmentInDBBase):
    pass
