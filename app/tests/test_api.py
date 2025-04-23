import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path для корректных импортов
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from fastapi.testclient import TestClient

from main import app
from app.core.config import settings
from app.api.deps import get_current_active_user, get_db
from app.models.user import User

# Test data
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword",
    "full_name": "Test User"
}

TEST_COURSE = {
    "title": "Test Course",
    "description": "This is a test course"
}

TEST_LESSON = {
    "title": "Test Lesson",
    "video_url": "https://example.com/test-video.mp4",
    "content": "This is test content for the lesson"
}


# Настройка мок-пользователя для тестов
@pytest.fixture
def test_user():
    return User(
        id=1,
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        is_admin=False
    )


class TestUserAPI:
    def test_create_user(self, client, db):
        response = client.post(
            f"{settings.API_V1_STR}/users/",
            json=TEST_USER,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_USER["email"]
        assert data["full_name"] == TEST_USER["full_name"]
        assert "id" in data
        assert "password" not in data


class TestCourseAPI:
    def test_create_course(self, client, db, test_user, monkeypatch):
        # Переопределяем зависимость для получения текущего пользователя
        monkeypatch.setattr("app.api.deps.get_current_active_user", lambda: test_user)
        
        response = client.post(
            f"{settings.API_V1_STR}/courses/",
            json=TEST_COURSE,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == TEST_COURSE["title"]
        assert data["description"] == TEST_COURSE["description"]
        assert "id" in data

    def test_get_courses(self, client, db):
        response = client.get(f"{settings.API_V1_STR}/courses/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestLessonAPI:
    def test_create_lesson(self, client, db, test_user, monkeypatch):
        # Переопределяем зависимость для получения текущего пользователя
        monkeypatch.setattr("app.api.deps.get_current_active_user", lambda: test_user)
        
        # Сначала создаем курс, с которым будет связан урок
        course_response = client.post(
            f"{settings.API_V1_STR}/courses/",
            json=TEST_COURSE,
        )
        course_id = course_response.json()["id"]
        
        # Теперь создаем урок
        lesson_data = {**TEST_LESSON, "course_id": course_id}
        response = client.post(
            f"{settings.API_V1_STR}/lessons/",
            json=lesson_data,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == TEST_LESSON["title"]
        assert data["video_url"] == TEST_LESSON["video_url"]
        assert data["content"] == TEST_LESSON["content"]
        assert data["course_id"] == course_id
        assert "id" in data
