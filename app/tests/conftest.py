import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Generator

# Добавляем корневую директорию проекта в sys.path для корректных импортов
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from main import app  # Импортируем из корня проекта
from fastapi.testclient import TestClient


# Создаем тестовую базу данных
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Фикстура для тестового пользователя
@pytest.fixture(scope="function")
def test_user(db) -> User:
    # Создаем тестового пользователя в БД
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # пароль: test
        is_active=True,
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Функция для создания тестового токена
def get_test_token(user: User) -> str:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )


@pytest.fixture(scope="function")
def db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    # Create a session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after the test is done
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db, test_user):
    # Переопределяем зависимость, чтобы использовать тестовую базу данных
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    # Создаем тестовый токен
    token = get_test_token(test_user)
    
    # Переопределяем зависимости
    app.dependency_overrides[get_db] = override_get_db
    
    # Создаем клиент с заголовком авторизации
    with TestClient(app) as c:
        c.headers = {
            "Authorization": f"Bearer {token}"
        }
        yield c
        
    # Сбрасываем переопределения зависимостей
    app.dependency_overrides = {}
