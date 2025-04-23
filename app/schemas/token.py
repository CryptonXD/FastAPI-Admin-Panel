from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    bearer_format: Optional[str] = None
    user_id: Optional[int] = None
    is_admin: Optional[bool] = None


class TokenPayload(BaseModel):
    sub: Optional[int] = None
