from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr, BaseModel
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


# Simple login schema without extra OAuth2 fields
class LoginForm(BaseModel):
    username: str
    password: str


@router.post("/token", response_model=schemas.Token)
def get_token(
    form_data: LoginForm,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Получить токен без дополнительных полей
    """
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(user.id, expires_delta=access_token_expires)
    return {
        "access_token": token,
        "token_type": "bearer",
        "bearer_format": f"Bearer {token}",
        "user_id": user.id,
        "is_admin": user.is_admin,
    }


@router.post("/login/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/register", response_model=schemas.User)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    full_name: str = Body(...),
    email: EmailStr = Body(...),
    password: str = Body(...),
) -> Any:
    """
    Register new user
    """
    user = crud.user.get_by_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user_in = schemas.UserCreate(
        full_name=full_name,
        email=email,
        password=password,
    )
    user = crud.user.create(db, obj_in=user_in)
    
    return user
