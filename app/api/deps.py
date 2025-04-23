from typing import Generator, Optional

from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

# API Key in header (только Bearer Token без дополнительных полей)
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def get_token_from_header(api_key: str = Depends(api_key_header)) -> str:
    """Извлекает токен из заголовка Authorization"""
    if not api_key:
        return ""
        
    if not api_key.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key.replace("Bearer ", "")


async def get_token_from_cookie(access_token: str = Cookie(None)) -> str:
    """Извлекает токен из cookie"""
    if not access_token:
        return ""
        
    # Если токен имеет префикс Bearer, удаляем его
    if access_token.startswith("Bearer "):
        return access_token.replace("Bearer ", "")
    return access_token

# Оставляем оригинальный OAuth2 для обратной совместимости
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Get current user with standard OAuth2 (with extra fields in Swagger UI)
def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(reusable_oauth2), 
    cookie_token: str = Depends(get_token_from_cookie)
) -> models.User:
    # Используем токен из cookie, если токен из OAuth2 не предоставлен
    # OAuth2 может быть None в случае API-запросов из браузера, где токен передается через cookie
    if not token and cookie_token:
        token = cookie_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Get current user with API key header (только Bearer token)
def get_current_user_api_key(
    db: Session = Depends(get_db), 
    header_token: str = Depends(get_token_from_header),
    cookie_token: str = Depends(get_token_from_cookie)
) -> models.User:
    # Используем токен из cookie, если токен из заголовка не предоставлен
    token = header_token if header_token else cookie_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Get current active user with API key header auth
def get_current_active_user_api_key(
    current_user: models.User = Depends(get_current_user_api_key),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user


# Get current active admin with API key auth
def get_current_active_admin_api_key(
    current_user: models.User = Depends(get_current_user_api_key),
) -> models.User:
    if not crud.user.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user
